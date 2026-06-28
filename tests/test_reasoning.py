from src.models import CandidateModel
from src.reasoning import generate_reasoning
from tests.test_scorers import get_base_candidate


def test_reasoning_top_five_tone():
    c = CandidateModel.model_validate(get_base_candidate())
    text = generate_reasoning(c, rank_index=0, matched_skills=["Python", "Pinecone"])
    assert "Exceptional Top 5 Match" in text
    assert "Python" in text


def test_reasoning_borderline_tone():
    c = CandidateModel.model_validate(get_base_candidate())
    text = generate_reasoning(c, rank_index=95, matched_skills=[])
    assert "Borderline Match" in text


def test_reasoning_no_hallucinated_fields():
    c = CandidateModel.model_validate(get_base_candidate())
    text = generate_reasoning(c, rank_index=10, matched_skills=["Python"])
    assert c.profile.current_company in text
    assert "Google" not in text
