from src.models import CandidateModel
from src.reasoning import generate_reasoning
from tests.test_scorers import get_base_candidate


def test_reasoning_top_five_tone():
    c = CandidateModel.model_validate(get_base_candidate())
    text = generate_reasoning(c, rank_index=0, matched_skills=["Python", "Pinecone"])
    assert "Rank 1:" in text
    assert "Python" in text
    assert "Strong fit" not in text


def test_reasoning_borderline_tone():
    c = CandidateModel.model_validate(get_base_candidate())
    text = generate_reasoning(c, rank_index=95, matched_skills=[])
    assert "Lower-tier" in text or "Gaps:" in text
    assert "Strong fit" not in text


def test_reasoning_mid_rank_variation():
    c = CandidateModel.model_validate(get_base_candidate())
    texts = {generate_reasoning(c, rank_index=i, matched_skills=["Python"]) for i in (25, 26, 27, 28)}
    assert len(texts) >= 2


def test_reasoning_no_hallucinated_fields():
    c = CandidateModel.model_validate(get_base_candidate())
    text = generate_reasoning(c, rank_index=10, matched_skills=["Python"])
    assert c.profile.current_company in text
    assert "Google" not in text
