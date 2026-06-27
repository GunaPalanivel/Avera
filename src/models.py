"""Pydantic models for candidate JSONL boundary validation."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class SkillModel(BaseModel):
    name: str = Field(max_length=200)
    proficiency: str = Field(pattern=r"^(beginner|intermediate|advanced|expert)$")
    endorsements: int = Field(ge=0)
    duration_months: int | None = Field(default=None, ge=0)


class ProfileModel(BaseModel):
    anonymized_name: str = Field(max_length=200)
    headline: str = Field(max_length=500)
    summary: str = Field(max_length=8000)
    location: str = Field(max_length=200)
    country: str = Field(max_length=100)
    years_of_experience: float = Field(ge=0, le=50)
    current_title: str = Field(max_length=200)
    current_company: str = Field(max_length=200)
    current_company_size: str
    current_industry: str = Field(max_length=200)


class CareerEntryModel(BaseModel):
    company: str = Field(max_length=200)
    title: str = Field(max_length=200)
    start_date: str
    end_date: str | None = None
    duration_months: int = Field(ge=0)
    is_current: bool
    industry: str = Field(max_length=200)
    company_size: str
    description: str = Field(max_length=8000)


class EducationModel(BaseModel):
    institution: str = Field(max_length=200)
    degree: str = Field(max_length=100)
    field_of_study: str = Field(max_length=200)
    start_year: int
    end_year: int
    grade: str | None = None
    tier: str | None = None


class SalaryRangeModel(BaseModel):
    min: float = Field(ge=0)
    max: float = Field(ge=0)


class RedrobSignalsModel(BaseModel):
    profile_completeness_score: float = Field(ge=0, le=100)
    signup_date: str
    last_active_date: str
    open_to_work_flag: bool
    profile_views_received_30d: int = Field(ge=0)
    applications_submitted_30d: int = Field(ge=0)
    recruiter_response_rate: float = Field(ge=0, le=1)
    avg_response_time_hours: float = Field(ge=0)
    skill_assessment_scores: dict[str, float] = Field(default_factory=dict)
    connection_count: int = Field(ge=0)
    endorsements_received: int = Field(ge=0)
    notice_period_days: int = Field(ge=0, le=180)
    expected_salary_range_inr_lpa: SalaryRangeModel
    preferred_work_mode: str
    willing_to_relocate: bool
    github_activity_score: float = Field(ge=0, le=100)
    search_appearance_30d: int = Field(ge=0)
    saved_by_recruiters_30d: int = Field(ge=0)
    interview_completion_rate: float = Field(ge=0, le=1)
    offer_acceptance_rate: float = Field(ge=0, le=1)
    verified_email: bool
    verified_phone: bool
    linkedin_connected: bool


class CandidateModel(BaseModel):
    candidate_id: str = Field(pattern=r"^CAND_[0-9]{7}$")
    profile: ProfileModel
    career_history: list[CareerEntryModel] = Field(min_length=1, max_length=10)
    education: list[EducationModel] = Field(default_factory=list, max_length=5)
    skills: list[SkillModel] = Field(default_factory=list)
    redrob_signals: RedrobSignalsModel
    certifications: list[dict[str, Any]] = Field(default_factory=list)
    languages: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("candidate_id")
    @classmethod
    def candidate_id_upper(cls, v: str) -> str:
        return v.strip()
