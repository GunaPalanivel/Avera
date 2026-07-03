from src.models import CandidateModel
from src.parsers.jd_parser import JobRequirements
from src.ranker import Ranker
from tests.test_scorers import get_base_candidate


def get_dummy_reqs() -> JobRequirements:
    return JobRequirements(
        raw_text="",
        must_have_skills=("python",),
        nice_to_have_skills=(),
        title_keywords=("ai", "ml"),
        target_cities=("pune",),
        red_flags=(),
    )


def test_ranker_malformed_id_tie_break():
    ranker = Ranker(get_dummy_reqs())
    c = CandidateModel.model_validate(get_base_candidate())
    c = c.model_copy(update={"candidate_id": "CAND_NOTNUM"})
    results = ranker.rank([c], top_k=1, require_exact_count=False)
    assert len(results) == 1


def test_ranker_partial_results_small_pool():
    ranker = Ranker(get_dummy_reqs())
    c = CandidateModel.model_validate(get_base_candidate())
    results = ranker.rank([c], top_k=10, require_exact_count=True)
    assert len(results) == 1
