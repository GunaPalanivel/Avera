"""Job description requirements derived from bundled Track 01 role."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JobRequirements:
    raw_text: str
    must_have_skills: tuple[str, ...]
    nice_to_have_skills: tuple[str, ...]
    title_keywords: tuple[str, ...]
    red_flags: tuple[str, ...]


def load_job_requirements(jd_path: Path | str | None = None) -> JobRequirements:
    if not jd_path:
        jd_path = Path("idea/ProcessedData/docx_extracts/job_description.txt")

    path = Path(jd_path)
    if not path.exists():
        text = "AI Engineer Machine Learning LLM NLP"
    else:
        text = path.read_text(encoding="utf-8")

    # Extract skills by looking for keywords in the JD text
    skill_taxonomy = {
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

    nice_taxonomy = {"lora", "qlora", "peft", "xgboost", "learning to rank", "ltr", "rag", "vector"}

    text_lower = text.lower()

    must_have = tuple(sk for sk in skill_taxonomy if sk in text_lower)
    nice_to_have = tuple(sk for sk in nice_taxonomy if sk in text_lower)

    title_kws = ("ai", "ml", "machine learning", "llm", "nlp", "data scientist")

    return JobRequirements(
        raw_text=text,
        must_have_skills=must_have,
        nice_to_have_skills=nice_to_have,
        title_keywords=title_kws,
        red_flags=("fictional", "consulting only"),
    )
