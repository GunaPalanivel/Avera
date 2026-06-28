"""Job description requirements derived from bundled Track 01 role."""

from dataclasses import dataclass
from pathlib import Path

from src.config import (
    JD_CITY_CATALOG,
    SKILL_TAXONOMY_MUST,
    SKILL_TAXONOMY_NICE,
    TITLE_KEYWORDS_DEFAULT,
)


@dataclass(frozen=True)
class JobRequirements:
    raw_text: str
    must_have_skills: tuple[str, ...]
    nice_to_have_skills: tuple[str, ...]
    title_keywords: tuple[str, ...]
    target_cities: tuple[str, ...]
    red_flags: tuple[str, ...]


def load_job_requirements(jd_path: Path | str | None = None) -> JobRequirements:
    if not jd_path:
        jd_path = Path("DataSet/job_description.txt")

    path = Path(jd_path)
    if not path.exists():
        text = "AI Engineer Machine Learning LLM NLP Python PyTorch embeddings vector database"
    else:
        text = path.read_text(encoding="utf-8")

    text_lower = text.lower()

    must_have = tuple(sk for sk in sorted(SKILL_TAXONOMY_MUST) if sk in text_lower)
    nice_to_have = tuple(sk for sk in sorted(SKILL_TAXONOMY_NICE) if sk in text_lower)
    target_cities = tuple(c for c in JD_CITY_CATALOG if c in text_lower)

    return JobRequirements(
        raw_text=text,
        must_have_skills=must_have,
        nice_to_have_skills=nice_to_have,
        title_keywords=TITLE_KEYWORDS_DEFAULT,
        target_cities=target_cities,
        red_flags=("fictional", "consulting only"),
    )
