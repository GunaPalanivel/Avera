import heapq
from collections.abc import Iterable

from src.config import FICTIONAL_COMPANIES, SCORER_WEIGHTS
from src.detectors.honeypot_detector import is_honeypot
from src.models import CandidateModel
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
            SkillsScorer(weight=SCORER_WEIGHTS["skills"], must_have=job_reqs.must_have_skills, nice_to_have=job_reqs.nice_to_have_skills),
            ExperienceScorer(weight=SCORER_WEIGHTS["experience"]),
            LocationScorer(weight=SCORER_WEIGHTS["location"]),
            SemanticScorer(weight=SCORER_WEIGHTS["semantic"], jd_text=job_reqs.raw_text),
        ]
        self.behavioral_scorer = BehavioralScorer(weight=1.0)

    def score_candidate(self, candidate: CandidateModel) -> tuple[float, str]:
        # Stage 1: Drop if current company is fictional
        if candidate.profile.current_company in FICTIONAL_COMPANIES:
            return 0.0, ""

        # Stage 1.5: Subtle honeypot methods
        if is_honeypot(candidate):
            return 0.0, ""

        total_score = 0.0
        for scorer in self.scorers:
            total_score += scorer(candidate)

        # Stage 1.75: Apply multiplicative behavioral modifier
        behavioral_modifier = self.behavioral_scorer.score(candidate)
        total_score *= behavioral_modifier

        matched_skills = [s.name for s in candidate.skills if any(kw in s.name.lower() for kw in self.job_reqs.must_have_skills)]
        # Reasoning will be generated with rank index later in `rank()`
        # For now we just pass matched_skills along
        return round(total_score, 4), ",".join(matched_skills)

    def rank(self, candidates: Iterable[CandidateModel], top_k: int = 100) -> list[tuple[float, CandidateModel, str]]:
        heap = []

        for candidate in candidates:
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

        results = []
        for rank_idx, (score, _tie, candidate, matched_skills_csv) in enumerate(heap):
            matched_skills = matched_skills_csv.split(",") if matched_skills_csv else []
            reasoning = generate_reasoning(candidate, rank_idx, matched_skills)
            results.append((score, candidate, reasoning))

        if len(results) < top_k and top_k == 100:
            raise RuntimeError(f"Expected exactly 100 candidates after filtering, but got {len(results)}. Dataset is too small or filters are too strict.")

        return results
