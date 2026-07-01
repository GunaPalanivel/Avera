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


def test_jd_domain_detection():
    ai_req = load_job_requirements(Path("DataSet/job_description.txt"))
    assert ai_req.domain == "ai_ml"

    devops_req = load_job_requirements(Path("DataSet/job_description_devops.txt"))
    assert devops_req.domain == "devops"


def test_generic_domain_injects_no_taxonomy():
    from src.config import get_skill_taxonomy, get_title_tiers

    must, nice = get_skill_taxonomy("generic")
    assert must == frozenset()
    assert nice == frozenset()
    assert get_title_tiers("generic") == {}


def test_bullet_skills_no_substring_leak():
    # "going"/"Google"/"trust" must not leak "go"/"rust" into must-have skills
    req = load_job_requirements(Path("DataSet/job_description.txt"))
    assert "go" not in req.must_have_skills
    assert "rust" not in req.must_have_skills


def test_bullet_skills_real_token_still_extracted(tmp_path):
    from src.parsers.jd_parser import _bullet_skills

    jd = "Senior Engineer\nMust have:\n- Go\n- Rust\n- Kubernetes\n"
    found = _bullet_skills(jd)
    assert "go" in found
    assert "rust" in found
    assert "kubernetes" in found
