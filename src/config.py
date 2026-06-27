"""JD-backed weights and company lists validated at import."""

from src.exceptions import ConfigError

# Rule-based weights, no labels to train on; behavioral 25% for JD hireability emphasis
SCORER_WEIGHTS: dict[str, float] = {
    "title_career": 0.35,
    "behavioral": 0.25,
    "skills": 0.20,
    "experience": 0.10,
    "location": 0.10,
}

# ~60% of the pool is fictional companies; honeypot filter uses this in scoring milestone
FICTIONAL_COMPANIES: frozenset[str] = frozenset(
    {
        "Dunder Mifflin",
        "Pawnee Parks Department",
        "Stark Industries",
        "Wayne Enterprises",
        "Wonka Industries",
        "Acme Corp",
        "Hooli",
        "Pied Piper",
        "Globex Inc",
        "Initech",
        "Massive Dynamic",
        "Cyberdyne Systems",
        "Tyrell Corporation",
        "Umbrella Corp",
    }
)

AI_TITLE_TIERS: dict[str, float] = {
    "senior ai engineer": 1.0,
    "staff ml engineer": 1.0,
    "machine learning engineer": 0.85,
    "data scientist": 0.75,
    "backend engineer": 0.5,
}

MAX_JSONL_BYTES = 2 * 1024 * 1024 * 1024  # challenge file cap
MAX_JSONL_LINE_BYTES = 10 * 1024 * 1024  # single-line bomb guard

# Fail fast at import so bad weights never reach a 100K run
_weight_sum = sum(SCORER_WEIGHTS.values())
if abs(_weight_sum - 1.0) > 1e-6:
    raise ConfigError(f"Scorer weights must sum to 1.0, got {_weight_sum}")

if not FICTIONAL_COMPANIES:
    raise ConfigError("FICTIONAL_COMPANIES must not be empty")
if not AI_TITLE_TIERS:
    raise ConfigError("AI_TITLE_TIERS must not be empty")
