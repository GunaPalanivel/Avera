from pathlib import Path

from src.config import SCORER_WEIGHTS
from src.parsers.candidate_parser import stream_candidates

FIXTURE = Path("tests/fixtures/sample.jsonl")


def test_parser_yields_same_order_on_repeat():
    first = [c.candidate_id for c in stream_candidates(FIXTURE)]
    second = [c.candidate_id for c in stream_candidates(FIXTURE)]
    assert first == second


def test_scorer_weights_stable():
    assert abs(sum(SCORER_WEIGHTS.values()) - 1.0) < 1e-6
