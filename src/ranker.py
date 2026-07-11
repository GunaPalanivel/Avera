import heapq
import logging
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

logger = logging.getLogger(__name__)


def _written_scores(
    ordered: list[tuple[float, float, float, CandidateModel, str]],
) -> list[tuple[float, float, CandidateModel, str]]:
    """Convert merit-ordered pool rows to submission scores.

    ordered: (display, raw_merit, join_prob, candidate, matched_skills_csv)
    Merit order is already fixed; assign strictly decreasing scores from 1.0 so
    validator tie-break rules and non-increasing rank order both hold.
    """
    written: list[tuple[float, float, CandidateModel, str]] = []
    for idx, (_display, _raw, join_prob, candidate, matched) in enumerate(ordered):
        score = round(max(0.0, 1.0 - idx * 0.0001), 4)
        written.append((score, join_prob, candidate, matched))
    return written


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

    def score_candidate(self, candidate: CandidateModel) -> tuple[float, float, float, str]:
        if candidate.profile.current_company in FICTIONAL_COMPANIES:
            return 0.0, 0.0, 0.0, ""

        if is_honeypot(candidate):
            return 0.0, 0.0, 0.0, ""

        total_score = self._heuristic_score(candidate)

        semantic_scorer = self._semantic_scorer()
        if semantic_scorer is not None and total_score >= SEMANTIC_MIN_HEURISTIC_SCORE:
            total_score += semantic_scorer(candidate)

        behavioral_modifier = self.behavioral_scorer.score(candidate)
        raw_score = round(total_score * behavioral_modifier, 4)
        display_score = min(1.0, raw_score)
        join_prob = self.behavioral_scorer.join_probability(candidate)

        matched_skills = self._matched_skill_names(candidate)
        return round(display_score, 4), raw_score, round(join_prob, 4), ",".join(matched_skills)

    def rank(
        self,
        candidates: Iterable[CandidateModel],
        top_k: int = 100,
        *,
        require_exact_count: bool = True,
        enable_rerank: bool | None = None,
    ) -> list[tuple[float, float, CandidateModel, str]]:
        t0 = time.perf_counter()
        # Keep a larger pool when CE rerank runs so the cross-encoder has room to reorder.
        rerank_enabled = enable_rerank if enable_rerank is not None else require_exact_count
        heap_k = max(top_k, RERANK_POOL_SIZE) if rerank_enabled else top_k
        heap: list[tuple[float, float, float, CandidateModel, str]] = []
        scored = 0
        filtered_zero = 0
        filtered_fictional = 0
        filtered_honeypot = 0
        semantic_gate_pass = 0
        input_count = 0
        ce_rerank_ms = 0

        for candidate in candidates:
            input_count += 1
            self.last_input_ids.add(candidate.candidate_id)
            if candidate.profile.current_company in FICTIONAL_COMPANIES:
                filtered_fictional += 1
                filtered_zero += 1
                continue
            if is_honeypot(candidate):
                filtered_honeypot += 1
                filtered_zero += 1
                continue
            if self._heuristic_score(candidate) >= SEMANTIC_MIN_HEURISTIC_SCORE:
                semantic_gate_pass += 1
            score, raw_score, join_prob, matched_skills_csv = self.score_candidate(candidate)
            if score == 0.0:
                filtered_zero += 1
                continue
            scored += 1

            item = (score, -raw_score, join_prob, candidate, matched_skills_csv)

            if len(heap) < heap_k:
                heapq.heappush(heap, item)
            else:
                heapq.heappushpop(heap, item)

        score_ms = int((time.perf_counter() - t0) * 1000)
        heap.sort(key=lambda x: (x[0], x[1], x[3].candidate_id), reverse=True)

        pool: list[tuple[float, float, CandidateModel, str]] = [(s, jp, c, m) for s, _neg_raw, jp, c, m in heap]
        if rerank_enabled:
            rerank_pool: list[tuple[float, CandidateModel, str]] = [(s, c, m) for s, _jp, c, m in pool]
            t_ce = time.perf_counter()
            reranked = CrossEncoderReranker(self.job_reqs.raw_text).rerank(rerank_pool, top_k)
            ce_rerank_ms = int((time.perf_counter() - t_ce) * 1000)
            join_by_id = {c.candidate_id: jp for _s, jp, c, _m in pool}
            merit_pool = [(min(1.0, s), raw, join_by_id[c.candidate_id], c, matched) for s, c, matched, raw in reranked]
        else:
            merit_pool = [(s, -neg_raw, jp, c, m) for s, neg_raw, jp, c, m in heap[:top_k]]

        pool = _written_scores(merit_pool)

        results: list[tuple[float, float, CandidateModel, str]] = []
        must_have_count = len(self.job_reqs.must_have_skills)
        for rank_idx, (score, join_prob, candidate, matched_skills_csv) in enumerate(pool):
            matched_skills = [s for s in matched_skills_csv.split(",") if s]
            reasoning = generate_reasoning(
                candidate,
                rank_idx,
                matched_skills,
                must_have_count=must_have_count,
                score=score,
                join_probability=join_prob,
            )
            results.append((score, join_prob, candidate, reasoning))

        total_ms = int((time.perf_counter() - t0) * 1000)
        self.last_pipeline_stats = {
            "input_count": input_count,
            "scored_count": scored,
            "filtered_zero": filtered_zero,
            "filtered_fictional": filtered_fictional,
            "filtered_honeypot": filtered_honeypot,
            "semantic_gate_pass": semantic_gate_pass,
            "output_count": len(results),
            "prefill_ms": 0,
            "score_ms": score_ms,
            "ce_rerank_ms": ce_rerank_ms,
            "total_ms": total_ms,
        }

        if require_exact_count and len(results) < top_k:
            logger.warning(
                "Expected %d candidates after filtering, got %d",
                top_k,
                len(results),
            )
            if top_k >= EXPECTED_SUBMISSION_ROWS:
                raise RuntimeError(f"Expected exactly {top_k} candidates after filtering, but got {len(results)}. Dataset is too small or filters are too strict.")

        return results
