from pathlib import Path

from src.parsers.jd_parser import load_job_requirements


def test_load_job_requirements_has_must_have_skills():
    req = load_job_requirements()
    assert len(req.must_have_skills) > 0
    assert "python" in req.must_have_skills


def test_load_job_requirements_has_nice_to_have_and_red_flags():
    req = load_job_requirements()
    assert len(req.nice_to_have_skills) > 0
    assert len(req.red_flags) > 0
    assert len(req.title_keywords) > 0
    assert req.seniority_level in ("senior", "staff", "lead", "mid", "junior")


def test_devops_jd_extracts_infra_skills():
    jd = Path("DataSet/job_description_devops.txt")
    req = load_job_requirements(jd)
    assert "python" in req.must_have_skills
    assert "devops" in req.title_keywords
    assert "kubernetes" in req.title_keywords or "aws" in req.title_keywords
    assert req.seniority_level == "senior"
