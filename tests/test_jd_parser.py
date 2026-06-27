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
