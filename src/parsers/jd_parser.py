"""Job description requirements derived from bundled Track 01 role."""

from dataclasses import dataclass


@dataclass(frozen=True)
class JobRequirements:
    must_have_skills: tuple[str, ...]
    nice_to_have_skills: tuple[str, ...]
    title_keywords: tuple[str, ...]
    red_flags: tuple[str, ...]


# Calibrated to Senior AI Engineer JD (see idea/ProcessedData/docx_extracts/job_description.txt)
DEFAULT_JD = JobRequirements(
    must_have_skills=(
        "python",
        "machine learning",
        "pytorch",
        "llm",
        "nlp",
    ),
    nice_to_have_skills=(
        "rag",
        "vector",
        "production",
        "deployed",
    ),
    title_keywords=(
        "ai",
        "ml",
        "machine learning",
        "llm",
        "nlp",
        "data scientist",
    ),
    red_flags=(
        "fictional",
        "consulting only",
    ),
)


# TODO: parse idea/ProcessedData/docx_extracts/job_description.txt; static tuple fine for foundation milestone
def load_job_requirements() -> JobRequirements:
    return DEFAULT_JD
