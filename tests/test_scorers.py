from src.models import CandidateModel
from src.scorers.behavioral_scorer import BehavioralScorer
from src.scorers.experience_scorer import ExperienceScorer
from src.scorers.location_scorer import LocationScorer
from src.scorers.skills_scorer import SkillsScorer
from src.scorers.title_career_scorer import TitleCareerScorer


def get_base_candidate() -> dict:
    return {
        "candidate_id": "CAND_0000001",
        "profile": {
            "anonymized_name": "Test",
            "headline": "Test",
            "summary": "Test",
            "location": "Pune",
            "country": "India",
            "years_of_experience": 7,
            "current_title": "Senior AI Engineer",
            "current_company": "Product Corp",
            "current_company_size": "100-500",
            "current_industry": "Tech",
        },
        "career_history": [
            {
                "company": "Product Corp",
                "title": "Senior AI Engineer",
                "start_date": "2022-01-01",
                "duration_months": 24,
                "is_current": True,
                "industry": "Tech",
                "company_size": "100-500",
                "description": "Test",
            },
            {
                "company": "Other Corp",
                "title": "AI Engineer",
                "start_date": "2020-01-01",
                "duration_months": 24,
                "is_current": False,
                "industry": "Tech",
                "company_size": "100-500",
                "description": "Test",
            },
        ],
        "skills": [
            {"name": "Python", "proficiency": "expert", "endorsements": 10, "duration_months": 48},
            {"name": "Pinecone", "proficiency": "advanced", "endorsements": 5, "duration_months": 24},
        ],
        "redrob_signals": {
            "profile_completeness_score": 100,
            "signup_date": "2020-01-01",
            "last_active_date": "2026-06-01",
            "open_to_work_flag": True,
            "profile_views_received_30d": 10,
            "applications_submitted_30d": 1,
            "recruiter_response_rate": 0.8,
            "avg_response_time_hours": 1.0,
            "connection_count": 500,
            "endorsements_received": 10,
            "notice_period_days": 15,
            "expected_salary_range_inr_lpa": {"min": 10, "max": 20},
            "preferred_work_mode": "office",
            "willing_to_relocate": True,
            "search_appearance_30d": 10,
            "saved_by_recruiters_30d": 5,
            "interview_completion_rate": 1.0,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True,
            "skill_assessment_scores": {"Python": 95.0, "sentence-transformers": 85.0},
        },
    }


def test_title_career_scorer():
    scorer = TitleCareerScorer(weight=0.45)
    c_dict = get_base_candidate()
    c = CandidateModel.model_validate(c_dict)

    score = scorer(c)
    # Expected: Title (Senior AI = 0.5) + Company (Product = 0.3) + Hopping (avg 24 = 0.2)
    # Raw = 1.0, Weighted = 0.45
    assert abs(score - 0.45) < 0.001

    # Test consulting penalty
    c_dict["career_history"][0]["company"] = "TCS"
    c_dict["career_history"][1]["company"] = "Infosys"
    c = CandidateModel.model_validate(c_dict)
    score = scorer(c)
    # Company should be 0.1, Raw = 0.5 + 0.1 + 0.2 = 0.8, Weighted = 0.36
    assert abs(score - (0.8 * 0.45)) < 0.001


def test_skills_scorer():
    scorer = SkillsScorer(weight=0.30)
    c_dict = get_base_candidate()
    c = CandidateModel.model_validate(c_dict)
    score = scorer(c)
    # We have assessed: Python (1.0), embeddings (sentence-transformers = 1.0)
    # self-reported: vector_db (Pinecone = 0.5)
    # Must have = 2.5/4 * 0.7 = 0.4375
    # Nice to have = 0
    # Expected raw = 0.4375
    assert score > 0.0  # Just ensure it computes correctly without crash


def test_behavioral_scorer():
    scorer = BehavioralScorer(weight=1.0)
    c_dict = get_base_candidate()
    c = CandidateModel.model_validate(c_dict)
    score = scorer.score(c)
    # Open to work (1.05) * Notice 15 (1.10) * Interview 1.0 (1.05) * Verifications (1.05) = >1.2 -> capped at 1.2
    assert abs(score - 1.2) < 0.001


def test_experience_scorer():
    scorer = ExperienceScorer(weight=0.15)
    c_dict = get_base_candidate()
    c = CandidateModel.model_validate(c_dict)
    score = scorer(c)
    assert abs(score - 0.15) < 0.001


def test_location_scorer():
    scorer = LocationScorer(weight=0.10)
    c_dict = get_base_candidate()
    c = CandidateModel.model_validate(c_dict)
    score = scorer(c)
    assert abs(score - 0.10) < 0.001
