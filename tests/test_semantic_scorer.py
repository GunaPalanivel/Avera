from unittest.mock import MagicMock

import pytest
from src.models import CandidateModel
from src.scorers.semantic_scorer import SemanticScorer
from tests.test_scorers import get_base_candidate


def test_semantic_scorer_uses_career_descriptions(monkeypatch):
    monkeypatch.delenv("AVERA_SKIP_SEMANTIC", raising=False)

    mock_model = MagicMock()
    mock_util = MagicMock()
    mock_model.encode.side_effect = ["jd_emb", "cand_emb"]
    mock_util.cos_sim.return_value.item.return_value = 0.82

    c_dict = get_base_candidate()
    c_dict["profile"]["summary"] = "Built semantic search with FAISS and embeddings."
    c_dict["career_history"][0]["description"] = "Deployed RAG pipeline in production."
    candidate = CandidateModel.model_validate(c_dict)

    scorer = SemanticScorer(weight=0.15, jd_text="Senior AI Engineer with embeddings experience")
    scorer._model = mock_model
    scorer._util = mock_util
    scorer._jd_embedding = "jd_emb"

    score = scorer.score(candidate)

    assert score == pytest.approx(0.82, rel=1e-3)
    encoded_text = mock_model.encode.call_args_list[-1][0][0]
    assert "RAG pipeline" in encoded_text
    assert "semantic search" in encoded_text
    encoded_text = mock_model.encode.call_args_list[-1][0][0]
    assert "RAG pipeline" in encoded_text
    assert "semantic search" in encoded_text


def test_semantic_scorer_empty_jd_returns_zero():
    scorer = SemanticScorer(weight=0.15, jd_text="")
    c = CandidateModel.model_validate(get_base_candidate())
    assert scorer.score(c) == 0.0
