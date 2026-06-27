from src.detectors.honeypot_detector import is_honeypot
from src.models import CandidateModel
from tests.test_scorers import get_base_candidate


def test_honeypot_marketing_trap():
    c_dict = get_base_candidate()
    c_dict["profile"]["current_title"] = "Marketing Manager"
    # Need 5 AI skills to trigger Method 1
    c_dict["skills"] = [
        {"name": "Python", "proficiency": "expert", "endorsements": 10, "duration_months": 24},
        {"name": "Machine Learning", "proficiency": "advanced", "endorsements": 5, "duration_months": 12},
        {"name": "Deep Learning", "proficiency": "advanced", "endorsements": 5, "duration_months": 12},
        {"name": "LLM", "proficiency": "advanced", "endorsements": 5, "duration_months": 12},
        {"name": "Vector Database", "proficiency": "advanced", "endorsements": 5, "duration_months": 12},
        {"name": "RAG", "proficiency": "advanced", "endorsements": 5, "duration_months": 12},
    ]
    c = CandidateModel.model_validate(c_dict)
    assert is_honeypot(c) is True


def test_honeypot_expert_zero():
    c_dict = get_base_candidate()
    c_dict["skills"] = [
        {"name": "Python", "proficiency": "expert", "endorsements": 10, "duration_months": 0},
        {"name": "Java", "proficiency": "expert", "endorsements": 10, "duration_months": 0},
        {"name": "C++", "proficiency": "expert", "endorsements": 10, "duration_months": 0},
    ]
    c = CandidateModel.model_validate(c_dict)
    assert is_honeypot(c) is True


def test_not_honeypot():
    c_dict = get_base_candidate()
    c = CandidateModel.model_validate(c_dict)
    assert is_honeypot(c) is False
