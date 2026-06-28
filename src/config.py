"""JD-backed weights, company lists, and scoring constants validated at import."""

import os

from src.exceptions import ConfigError

# Base scorer weights; behavioral is a multiplicative modifier (ADR-03)
SCORER_WEIGHTS: dict[str, float] = {
    "title_career": 0.35,
    "skills": 0.25,
    "experience": 0.15,
    "location": 0.10,
    "semantic": 0.15,
}

BEHAVIORAL_MODIFIER_MIN = 0.4
BEHAVIORAL_MODIFIER_MAX = 1.3

# Skip expensive embedding when heuristic base is too weak to reach top-100
SEMANTIC_MIN_HEURISTIC_SCORE = 0.06

# Offline-friendly: set AVERA_SEMANTIC_MODEL to a local directory path after `make download-model`
SEMANTIC_MODEL_NAME = os.environ.get("AVERA_SEMANTIC_MODEL", "all-MiniLM-L6-v2")

# ~60% of the pool is fictional companies (ADR-02)
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

CONSULTING_FIRMS: frozenset[str] = frozenset({"tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini", "ibm"})

JD_CITY_CATALOG: tuple[str, ...] = (
    "hyderabad",
    "pune",
    "mumbai",
    "delhi ncr",
    "delhi",
    "noida",
    "gurgaon",
    "gurugram",
    "bangalore",
    "bengaluru",
)

AI_TITLE_TIERS: dict[str, float] = {
    "senior ai engineer": 1.0,
    "staff ml engineer": 1.0,
    "principal ml engineer": 1.0,
    "lead ai engineer": 0.95,
    "machine learning engineer": 0.85,
    "ml engineer": 0.85,
    "ai engineer": 0.8,
    "data scientist": 0.75,
    "backend engineer": 0.5,
}

SKILL_TAXONOMY_MUST: frozenset[str] = frozenset(
    {
        "embeddings",
        "sentence-transformers",
        "bge",
        "e5",
        "pinecone",
        "weaviate",
        "qdrant",
        "milvus",
        "opensearch",
        "elasticsearch",
        "faiss",
        "vector database",
        "python",
        "ndcg",
        "mrr",
        "map",
        "evaluation",
        "a/b test",
        "llm",
        "nlp",
        "pytorch",
        "machine learning",
    }
)

SKILL_TAXONOMY_NICE: frozenset[str] = frozenset({"lora", "qlora", "peft", "xgboost", "learning to rank", "ltr", "rag", "vector"})

SKILL_SYNONYMS: dict[str, tuple[str, ...]] = {
    "vector database": ("vector db", "vector search", "vector store", "ann index"),
    "sentence-transformers": ("sentence transformers", "sbert", "minilm"),
    "machine learning": ("ml", "applied ml"),
    "llm": ("large language model", "language model"),
    "faiss": ("facebook ai similarity search",),
}

TITLE_KEYWORDS_DEFAULT: tuple[str, ...] = (
    "ai",
    "ml",
    "machine learning",
    "llm",
    "nlp",
    "data scientist",
)

MAX_JSONL_BYTES = 2 * 1024 * 1024 * 1024
MAX_JSONL_LINE_BYTES = 10 * 1024 * 1024

_weight_sum = sum(SCORER_WEIGHTS.values())
if abs(_weight_sum - 1.0) > 1e-6:
    raise ConfigError(f"Scorer weights must sum to 1.0, got {_weight_sum}")

if not FICTIONAL_COMPANIES:
    raise ConfigError("FICTIONAL_COMPANIES must not be empty")
if not AI_TITLE_TIERS:
    raise ConfigError("AI_TITLE_TIERS must not be empty")


def expand_skill_keyword(keyword: str) -> frozenset[str]:
    """Return keyword plus known synonyms for deterministic skill matching."""
    kw = keyword.lower().strip()
    variants: set[str] = {kw}
    for canonical, syns in SKILL_SYNONYMS.items():
        if kw == canonical or kw in syns:
            variants.add(canonical)
            variants.update(syns)
    return frozenset(variants)
