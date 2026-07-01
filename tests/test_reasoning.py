from src.models import CandidateModel
from src.reasoning import generate_reasoning
from tests.test_scorers import get_base_candidate


def test_reasoning_top_five_tone():
    c = CandidateModel.model_validate(get_base_candidate())
    text = generate_reasoning(c, rank_index=0, matched_skills=["Python", "Pinecone"])
    assert "Rank 1:" in text
    assert "Python" in text
    assert "Strong fit" not in text


def test_reasoning_top_rank_has_counterfactual():
    c = CandidateModel.model_validate(get_base_candidate())
    # Full coverage, clean signals -> no hard concern, so a counterfactual must still appear
    text = generate_reasoning(c, rank_index=0, matched_skills=["Python", "Pinecone"], must_have_count=2)
    assert "Counterfactual:" in text or "Minor note:" in text


def test_reasoning_weak_score_not_overclaimed():
    c = CandidateModel.model_validate(get_base_candidate())
    # A low absolute score at rank 1 must not be framed as "Top-tier" / "Strong match"
    text = generate_reasoning(c, rank_index=0, matched_skills=["Python"], must_have_count=20, score=0.42)
    assert "Top-tier" not in text
    assert "Strong match" not in text
    assert "weak absolute fit" in text.lower()


def test_reasoning_strong_score_keeps_top_tier():
    c = CandidateModel.model_validate(get_base_candidate())
    text = generate_reasoning(c, rank_index=0, matched_skills=["Python", "Pinecone"], must_have_count=2, score=0.95)
    assert "Rank 1:" in text


def test_reasoning_thin_coverage_top_rank_frames_as_trajectory():
    c = CandidateModel.model_validate(get_base_candidate())
    # 3 of 20 must-haves matched at a strong score -> career-trajectory framing, not apology
    text = generate_reasoning(c, rank_index=0, matched_skills=["Python", "Pinecone", "NLP"], must_have_count=20, score=0.95)
    assert "career trajectory" in text
    assert "trails a perfect match" not in text


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
