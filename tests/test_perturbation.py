from src.models import CandidateModel


def test_proficiency_change_does_not_break_validation():
    """Small field edits should still validate (perturbation sanity)."""
    base = {
        "candidate_id": "CAND_0000099",
        "profile": {
            "anonymized_name": "Test",
            "headline": "ML Engineer",
            "summary": "Summary text.",
            "location": "City",
            "country": "India",
            "years_of_experience": 4.0,
            "current_title": "ML Engineer",
            "current_company": "Co",
            "current_company_size": "501-1000",
            "current_industry": "Software",
        },
        "career_history": [
            {
                "company": "Co",
                "title": "ML Engineer",
                "start_date": "2021-01-01",
                "end_date": None,
                "duration_months": 48,
                "is_current": True,
                "industry": "Software",
                "company_size": "501-1000",
                "description": "Built models.",
            }
        ],
        "education": [],
        "skills": [
            {"name": "Python", "proficiency": "advanced", "endorsements": 5},
        ],
        "redrob_signals": {
            "profile_completeness_score": 80.0,
            "signup_date": "2022-01-01",
            "last_active_date": "2024-01-01",
            "open_to_work_flag": True,
            "profile_views_received_30d": 1,
            "applications_submitted_30d": 0,
            "recruiter_response_rate": 0.5,
            "avg_response_time_hours": 2.0,
            "skill_assessment_scores": {},
            "connection_count": 10,
            "endorsements_received": 5,
            "notice_period_days": 30,
            "expected_salary_range_inr_lpa": {"min": 10.0, "max": 20.0},
            "preferred_work_mode": "remote",
            "willing_to_relocate": False,
            "github_activity_score": 10.0,
            "search_appearance_30d": 1,
            "saved_by_recruiters_30d": 0,
            "interview_completion_rate": 0.5,
            "offer_acceptance_rate": 0.5,
            "verified_email": True,
            "verified_phone": False,
            "linkedin_connected": False,
        },
    }
    m1 = CandidateModel.model_validate(base)
    tweaked = dict(base)
    tweaked["skills"] = [
        {"name": "Python", "proficiency": "expert", "endorsements": 5},
    ]
    m2 = CandidateModel.model_validate(tweaked)
    assert m1.candidate_id == m2.candidate_id
    assert m1.skills[0].proficiency != m2.skills[0].proficiency
