from unittest.mock import MagicMock

from src.models import CandidateModel
from src.rerank import CrossEncoderReranker
from tests.test_scorers import get_base_candidate


def _pool(n: int) -> list[tuple[float, CandidateModel, str]]:
    items = []
    for i in range(n):
        d = get_base_candidate()
        d["candidate_id"] = f"CAND_{i:07d}"
        items.append((round(0.9 - i * 0.01, 4), CandidateModel.model_validate(d), "Python"))
    return items


def _pool_with_ids(ids: list[str]) -> list[tuple[float, CandidateModel, str]]:
    items = []
    for i, cid in enumerate(ids):
        d = get_base_candidate()
        d["candidate_id"] = cid
        items.append((round(0.90 - i * 0.01, 4), CandidateModel.model_validate(d), "Python"))
    return items


def test_rerank_falls_back_to_base_order_when_skipped(monkeypatch):
    monkeypatch.setenv("AVERA_SKIP_SEMANTIC", "1")
    pool = _pool(5)
    out = CrossEncoderReranker("Senior AI Engineer").rerank(pool, top_k=3)
    assert [c.candidate_id for _s, c, _m in out] == [c.candidate_id for _s, c, _m in pool[:3]]


def test_rerank_empty_pool():
    assert CrossEncoderReranker("jd").rerank([], top_k=10) == []


def test_rerank_minmax_spread_without_sigmoid(monkeypatch):
    monkeypatch.delenv("AVERA_SKIP_SEMANTIC", raising=False)
    monkeypatch.delenv("AVERA_SKIP_RERANK", raising=False)

    pool = _pool_with_ids(["CAND_0000003", "CAND_0000002", "CAND_0000001"])
    reranker = CrossEncoderReranker("Senior AI Engineer", alpha=0.15)
    reranker._model = MagicMock()
    reranker._model.predict.return_value = [3.2, 3.5, 3.8]

    out = reranker.rerank(pool, top_k=3)
    scores = [s for s, _c, _m in out]
    assert scores[0] > scores[1] > scores[2]
    assert max(scores) - min(scores) >= 0.03
    assert out[0][1].candidate_id == "CAND_0000001"


def test_rerank_clamps_blended_score_at_one(monkeypatch):
    monkeypatch.delenv("AVERA_SKIP_SEMANTIC", raising=False)
    monkeypatch.delenv("AVERA_SKIP_RERANK", raising=False)

    d = get_base_candidate()
    d["candidate_id"] = "CAND_0000001"
    pool = [(1.0, CandidateModel.model_validate(d), "Python")]
    reranker = CrossEncoderReranker("Senior AI Engineer", alpha=0.15)
    reranker._model = MagicMock()
    reranker._model.predict.return_value = [9.0]

    out = reranker.rerank(pool, top_k=1)
    assert out[0][0] == 1.0
