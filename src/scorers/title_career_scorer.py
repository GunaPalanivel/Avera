from src.config import AI_TITLE_TIERS, CONSULTING_FIRMS, CV_SPEECH_ROBOTICS_TERMS, NLP_IR_TERMS
from src.models import CandidateModel
from src.scorers.base import BaseScorer

_SENIOR_TITLE_TOKENS = ("senior", "lead", "principal", "staff")


class TitleCareerScorer(BaseScorer):
    def __init__(
        self,
        weight: float,
        title_tiers: dict[str, float] | None = None,
        anti_requirements: tuple[str, ...] = (),
    ):
        super().__init__(weight)
        # None means "caller did not specify" -> default to AI/ML. An explicit empty dict
        # (generic domain) is respected as "no title-tier bias".
        self.title_tiers = AI_TITLE_TIERS if title_tiers is None else title_tiers
        self.anti_requirements = anti_requirements

    def _anti_requirement_penalty(self, candidate: CandidateModel) -> float:
        """Bounded penalty when a JD-named anti-requirement matches the candidate."""
        penalty = 0.0

        if "title_chaser" in self.anti_requirements:
            career = candidate.career_history
            if len(career) >= 3:
                avg_months = sum(c.duration_months for c in career) / len(career)
                escalates = any(any(t in c.title.lower() for t in _SENIOR_TITLE_TOKENS) for c in career)
                if avg_months < 18 and escalates:
                    penalty += 0.15

        if "cv_speech_robotics_without_nlp" in self.anti_requirements:
            skill_text = " ".join(s.name.lower() for s in candidate.skills)
            has_cv = any(term in skill_text for term in CV_SPEECH_ROBOTICS_TERMS)
            has_nlp = any(term in skill_text for term in NLP_IR_TERMS)
            if has_cv and not has_nlp:
                penalty += 0.15

        return penalty

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

        raw = title_score + company_score + hopping_score
        return max(0.0, raw - self._anti_requirement_penalty(candidate))
