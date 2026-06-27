"""JD-backed weights and company lists validated at import."""

from src.exceptions import ConfigError

SCORER_WEIGHTS: dict[str, float] = {
    "title_career": 0.35,
    "behavioral": 0.25,
    "skills": 0.20,
    "experience": 0.10,
    "location": 0.10,
}

FICTIONAL_COMPANIES: frozenset[str] = frozenset(
    {
        "Dunder Mifflin",
        "Pawnee Parks Department",
        "Stark Industries",
        "Wayne Enterprises",
        "Wonka Industries",
        "Acme Corp",
    }
)

AI_TITLE_TIERS: dict[str, float] = {
    "senior ai engineer": 1.0,
    "staff ml engineer": 1.0,
    "machine learning engineer": 0.85,
    "data scientist": 0.75,
    "backend engineer": 0.5,
}

MAX_JSONL_BYTES = 2 * 1024 * 1024 * 1024
MAX_JSONL_LINE_BYTES = 10 * 1024 * 1024

_weight_sum = sum(SCORER_WEIGHTS.values())
if abs(_weight_sum - 1.0) > 1e-6:
    raise ConfigError(f"Scorer weights must sum to 1.0, got {_weight_sum}")

if not FICTIONAL_COMPANIES:
    raise ConfigError("FICTIONAL_COMPANIES must not be empty")
if not AI_TITLE_TIERS:
    raise ConfigError("AI_TITLE_TIERS must not be empty")
