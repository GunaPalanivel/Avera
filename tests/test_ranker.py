from src.parsers.jd_parser import JobRequirements


def get_dummy_reqs() -> JobRequirements:
    return JobRequirements(
        raw_text="",
        must_have_skills=("python",),
        nice_to_have_skills=(),
        title_keywords=("ai", "ml"),
        target_cities=("pune",),
        red_flags=(),
    )
