"""Job description requirements derived from free-text JD input."""

import re
from dataclasses import dataclass
from pathlib import Path

from src.config import (
    JD_CITY_CATALOG,
    TITLE_KEYWORDS_DEFAULT,
    detect_domain,
    get_skill_taxonomy,
)

_SENIORITY_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\b(principal|staff|distinguished)\b", "staff"),
    (r"\b(senior|sr\.?)\b", "senior"),
    (r"\b(lead|leading)\b", "lead"),
    (r"\b(junior|jr\.?|entry[- ]level|graduate)\b", "junior"),
    (r"\b(mid[- ]level|intermediate)\b", "mid"),
)

_TITLE_LINE_RE = re.compile(
    r"^(?:job\s*title|role|position)\s*[:\-]\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)

_BULLET_SKILL_RE = re.compile(
    r"[\u2022\-\*]\s*([A-Za-z0-9][A-Za-z0-9\s\+\#\/\.\-]{1,48})",
)


@dataclass(frozen=True)
class JobRequirements:
    raw_text: str
    must_have_skills: tuple[str, ...]
    nice_to_have_skills: tuple[str, ...]
    title_keywords: tuple[str, ...]
    target_cities: tuple[str, ...]
    red_flags: tuple[str, ...]
    seniority_level: str = "senior"
    domain: str = "ai_ml"


def _detect_seniority(text_lower: str) -> str:
    for pattern, level in _SENIORITY_PATTERNS:
        if re.search(pattern, text_lower):
            return level
    return "senior"


def _extract_title_keywords(text: str, text_lower: str) -> tuple[str, ...]:
    keywords: set[str] = set()
    match = _TITLE_LINE_RE.search(text)
    if match:
        title_line = match.group(1).lower()
        for token in re.findall(r"[a-z][a-z0-9\+\#]{1,}", title_line):
            if len(token) > 2:
                keywords.add(token)
    else:
        first_line = text.strip().splitlines()[0].lower() if text.strip() else ""
        for token in re.findall(r"[a-z][a-z0-9\+\#]{1,}", first_line):
            if len(token) > 2:
                keywords.add(token)

    for phrase in TITLE_KEYWORDS_DEFAULT:
        if phrase in text_lower:
            keywords.add(phrase)

    for phrase in ("devops", "sre", "machine learning", "data scientist", "sales", "kubernetes", "aws"):
        if phrase in text_lower:
            keywords.add(phrase)

    return tuple(sorted(keywords)) if keywords else TITLE_KEYWORDS_DEFAULT


def _taxonomy_skills(text_lower: str, domain: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    must_taxonomy, nice_taxonomy = get_skill_taxonomy(domain)
    must = {sk for sk in must_taxonomy if sk in text_lower}
    nice = {sk for sk in nice_taxonomy if sk in text_lower}
    return tuple(sorted(must)), tuple(sorted(nice))


def _bullet_skills(text: str) -> set[str]:
    found: set[str] = set()
    tech_tokens = (
        "docker",
        "kubernetes",
        "terraform",
        "aws",
        "prometheus",
        "grafana",
        "python",
        "linux",
        "jenkins",
        "gitlab",
    )
    text_lower = text.lower()
    for token in tech_tokens:
        if token in text_lower:
            found.add(token)
    for raw in _BULLET_SKILL_RE.findall(text):
        token = raw.strip().lower()
        if token in tech_tokens:
            found.add(token)
    return found


def load_job_requirements(jd_path: Path | str | None = None) -> JobRequirements:
    if not jd_path:
        jd_path = Path("DataSet/job_description.txt")

    path = Path(jd_path)
    if not path.exists():
        text = "AI Engineer Machine Learning LLM NLP Python PyTorch embeddings vector database"
    else:
        text = path.read_text(encoding="utf-8")

    text_lower = text.lower()
    seniority = _detect_seniority(text_lower)
    domain = detect_domain(text_lower)
    must_have, nice_to_have = _taxonomy_skills(text_lower, domain)

    bullet = _bullet_skills(text)
    if bullet:
        must_have = tuple(sorted(set(must_have) | bullet))

    target_cities = tuple(c for c in JD_CITY_CATALOG if c in text_lower)
    title_keywords = _extract_title_keywords(text, text_lower)

    return JobRequirements(
        raw_text=text,
        must_have_skills=must_have,
        nice_to_have_skills=nice_to_have,
        title_keywords=title_keywords,
        target_cities=target_cities,
        red_flags=("fictional", "consulting only"),
        seniority_level=seniority,
        domain=domain,
    )
