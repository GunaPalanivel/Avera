import heapq
from collections.abc import Iterable

from src.config import FICTIONAL_COMPANIES, SCORER_WEIGHTS, expand_skill_keyword
from src.detectors.honeypot_detector import is_honeypot
from src.models import CandidateModel
from src.output_writer import EXPECTED_SUBMISSION_ROWS
from src.parsers.jd_parser import JobRequirements
from src.reasoning import generate_reasoning
from src.scorers.behavioral_scorer import BehavioralScorer
from src.scorers.experience_scorer import ExperienceScorer
from src.scorers.location_scorer import LocationScorer
from src.scorers.semantic_scorer import SemanticScorer
from src.scorers.skills_scorer import SkillsScorer
from src.scorers.title_career_scorer import TitleCareerScorer


class Ranker:
    def __init__(self, job_reqs: JobRequirements):
        self.job_reqs = job_reqs
        self.scorers = [
            TitleCareerScorer(weight=SCORER_WEIGHTS["title_career"]),
            SkillsScorer(
                weight=SCORER_WEIGHTS["skills"],
                must_have=job_reqs.must_have_skills,
                nice_to_have=job_reqs.nice_to_have_skills,
            ),
            ExperienceScorer(weight=SCORER_WEIGHTS["experience"], title_keywords=job_reqs.title_keywords),
            LocationScorer(weight=SCORER_WEIGHTS["location"], target_cities=job_reqs.target_cities),
            SemanticScorer(weight=SCORER_WEIGHTS["semantic"], jd_text=job_reqs.raw_text),
        ]
        self.behavioral_scorer = BehavioralScorer(weight=1.0)
        self.last_input_ids: set[str] = set()

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

        total_score = 0.0
        for scorer in self.scorers:
            total_score += scorer(candidate)

        behavioral_modifier = self.behavioral_scorer.score(candidate)
        total_score *= behavioral_modifier

        matched_skills = self._matched_skill_names(candidate)
        return round(total_score, 4), ",".join(matched_skills)

    def rank(self, candidates: Iterable[CandidateModel], top_k: int = 100) -> list[tuple[float, CandidateModel, str]]:
        heap: list[tuple[float, int, CandidateModel, str]] = []
        self.last_input_ids = set()

        for candidate in candidates:
            self.last_input_ids.add(candidate.candidate_id)
            score, matched_skills_csv = self.score_candidate(candidate)
            if score == 0.0:
                continue

            try:
                id_num = int(candidate.candidate_id.split("_")[1])
                tie_breaker = -id_num
            except Exception:
                tie_breaker = 0

            item = (score, tie_breaker, candidate, matched_skills_csv)

            if len(heap) < top_k:
                heapq.heappush(heap, item)
            else:
                heapq.heappushpop(heap, item)

        heap.sort(key=lambda x: (x[0], x[1]), reverse=True)

        results: list[tuple[float, CandidateModel, str]] = []
        for rank_idx, (score, _tie, candidate, matched_skills_csv) in enumerate(heap):
            matched_skills = [s for s in matched_skills_csv.split(",") if s]
            reasoning = generate_reasoning(candidate, rank_idx, matched_skills)
            results.append((score, candidate, reasoning))

        if top_k >= EXPECTED_SUBMISSION_ROWS and len(results) < top_k:
            raise RuntimeError(f"Expected exactly {top_k} candidates after filtering, but got {len(results)}. Dataset is too small or filters are too strict.")

        return results
