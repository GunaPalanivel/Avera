from src.models import CandidateModel
from src.scorers.base import BaseScorer

class ExperienceScorer(BaseScorer):
    def score(self, candidate: CandidateModel) -> float:
        yoe = candidate.profile.years_of_experience
        
        # 5-9 years is the optimal band (JD L24-25)
        if 5 <= yoe <= 9:
            return 1.0
        elif 9 < yoe <= 12:
            return 0.8
        elif yoe > 12:
            return 0.6
        elif 4 <= yoe < 5:
            return 0.5
        elif 3 <= yoe < 4:
            return 0.2
        else:
            return 0.0
