from src.models import CandidateModel
from src.parsers.jd_parser import JobRequirements
from src.ranker import Ranker
from tests.test_scorers import get_base_candidate


def get_dummy_reqs():
    return JobRequirements(raw_text="", must_have_skills=("python",), nice_to_have_skills=(), title_keywords=(), red_flags=())


def test_ranker_honeypot():
    ranker = Ranker(get_dummy_reqs())
    c_dict = get_base_candidate()
    c_dict["profile"]["current_title"] = "Marketing Manager"
    c_dict["skills"].extend(
        [
            {"name": "Machine Learning", "proficiency": "expert", "endorsements": 10, "duration_months": 24},
            {"name": "Deep Learning", "proficiency": "expert", "endorsements": 10, "duration_months": 24},
            {"name": "LLM", "proficiency": "expert", "endorsements": 10, "duration_months": 24},
            {"name": "Vector Database", "proficiency": "expert", "endorsements": 10, "duration_months": 24},
            {"name": "RAG", "proficiency": "expert", "endorsements": 10, "duration_months": 24},
        ]
    )
    c = CandidateModel.model_validate(c_dict)

    score, reasoning = ranker.score_candidate(c)
    assert score == 0.0
    assert reasoning == ""


def test_ranker_normal():
    ranker = Ranker(get_dummy_reqs())
    c_dict = get_base_candidate()
    c = CandidateModel.model_validate(c_dict)

    score, reasoning = ranker.score_candidate(c)
    assert 0.0 < score <= 1.0
    assert isinstance(reasoning, str)
    assert len(reasoning) > 0


def test_ranker_top_k():
    ranker = Ranker(get_dummy_reqs())

    c_dict1 = get_base_candidate()
    c_dict1["candidate_id"] = "CAND_0000001"
    c1 = CandidateModel.model_validate(c_dict1)

    c_dict2 = get_base_candidate()
    c_dict2["candidate_id"] = "CAND_0000002"
    c2 = CandidateModel.model_validate(c_dict2)

    # We assume c2 has a higher or lower score, just testing rank() structure
    ranked = ranker.rank([c1, c2], top_k=1)

    assert len(ranked) == 1
    assert isinstance(ranked[0][0], float)
    assert ranked[0][1].candidate_id in ("CAND_0000001", "CAND_0000002")
    assert isinstance(ranked[0][2], str)
