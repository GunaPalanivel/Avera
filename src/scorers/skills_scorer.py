from src.models import CandidateModel
from src.scorers.base import BaseScorer


class SkillsScorer(BaseScorer):
    def __init__(self, weight: float, must_have: tuple[str, ...], nice_to_have: tuple[str, ...]):
        super().__init__(weight)
        self.must_have = must_have
        self.nice_to_have = nice_to_have

    def score(self, candidate: CandidateModel) -> float:
        # Extract self-reported skills
        self_reported = {s.name.lower(): s for s in candidate.skills}

        # Extract assessed skills
        assessed_skills = {k.lower(): v for k, v in candidate.redrob_signals.skill_assessment_scores.items()}

        # Check MUST_HAVE (max 0.7)
        must_have_count = 0
        for kw in self.must_have:
            # Check assessed first (1.0 weight)
            if any(kw in a for a in assessed_skills):
                must_have_count += 1
            # Check self-reported (0.5 weight)
            elif any(kw in s for s in self_reported):
                must_have_count += 0.5

            # Cap at 4 must-have skills equivalent
            if must_have_count >= 4:
                break

        # Normalize must have score to 0.7
        must_have_score = min(0.7, (must_have_count / 4.0) * 0.7) if self.must_have else 0.7

        # Check NICE_TO_HAVE (max 0.3)
        nice_count = 0
        for kw in self.nice_to_have:
            if any(kw in a for a in assessed_skills):
                nice_count += 1
            elif any(kw in s for s in self_reported):
                nice_count += 0.5

        nice_score = min(0.3, (nice_count / 2.0) * 0.3) if self.nice_to_have else 0.3

        return must_have_score + nice_score
