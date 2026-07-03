from src.config import expand_skill_adjacency, expand_skill_keyword
from src.models import CandidateModel
from src.scorers.base import BaseScorer

ADJACENCY_ASSESSED_CREDIT = 0.7
ADJACENCY_SELF_CREDIT = 0.35


def _pool_matches_keyword(keyword: str, pool: set[str]) -> bool:
    for variant in expand_skill_keyword(keyword):
        if any(variant in item for item in pool):
            return True
    return False


def _pool_matches_adjacency(keyword: str, pool: set[str]) -> bool:
    for variant in expand_skill_adjacency(keyword):
        if any(variant in item for item in pool):
            return True
    return False


def _self_reported_credit(duration_months: int | None) -> float:
    if duration_months is None or duration_months <= 0:
        return 0.25
    return min(1.0, duration_months / 24.0) * 0.5


class SkillsScorer(BaseScorer):
    def __init__(self, weight: float, must_have: tuple[str, ...], nice_to_have: tuple[str, ...]):
        super().__init__(weight)
        self.must_have = must_have
        self.nice_to_have = nice_to_have

    def _keyword_credit(self, keyword: str, assessed: set[str], self_reported: dict[str, int | None]) -> float:
        if _pool_matches_keyword(keyword, assessed):
            return 1.0
        for name, duration in self_reported.items():
            if any(v in name for v in expand_skill_keyword(keyword)):
                return _self_reported_credit(duration)
        if _pool_matches_adjacency(keyword, assessed):
            return ADJACENCY_ASSESSED_CREDIT
        for name, duration in self_reported.items():
            if any(v in name for v in expand_skill_adjacency(keyword)):
                return ADJACENCY_SELF_CREDIT * max(0.5, _self_reported_credit(duration) / 0.5)
        return 0.0

    def score(self, candidate: CandidateModel) -> float:
        self_reported = {s.name.lower(): s.duration_months for s in candidate.skills}
        assessed_skills = {k.lower() for k in candidate.redrob_signals.skill_assessment_scores}

        must_have_count = 0.0
        for kw in self.must_have:
            must_have_count += self._keyword_credit(kw, assessed_skills, self_reported)
            if must_have_count >= 4:
                break

        must_have_score = min(0.7, (must_have_count / 4.0) * 0.7) if self.must_have else 0.0

        nice_count = 0.0
        for kw in self.nice_to_have:
            nice_count += self._keyword_credit(kw, assessed_skills, self_reported)

        nice_score = min(0.3, (nice_count / 2.0) * 0.3) if self.nice_to_have else 0.0

        return must_have_score + nice_score
