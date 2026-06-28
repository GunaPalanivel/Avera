from src.config import TITLE_KEYWORDS_DEFAULT
from src.models import CandidateModel
from src.scorers.base import BaseScorer


class ExperienceScorer(BaseScorer):
    def __init__(self, weight: float, title_keywords: tuple[str, ...] | None = None):
        super().__init__(weight)
        self.title_keywords = title_keywords if title_keywords else TITLE_KEYWORDS_DEFAULT

    def score(self, candidate: CandidateModel) -> float:
        yoe = candidate.profile.years_of_experience

        ml_months = 0
        for job in candidate.career_history:
            title_lower = job.title.lower()
            if any(kw in title_lower for kw in self.title_keywords):
                ml_months += job.duration_months

        ml_yoe = ml_months / 12.0

        base_score = 0.0
        if 5 <= yoe <= 9:
            base_score = 1.0
        elif 9 < yoe <= 12:
            base_score = 0.8
        elif yoe > 12:
            base_score = 0.6
        elif 4 <= yoe < 5:
            base_score = 0.5
        elif 3 <= yoe < 4:
            base_score = 0.2

        if ml_yoe < 2.0:
            return base_score * 0.2
        if ml_yoe < 4.0:
            return base_score * 0.6

        return base_score
