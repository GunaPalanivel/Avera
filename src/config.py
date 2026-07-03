"""JD-backed weights, company lists, and scoring constants validated at import."""

import os

from src.exceptions import ConfigError

# Base scorer weights; behavioral is a multiplicative modifier (ADR-03)
SCORER_WEIGHTS: dict[str, float] = {
    "title_career": 0.18,
    "skills": 0.14,
    "experience": 0.11,
    "location": 0.06,
    "semantic": 0.25,
    "education": 0.12,
    "trajectory": 0.14,
}

BEHAVIORAL_MODIFIER_MIN = 0.4
BEHAVIORAL_MODIFIER_MAX = 1.3

# Skip expensive embedding when heuristic base is too weak to reach top-100
# Tuned above sample P10 (~0.105) so gate drops weak heuristic profiles before batch embed
SEMANTIC_MIN_HEURISTIC_SCORE = 0.11

# Two-stage funnel: only embed the strongest heuristic candidates (candidate generation ->
# semantic rerank). Generous default keeps the top-100 effectively unchanged while cutting
# the encode workload from all survivors to K. Override with AVERA_SEMANTIC_RERANK_TOPK.
SEMANTIC_RERANK_TOPK = int(os.environ.get("AVERA_SEMANTIC_RERANK_TOPK", "5000"))

