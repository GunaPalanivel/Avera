from src.models import CandidateModel
from src.scorers.base import BaseScorer

_TIER_SCORES: dict[str, float] = {
    "tier_1": 1.0,
    "tier_2": 0.7,
    "tier_3": 0.45,
    "tier_4": 0.3,
    "unknown": 0.35,
}

_RELEVANT_FIELDS = (
    "computer science",
    "artificial intelligence",
    "machine learning",
    "data science",
    "statistics",
    "mathematics",
    "information technology",
    "electronics",
    "computer engineering",
)

_NEUTRAL_WHEN_MISSING = 0.35


class EducationScorer(BaseScorer):
    """Rewards institution tier and field relevance from the education records."""

    def score(self, candidate: CandidateModel) -> float:
        if not candidate.education:
            return _NEUTRAL_WHEN_MISSING

        best_tier = 0.0
        relevant = False
        for edu in candidate.education:
            tier_key = (edu.tier or "unknown").lower()
            best_tier = max(best_tier, _TIER_SCORES.get(tier_key, _NEUTRAL_WHEN_MISSING))
            field = edu.field_of_study.lower()
            if any(rf in field for rf in _RELEVANT_FIELDS):
                relevant = True

        score = best_tier
        if relevant:
            score = min(1.0, score + 0.1)
        return score
