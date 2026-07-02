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


def test_rerank_falls_back_to_base_order_when_skipped(monkeypatch):
    # AVERA_SKIP_SEMANTIC is set by conftest; rerank must degrade to the base top_k order
    monkeypatch.setenv("AVERA_SKIP_SEMANTIC", "1")
    pool = _pool(5)
    out = CrossEncoderReranker("Senior AI Engineer").rerank(pool, top_k=3)
    assert [c.candidate_id for _s, c, _m in out] == [c.candidate_id for _s, c, _m in pool[:3]]


def test_rerank_empty_pool():
    assert CrossEncoderReranker("jd").rerank([], top_k=10) == []
