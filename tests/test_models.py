from src.models import CandidateModel


def _minimal_candidate_raw(**signal_overrides):
    signals = {
        "profile_completeness_score": 90.0,
        "signup_date": "2023-01-01",
        "last_active_date": "2024-06-01",
        "open_to_work_flag": True,
        "profile_views_received_30d": 10,
        "applications_submitted_30d": 2,
        "recruiter_response_rate": 0.8,
        "avg_response_time_hours": 4.0,
        "skill_assessment_scores": {"python": 85.0},
        "connection_count": 100,
        "endorsements_received": 20,
        "notice_period_days": 30,
        "expected_salary_range_inr_lpa": {"min": 20.0, "max": 35.0},
        "preferred_work_mode": "hybrid",
        "willing_to_relocate": True,
        "github_activity_score": 50.0,
        "search_appearance_30d": 5,
        "saved_by_recruiters_30d": 1,
        "interview_completion_rate": 0.9,
        "offer_acceptance_rate": 0.8,
        "verified_email": True,
        "verified_phone": True,
        "linkedin_connected": True,
    }
    signals.update(signal_overrides)
    return {
        "candidate_id": "CAND_0000001",
        "profile": {
            "anonymized_name": "Test User",
            "headline": "ML Engineer",
            "summary": "Builds models in production.",
            "location": "Bengaluru",
            "country": "India",
            "years_of_experience": 5.0,
            "current_title": "ML Engineer",
            "current_company": "Example Co",
            "current_company_size": "501-1000",
            "current_industry": "Software",
        },
        "career_history": [
            {
                "company": "Example Co",
                "title": "ML Engineer",
                "start_date": "2022-01-01",
                "end_date": None,
                "duration_months": 36,
                "is_current": True,
                "industry": "Software",
                "company_size": "501-1000",
                "description": "Shipped ranking models.",
            }
        ],
        "education": [],
        "skills": [
            {
                "name": "Python",
                "proficiency": "expert",
                "endorsements": 10,
                "duration_months": 48,
            }
        ],
        "redrob_signals": signals,
    }


def test_candidate_model_accepts_fixture_sample():
    raw = _minimal_candidate_raw()
    model = CandidateModel.model_validate(raw)
    assert model.candidate_id == "CAND_0000001"


def test_missing_sentinel_coerces_to_none():
    model = CandidateModel.model_validate(_minimal_candidate_raw(github_activity_score=-1, offer_acceptance_rate=-1))
    assert model.redrob_signals.github_activity_score is None
    assert model.redrob_signals.offer_acceptance_rate is None


def test_valid_behavioral_scores_unchanged():
    model = CandidateModel.model_validate(
        _minimal_candidate_raw(github_activity_score=42.5, offer_acceptance_rate=0.75)
    )
    assert model.redrob_signals.github_activity_score == 42.5
    assert model.redrob_signals.offer_acceptance_rate == 0.75


def test_invalid_proficiency_rejected():
    raw = {
        "candidate_id": "CAND_0000002",
        "profile": {
            "anonymized_name": "X",
            "headline": "h",
            "summary": "s",
            "location": "l",
            "country": "c",
            "years_of_experience": 1.0,
            "current_title": "t",
            "current_company": "co",
            "current_company_size": "1-10",
            "current_industry": "i",
        },
        "career_history": [
            {
                "company": "co",
                "title": "t",
                "start_date": "2020-01-01",
                "end_date": None,
                "duration_months": 12,
                "is_current": True,
                "industry": "i",
                "company_size": "1-10",
                "description": "d",
            }
        ],
        "education": [],
        "skills": [
            {"name": "Py", "proficiency": "godmode", "endorsements": 0},
        ],
        "redrob_signals": {
            "profile_completeness_score": 1.0,
            "signup_date": "2020-01-01",
            "last_active_date": "2020-02-01",
            "open_to_work_flag": False,
            "profile_views_received_30d": 0,
            "applications_submitted_30d": 0,
            "recruiter_response_rate": 0.0,
            "avg_response_time_hours": 0.0,
            "skill_assessment_scores": {},
            "connection_count": 0,
            "endorsements_received": 0,
            "notice_period_days": 0,
            "expected_salary_range_inr_lpa": {"min": 0.0, "max": 0.0},
            "preferred_work_mode": "remote",
            "willing_to_relocate": False,
            "github_activity_score": 0.0,
            "search_appearance_30d": 0,
            "saved_by_recruiters_30d": 0,
            "interview_completion_rate": 0.0,
            "offer_acceptance_rate": 0.0,
            "verified_email": False,
            "verified_phone": False,
            "linkedin_connected": False,
        },
    }
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CandidateModel.model_validate(raw)