# Cross-encoder rerank: after the heap yields a shortlist pool, a cross-encoder re-scores the
# pool and nudges the final order. The blend is additive and bounded (final = base + alpha * ce),
# so monotonicity and the reasoning floor are preserved. Only runs on full ranking passes.
RERANK_POOL_SIZE = int(os.environ.get("AVERA_RERANK_POOL", "300"))
RERANK_ALPHA = float(os.environ.get("AVERA_RERANK_ALPHA", "0.15"))
CROSS_ENCODER_MODEL_NAME = os.environ.get("AVERA_CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

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

# Anti-requirement detection: the JD's "Things we explicitly do NOT want" section names
# candidates whose primary expertise is CV/speech/robotics without NLP/IR exposure.
CV_SPEECH_ROBOTICS_TERMS: frozenset[str] = frozenset(
    {
        "computer vision",
        "opencv",
        "image classification",
        "object detection",
        "yolo",
        "cnn",
        "segmentation",
        "image segmentation",
        "speech recognition",
        "asr",
        "tts",
        "robotics",
        "slam",
        "diffusion models",
        "gans",
    }
)

NLP_IR_TERMS: frozenset[str] = frozenset(
    {
        "nlp",
        "llm",
        "llms",
        "embeddings",
        "retrieval",
        "information retrieval",
        "semantic search",
        "vector search",
        "rag",
        "sentence transformers",
        "bert",
        "transformers",
        "fine-tuning llms",
    }
)

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
        "pgvector",
        "haystack",
        "information retrieval",
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

# Domain-specific taxonomies keep the engine JD-agnostic instead of AI/ML-only (see ADR-17)
DEVOPS_TITLE_TIERS: dict[str, float] = {
    "senior devops engineer": 1.0,
    "staff site reliability engineer": 1.0,
    "principal sre": 1.0,
    "site reliability engineer": 0.95,
    "senior sre": 0.95,
    "devops engineer": 0.9,
    "platform engineer": 0.9,
    "sre": 0.9,
    "infrastructure engineer": 0.85,
    "cloud engineer": 0.8,
    "systems engineer": 0.7,
    "backend engineer": 0.5,
}

DEVOPS_SKILL_TAXONOMY_MUST: frozenset[str] = frozenset(
    {
        "aws",
        "docker",
        "kubernetes",
        "terraform",
        "ci/cd",
        "jenkins",
        "gitlab",
        "prometheus",
        "grafana",
        "linux",
        "python",
        "ansible",
        "cloudformation",
        "observability",
        "helm",
    }
)

DEVOPS_SKILL_TAXONOMY_NICE: frozenset[str] = frozenset({"datadog", "eks", "ecs", "vault", "sast", "incident response", "on-call", "gpu", "secrets management"})

AI_ML_DOMAIN_KEYWORDS: tuple[str, ...] = (
    "machine learning",
    "ml engineer",
    "ai engineer",
    "embeddings",
    "retrieval",
    "ranking",
    "llm",
    "nlp",
    "data scientist",
    "fine-tuning",
    "vector",
)

DEVOPS_DOMAIN_KEYWORDS: tuple[str, ...] = (
    "devops",
    "sre",
    "site reliability",
    "kubernetes",
    "terraform",
    "ci/cd",
    "observability",
    "infrastructure",
    "cloud infrastructure",
    "prometheus",
)


def detect_domain(text_lower: str) -> str:
    """Classify a JD by keyword prevalence so scorers can branch taxonomy (ADR-17)."""
    ai_hits = sum(text_lower.count(kw) for kw in AI_ML_DOMAIN_KEYWORDS)
    devops_hits = sum(text_lower.count(kw) for kw in DEVOPS_DOMAIN_KEYWORDS)
    if devops_hits > ai_hits and devops_hits >= 2:
        return "devops"
    if ai_hits >= 2:
        return "ai_ml"
    return "generic"


def get_title_tiers(domain: str) -> dict[str, float]:
    """Title tier table for the JD domain. Generic JDs get no title-tier bias (empty table)."""
    if domain == "devops":
        return DEVOPS_TITLE_TIERS
    if domain == "generic":
        return {}
    return AI_TITLE_TIERS


def get_skill_taxonomy(domain: str) -> tuple[frozenset[str], frozenset[str]]:
    """Return (must, nice) skill taxonomies for the JD domain. Generic JDs inject no taxonomy."""
    if domain == "devops":
        return DEVOPS_SKILL_TAXONOMY_MUST, DEVOPS_SKILL_TAXONOMY_NICE
    if domain == "generic":
        return frozenset(), frozenset()
    return SKILL_TAXONOMY_MUST, SKILL_TAXONOMY_NICE


SKILL_SYNONYMS: dict[str, tuple[str, ...]] = {
    "vector database": ("vector db", "vector search", "vector store", "ann index", "pgvector"),
    "sentence-transformers": ("sentence transformers", "sbert", "minilm"),
    "machine learning": ("ml", "applied ml"),
    "llm": ("large language model", "language model"),
    "faiss": ("facebook ai similarity search",),
    "embeddings": ("vector representations", "text encoders", "embedding model"),
    "nlp": ("natural language processing", "information retrieval"),
    "haystack": ("deepset haystack",),
}

SKILL_ADJACENCIES: dict[str, tuple[str, ...]] = {
    "pinecone": ("weaviate", "milvus", "qdrant", "faiss", "pgvector", "opensearch", "elasticsearch"),
    "weaviate": ("pinecone", "milvus", "qdrant", "faiss", "pgvector"),
    "qdrant": ("pinecone", "weaviate", "milvus", "faiss", "pgvector"),
    "milvus": ("pinecone", "weaviate", "qdrant", "faiss", "pgvector"),
    "faiss": ("pinecone", "weaviate", "qdrant", "milvus", "pgvector"),
    "pgvector": ("pinecone", "weaviate", "milvus", "qdrant", "faiss"),
    "opensearch": ("elasticsearch", "pinecone", "weaviate"),
    "elasticsearch": ("opensearch", "pinecone", "weaviate"),
    "vector database": ("pgvector", "pinecone", "weaviate", "milvus", "qdrant", "faiss"),
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
if not DEVOPS_TITLE_TIERS:
    raise ConfigError("DEVOPS_TITLE_TIERS must not be empty")


def get_scorer_weights(seniority_level: str) -> dict[str, float]:
    """JD-derived weight profiles; behavioral remains a separate multiplier (ADR-03)."""
    level = (seniority_level or "mid").lower()
    if level in ("senior", "staff", "principal", "lead"):
        return {
            "title_career": 0.18,
            "skills": 0.14,
            "experience": 0.11,
            "location": 0.06,
            "semantic": 0.25,
            "education": 0.12,
            "trajectory": 0.14,
        }
    if level in ("junior", "entry", "associate"):
        return {
            "title_career": 0.10,
            "skills": 0.22,
            "experience": 0.11,
            "location": 0.06,
            "semantic": 0.25,
            "education": 0.12,
            "trajectory": 0.14,
        }
    return {
        "title_career": 0.16,
        "skills": 0.16,
        "experience": 0.11,
        "location": 0.06,
        "semantic": 0.25,
        "education": 0.12,
        "trajectory": 0.14,
    }


def expand_skill_keyword(keyword: str) -> frozenset[str]:
    """Return keyword plus known synonyms for deterministic skill matching."""
    kw = keyword.lower().strip()
    variants: set[str] = {kw}
    for canonical, syns in SKILL_SYNONYMS.items():
        if kw == canonical or kw in syns:
            variants.add(canonical)
            variants.update(syns)
    return frozenset(variants)


def expand_skill_adjacency(keyword: str) -> frozenset[str]:
    """Return adjacent skill tokens for partial must-have credit."""
    kw = keyword.lower().strip()
    adj_keys: set[str] = set()
    for canonical in SKILL_ADJACENCIES:
        if kw == canonical or kw in expand_skill_keyword(canonical):
            adj_keys.add(canonical)
    variants: set[str] = set()
    for key in adj_keys:
        for adj in SKILL_ADJACENCIES[key]:
            variants.add(adj)
            variants.update(expand_skill_keyword(adj))
    return frozenset(variants)
