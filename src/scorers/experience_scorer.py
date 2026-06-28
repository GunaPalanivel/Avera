from src.models import CandidateModel
from src.scorers.base import BaseScorer


class ExperienceScorer(BaseScorer):
    def score(self, candidate: CandidateModel) -> float:
        yoe = candidate.profile.years_of_experience

        # Calculate ML/AI specific tenure
        ml_keywords = {"ml", "machine learning", "ai", "artificial intelligence", "data scientist", "deep learning", "nlp", "computer vision"}
        ml_months = 0
        for job in candidate.career_history:
            if any(kw in job.title.lower() for kw in ml_keywords):
                ml_months += job.duration_months

        ml_yoe = ml_months / 12.0

        # Step bands for total YOE
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

        # Penalty if they have high total YOE but very little ML YOE (JD wants 4-5 years in ML)
        if ml_yoe < 2.0:
            return base_score * 0.2
        elif ml_yoe < 4.0:
            return base_score * 0.6

        return base_score
