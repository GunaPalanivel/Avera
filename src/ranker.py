import heapq
import time
from collections.abc import Iterable

from src.config import (
    FICTIONAL_COMPANIES,
    RERANK_POOL_SIZE,
    SEMANTIC_MIN_HEURISTIC_SCORE,
    SEMANTIC_RERANK_TOPK,
    expand_skill_keyword,
    get_scorer_weights,
    get_title_tiers,
)
from src.detectors.honeypot_detector import is_honeypot
from src.models import CandidateModel
from src.output_writer import EXPECTED_SUBMISSION_ROWS
from src.parsers.jd_parser import JobRequirements
from src.reasoning import generate_reasoning
from src.rerank import CrossEncoderReranker
from src.scorers.behavioral_scorer import BehavioralScorer
from src.scorers.education_scorer import EducationScorer
from src.scorers.experience_scorer import ExperienceScorer
from src.scorers.location_scorer import LocationScorer
from src.scorers.semantic_scorer import SemanticScorer
from src.scorers.skills_scorer import SkillsScorer
from src.scorers.title_career_scorer import TitleCareerScorer
from src.scorers.trajectory_scorer import TrajectoryScorer


class Ranker:
    def __init__(self, job_reqs: JobRequirements):
        self.job_reqs = job_reqs
        weights = get_scorer_weights(job_reqs.seniority_level)
        self.scorers = [
            TitleCareerScorer(
                weight=weights["title_career"],
                title_tiers=get_title_tiers(job_reqs.domain),
                anti_requirements=job_reqs.anti_requirements,
            ),
            SkillsScorer(
                weight=weights["skills"],
                must_have=job_reqs.must_have_skills,
                nice_to_have=job_reqs.nice_to_have_skills,
            ),
            ExperienceScorer(weight=weights["experience"], title_keywords=job_reqs.title_keywords),
            LocationScorer(weight=weights["location"], target_cities=job_reqs.target_cities),
            EducationScorer(weight=weights["education"]),
            TrajectoryScorer(weight=weights["trajectory"]),
            SemanticScorer(weight=weights["semantic"], jd_text=job_reqs.raw_text),
        ]
        self.behavioral_scorer = BehavioralScorer(weight=1.0)
        self.last_input_ids: set[str] = set()
        self.last_pipeline_stats: dict[str, float | int] = {}

    def _semantic_scorer(self) -> SemanticScorer | None:
        for scorer in self.scorers:
            if isinstance(scorer, SemanticScorer):
                return scorer
        return None

    def _heuristic_score(self, candidate: CandidateModel) -> float:
        total = 0.0
        for scorer in self.scorers:
            if isinstance(scorer, SemanticScorer):
                continue
            total += scorer(candidate)
        return total

    def prefill_semantic_stream(self, candidates: Iterable[CandidateModel]) -> int:
        """First pass of the funnel: heuristic candidate generation, then embed the top-K only."""
        semantic_scorer = self._semantic_scorer()
        if semantic_scorer is None:
            return 0

        survivors: list[tuple[float, str, CandidateModel]] = []
        for candidate in candidates:
            if candidate.profile.current_company in FICTIONAL_COMPANIES:
                continue
            if is_honeypot(candidate):
                continue
            heuristic = self._heuristic_score(candidate)
            if heuristic >= SEMANTIC_MIN_HEURISTIC_SCORE:
                survivors.append((heuristic, candidate.candidate_id, candidate))

        # Deterministic selection of the strongest heuristic candidates for semantic rerank
        top_k = heapq.nlargest(SEMANTIC_RERANK_TOPK, survivors, key=lambda item: (item[0], item[1]))
        queue = [(cid, candidate) for _heuristic, cid, candidate in top_k]

        encoded = semantic_scorer.prefill_batch(queue)
        semantic_scorer.mark_prefill_complete()
        return encoded

    def _matched_skill_names(self, candidate: CandidateModel) -> list[str]:
        matched: list[str] = []
        for skill in candidate.skills:
            skill_lower = skill.name.lower()
            for kw in self.job_reqs.must_have_skills:
                if any(v in skill_lower for v in expand_skill_keyword(kw)):
                    matched.append(skill.name)
                    break
        return matched

    def score_candidate(self, candidate: CandidateModel) -> tuple[float, str]:
        if candidate.profile.current_company in FICTIONAL_COMPANIES:
            return 0.0, ""

        if is_honeypot(candidate):
            return 0.0, ""

        total_score = self._heuristic_score(candidate)

        semantic_scorer = self._semantic_scorer()
        if semantic_scorer is not None and total_score >= SEMANTIC_MIN_HEURISTIC_SCORE:
            total_score += semantic_scorer(candidate)

        behavioral_modifier = self.behavioral_scorer.score(candidate)
        total_score *= behavioral_modifier

        matched_skills = self._matched_skill_names(candidate)
        return round(total_score, 4), ",".join(matched_skills)

    def rank(
        self,
        candidates: Iterable[CandidateModel],
        top_k: int = 100,
        *,
        require_exact_count: bool = True,
    ) -> list[tuple[float, CandidateModel, str]]:
        t0 = time.perf_counter()
        # On full passes, keep a larger pool so the cross-encoder has room to rerank.
        rerank_enabled = require_exact_count
        heap_k = max(top_k, RERANK_POOL_SIZE) if rerank_enabled else top_k
        heap: list[tuple[float, int, CandidateModel, str]] = []
        scored = 0
        filtered_zero = 0
        input_count = 0

        for candidate in candidates:
            input_count += 1
            self.last_input_ids.add(candidate.candidate_id)
            score, matched_skills_csv = self.score_candidate(candidate)
            if score == 0.0:
                filtered_zero += 1
                continue
            scored += 1

            try:
                id_num = int(candidate.candidate_id.split("_")[1])
                tie_breaker = -id_num
            except Exception:
                tie_breaker = 0

            item = (score, tie_breaker, candidate, matched_skills_csv)

            if len(heap) < heap_k:
                heapq.heappush(heap, item)
            else:
                heapq.heappushpop(heap, item)

        score_ms = int((time.perf_counter() - t0) * 1000)
        heap.sort(key=lambda x: (x[0], x[1]), reverse=True)

        pool: list[tuple[float, CandidateModel, str]] = [(s, c, m) for s, _t, c, m in heap]
        if rerank_enabled:
            pool = CrossEncoderReranker(self.job_reqs.raw_text).rerank(pool, top_k)
        else:
            pool = pool[:top_k]

        results: list[tuple[float, CandidateModel, str]] = []
        must_have_count = len(self.job_reqs.must_have_skills)
        for rank_idx, (score, candidate, matched_skills_csv) in enumerate(pool):
            matched_skills = [s for s in matched_skills_csv.split(",") if s]
            reasoning = generate_reasoning(
                candidate,
                rank_idx,
                matched_skills,
                must_have_count=must_have_count,
                score=score,
            )
            results.append((score, candidate, reasoning))

        total_ms = int((time.perf_counter() - t0) * 1000)
        self.last_pipeline_stats = {
            "input_count": input_count,
            "scored_count": scored,
            "filtered_zero": filtered_zero,
            "output_count": len(results),
            "prefill_ms": 0,
            "score_ms": score_ms,
            "total_ms": total_ms,
        }

        if require_exact_count and top_k >= EXPECTED_SUBMISSION_ROWS and len(results) < top_k:
            raise RuntimeError(f"Expected exactly {top_k} candidates after filtering, but got {len(results)}. Dataset is too small or filters are too strict.")

        return results
