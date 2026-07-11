from unittest.mock import patch

from src.models import CandidateModel
from src.parsers.jd_parser import JobRequirements
from src.ranker import Ranker, _written_scores
from src.rerank import CrossEncoderReranker
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


def test_ranker_output_scores_bounded(monkeypatch):
    monkeypatch.setenv("AVERA_SKIP_SEMANTIC", "1")
    monkeypatch.setenv("AVERA_SKIP_RERANK", "1")
    ranker = Ranker(get_dummy_reqs())
    c = CandidateModel.model_validate(get_base_candidate())
    results = ranker.rank([c], top_k=1, require_exact_count=False)
    assert all(score <= 1.0 for score, _jp, _c, _r in results)


def test_ranker_clamps_inflated_ce_rerank_scores(monkeypatch):
    """CE rerank path must clamp scores even when reranker returns values above 1.0."""
    monkeypatch.setenv("AVERA_SKIP_SEMANTIC", "1")

    def inflated_rerank(_self, pool, top_k):
        return [(1.0, c, m, 1.15) for _s, c, m in pool[:top_k]]

    ranker = Ranker(get_dummy_reqs())
    c = CandidateModel.model_validate(get_base_candidate())
    with patch.object(CrossEncoderReranker, "rerank", inflated_rerank):
        results = ranker.rank([c], top_k=1, require_exact_count=True)
    assert len(results) == 1
    assert results[0][0] == 1.0


def test_written_scores_spreads_ceiling_tier():
    """Merit-ordered rows get strictly decreasing written scores."""
    d1 = get_base_candidate()
    d1["candidate_id"] = "CAND_0000009"
    d2 = get_base_candidate()
    d2["candidate_id"] = "CAND_0000001"
    c1 = CandidateModel.model_validate(d1)
    c2 = CandidateModel.model_validate(d2)
    ordered = [
        (1.0, 1.15, 0.5, c1, "Python"),
        (1.0, 1.10, 0.5, c2, "Python"),
    ]
    out = _written_scores(ordered)
    assert out[0][0] == 1.0
    assert out[1][0] == 0.9999
    assert out[0][0] > out[1][0]


def test_ranker_rerank_on_limited_slice(monkeypatch):
    """Sandbox uploads use require_exact_count=False but still run CE rerank."""
    monkeypatch.setenv("AVERA_SKIP_SEMANTIC", "1")
    rerank_called = False

    def mock_rerank(_self, pool, top_k):
        nonlocal rerank_called
        rerank_called = True
        return [(s, c, m, s) for s, c, m in pool[:top_k]]

    ranker = Ranker(get_dummy_reqs())
    c = CandidateModel.model_validate(get_base_candidate())
    with patch.object(CrossEncoderReranker, "rerank", mock_rerank):
        results = ranker.rank([c], top_k=10, require_exact_count=False, enable_rerank=True)
    assert rerank_called
    assert len(results) == 1
