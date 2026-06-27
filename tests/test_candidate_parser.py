from pathlib import Path

from src.parsers.candidate_parser import count_candidates, stream_candidates

FIXTURE = Path("tests/fixtures/sample.jsonl")


def test_stream_candidates_reads_fixture():
    ids = [c.candidate_id for c in stream_candidates(FIXTURE)]
    assert len(ids) >= 1
    assert ids[0].startswith("CAND_")


def test_count_candidates_with_limit():
    assert count_candidates(FIXTURE, limit=1) == 1


def test_skips_blank_lines(tmp_path):
    p = tmp_path / "blank.jsonl"
    p.write_text("\n\n", encoding="utf-8")
    assert count_candidates(p) == 0
