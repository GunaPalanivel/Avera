from src.config import expand_skill_keyword
from src.models import CandidateModel
from src.scorers.base import BaseScorer


def _pool_matches_keyword(keyword: str, pool: set[str]) -> bool:
    for variant in expand_skill_keyword(keyword):
        if any(variant in item for item in pool):
            return True
    return False


class SkillsScorer(BaseScorer):
    def __init__(self, weight: float, must_have: tuple[str, ...], nice_to_have: tuple[str, ...]):
        super().__init__(weight)
        self.must_have = must_have
        self.nice_to_have = nice_to_have

    def score(self, candidate: CandidateModel) -> float:
        self_reported = {s.name.lower() for s in candidate.skills}
        assessed_skills = {k.lower() for k in candidate.redrob_signals.skill_assessment_scores}

        must_have_count = 0.0
        for kw in self.must_have:
            if _pool_matches_keyword(kw, assessed_skills):
                must_have_count += 1.0
            elif _pool_matches_keyword(kw, self_reported):
                must_have_count += 0.5

            if must_have_count >= 4:
                break

        must_have_score = min(0.7, (must_have_count / 4.0) * 0.7) if self.must_have else 0.0

        nice_count = 0.0
        for kw in self.nice_to_have:
            if _pool_matches_keyword(kw, assessed_skills):
                nice_count += 1.0
            elif _pool_matches_keyword(kw, self_reported):
                nice_count += 0.5

        nice_score = min(0.3, (nice_count / 2.0) * 0.3) if self.nice_to_have else 0.0

        return must_have_score + nice_score
