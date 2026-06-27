import pytest
from src.models import CandidateModel
from src.ranker import Ranker
from tests.test_scorers import get_base_candidate

def test_ranker_honeypot():
    ranker = Ranker()
    c_dict = get_base_candidate()
    c_dict["profile"]["current_title"] = "Marketing Manager"
    c_dict["skills"].append({"name": "LLM", "proficiency": "expert", "endorsements": 10, "duration_months": 24})
    c = CandidateModel.model_validate(c_dict)
    
    score = ranker.score_candidate(c)
    assert score == 0.0

def test_ranker_normal():
    ranker = Ranker()
    c_dict = get_base_candidate()
    c = CandidateModel.model_validate(c_dict)
    
    score = ranker.score_candidate(c)
    assert 0.0 < score <= 1.0
    
def test_ranker_top_k():
    ranker = Ranker()
    candidates = []
    
    # Add 5 normal candidates with increasing scores (by varying something, like notice period)
    for i in range(5):
        c_dict = get_base_candidate()
        c_dict["candidate_id"] = f"CAND_{1000000+i}"
        # We can just change location to affect score
        if i % 2 == 0:
            c_dict["profile"]["location"] = "Pune"
        else:
            c_dict["profile"]["location"] = "Unknown"
        candidates.append(CandidateModel.model_validate(c_dict))
        
    results = ranker.rank(candidates, top_k=2)
    assert len(results) == 2
    # Ensure they are sorted descending by score
    assert results[0][0] >= results[1][0]
