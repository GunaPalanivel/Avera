import pytest
from src.detectors.honeypot_detector import is_honeypot
from src.models import CandidateModel

def test_honeypot_fictional_company():
    c = CandidateModel.model_validate({
        "candidate_id": "CAND_0000001",
        "profile": {
            "anonymized_name": "Test", "headline": "Test", "summary": "Test",
            "location": "Test", "country": "Test", "years_of_experience": 5,
            "current_title": "AI Engineer", "current_company": "Stark Industries",
            "current_company_size": "1-10", "current_industry": "Tech"
        },
        "career_history": [
            {
                "company": "Stark Industries", "title": "AI Engineer",
                "start_date": "2020", "duration_months": 12, "is_current": True,
                "industry": "Tech", "company_size": "1-10", "description": "Test"
            }
        ],
        "redrob_signals": {
            "profile_completeness_score": 100, "signup_date": "2020", "last_active_date": "2020",
            "open_to_work_flag": True, "profile_views_received_30d": 1,
            "applications_submitted_30d": 1, "recruiter_response_rate": 1.0,
            "avg_response_time_hours": 1.0, "connection_count": 1,
            "endorsements_received": 1, "notice_period_days": 1,
            "expected_salary_range_inr_lpa": {"min": 1, "max": 2},
            "preferred_work_mode": "office", "willing_to_relocate": True,
            "search_appearance_30d": 1, "saved_by_recruiters_30d": 1,
            "interview_completion_rate": 1.0, "verified_email": True,
            "verified_phone": True, "linkedin_connected": True
        }
    })
    assert is_honeypot(c) == True

def test_honeypot_marketing_trap():
    c = CandidateModel.model_validate({
        "candidate_id": "CAND_0000002",
        "profile": {
            "anonymized_name": "Test", "headline": "Test", "summary": "Test",
            "location": "Test", "country": "Test", "years_of_experience": 5,
            "current_title": "Marketing Manager", "current_company": "Real Corp",
            "current_company_size": "1-10", "current_industry": "Tech"
        },
        "career_history": [
            {
                "company": "Real Corp", "title": "Marketing Manager",
                "start_date": "2020", "duration_months": 12, "is_current": True,
                "industry": "Tech", "company_size": "1-10", "description": "Test"
            }
        ],
        "skills": [
            {
                "name": "Machine Learning", "proficiency": "advanced",
                "endorsements": 10, "duration_months": 24
            }
        ],
        "redrob_signals": {
            "profile_completeness_score": 100, "signup_date": "2020", "last_active_date": "2020",
            "open_to_work_flag": True, "profile_views_received_30d": 1,
            "applications_submitted_30d": 1, "recruiter_response_rate": 1.0,
            "avg_response_time_hours": 1.0, "connection_count": 1,
            "endorsements_received": 1, "notice_period_days": 1,
            "expected_salary_range_inr_lpa": {"min": 1, "max": 2},
            "preferred_work_mode": "office", "willing_to_relocate": True,
            "search_appearance_30d": 1, "saved_by_recruiters_30d": 1,
            "interview_completion_rate": 1.0, "verified_email": True,
            "verified_phone": True, "linkedin_connected": True
        }
    })
    assert is_honeypot(c) == True

def test_not_honeypot():
    c = CandidateModel.model_validate({
        "candidate_id": "CAND_0000003",
        "profile": {
            "anonymized_name": "Test", "headline": "Test", "summary": "Test",
            "location": "Test", "country": "Test", "years_of_experience": 5,
            "current_title": "AI Engineer", "current_company": "Real Corp",
            "current_company_size": "1-10", "current_industry": "Tech"
        },
        "career_history": [
            {
                "company": "Real Corp", "title": "AI Engineer",
                "start_date": "2020", "duration_months": 12, "is_current": True,
                "industry": "Tech", "company_size": "1-10", "description": "Test"
            }
        ],
        "skills": [
            {
                "name": "Machine Learning", "proficiency": "advanced",
                "endorsements": 10, "duration_months": 24
            }
        ],
        "redrob_signals": {
            "profile_completeness_score": 100, "signup_date": "2020", "last_active_date": "2020",
            "open_to_work_flag": True, "profile_views_received_30d": 1,
            "applications_submitted_30d": 1, "recruiter_response_rate": 1.0,
            "avg_response_time_hours": 1.0, "connection_count": 1,
            "endorsements_received": 1, "notice_period_days": 1,
            "expected_salary_range_inr_lpa": {"min": 1, "max": 2},
            "preferred_work_mode": "office", "willing_to_relocate": True,
            "search_appearance_30d": 1, "saved_by_recruiters_30d": 1,
            "interview_completion_rate": 1.0, "verified_email": True,
            "verified_phone": True, "linkedin_connected": True
        }
    })
    assert is_honeypot(c) == False
