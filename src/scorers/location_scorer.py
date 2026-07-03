from src.config import JD_CITY_CATALOG
from src.models import CandidateModel
from src.scorers.base import BaseScorer


class LocationScorer(BaseScorer):
    def __init__(self, weight: float, target_cities: tuple[str, ...] | None = None):
        super().__init__(weight)
        self.target_cities = target_cities if target_cities else JD_CITY_CATALOG

    def score(self, candidate: CandidateModel) -> float:
        location = candidate.profile.location.lower()
        country = candidate.profile.country.lower() if candidate.profile.country else ""

        score = 0.0

        if "india" in country or "india" in location:
            score = max(score, 0.4)

        if candidate.redrob_signals.willing_to_relocate:
            score = max(score, 0.8)

        if any(t in location for t in self.target_cities):
            score = max(score, 1.0)

        # Remote/hybrid preference lowers location friction for tier-2 Bharat talent surfacing
        mode = (candidate.redrob_signals.preferred_work_mode or "").lower()
        if mode in ("remote", "hybrid"):
            score = max(score, 0.85)

        return score
