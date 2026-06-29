import hashlib
from pathlib import Path

from src.parsers.candidate_parser import stream_candidates
from src.parsers.jd_parser import load_job_requirements
from src.ranker import Ranker


def _run_rank_hash(limit: int = 5) -> str:
    fixture = Path("tests/fixtures/sample.jsonl")
    ranker = Ranker(load_job_requirements())
    results = ranker.rank(stream_candidates(fixture, limit=limit), top_k=limit, require_exact_count=False)
    payload = "|".join(f"{c.candidate_id}:{score:.4f}" for score, c, _ in results)
    return hashlib.sha256(payload.encode()).hexdigest()


def test_ranking_is_deterministic_on_fixture():
    assert _run_rank_hash() == _run_rank_hash()
