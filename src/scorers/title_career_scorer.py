from src.config import AI_TITLE_TIERS, CONSULTING_FIRMS
from src.models import CandidateModel
from src.scorers.base import BaseScorer


class TitleCareerScorer(BaseScorer):
    def __init__(self, weight: float, title_tiers: dict[str, float] | None = None):
        super().__init__(weight)
        self.title_tiers = title_tiers if title_tiers else AI_TITLE_TIERS

    def score(self, candidate: CandidateModel) -> float:
        current_title = candidate.profile.current_title.lower()

        title_score = 0.0
        if "junior" not in current_title:
            best_tier = 0.0
            for tier_title, tier_val in sorted(self.title_tiers.items(), key=lambda x: len(x[0]), reverse=True):
                if tier_title in current_title:
                    best_tier = max(best_tier, tier_val)
            title_score = best_tier * 0.5

        company_score = 0.3
        career = candidate.career_history
        all_companies = [c.company.lower() for c in career]

        consulting_count = sum(1 for c in all_companies if any(f in c for f in CONSULTING_FIRMS))
        if consulting_count == len(all_companies) and len(all_companies) > 0:
            company_score = 0.1
        elif consulting_count > 0:
            company_score = 0.25

        hopping_score = 0.2
        if len(career) > 1 and title_score < 0.5:
            total_months = sum(c.duration_months for c in career)
            avg_months = total_months / len(career)
            if avg_months < 15:
                hopping_score = 0.0
            elif avg_months < 24:
                hopping_score = 0.1

        return title_score + company_score + hopping_score
