import json
from pathlib import Path
from unittest.mock import patch

import pytest
from src.exceptions import ConfigError
from src.parsers.candidate_parser import count_candidates, stream_candidates
from tests.test_models import _minimal_candidate_raw

FIXTURE = Path("tests/fixtures/sample.jsonl")


def test_stream_candidates_reads_fixture():
    ids = [c.candidate_id for c in stream_candidates(FIXTURE)]
    assert len(ids) == 2
    assert all(i.startswith("CAND_") for i in ids)


def test_count_candidates_with_limit():
    assert count_candidates(FIXTURE, limit=1) == 1


def test_skips_blank_lines(tmp_path):
    p = tmp_path / "blank.jsonl"
    p.write_text("\n\n", encoding="utf-8")
    assert count_candidates(p) == 0


def test_skips_malformed_json(tmp_path):
    p = tmp_path / "bad.jsonl"
    p.write_text("{not valid json\n", encoding="utf-8")
    assert count_candidates(p) == 0


def test_rejects_oversized_file(tmp_path):
    p = tmp_path / "big.jsonl"
    p.write_text("x" * 20 + "\n", encoding="utf-8")
    with patch("src.parsers.candidate_parser.MAX_JSONL_BYTES", 10):
        with pytest.raises(ConfigError, match="exceeds"):
            count_candidates(p)


def test_skips_oversized_line(tmp_path):
    p = tmp_path / "longline.jsonl"
    p.write_text("x" * 20 + "\n", encoding="utf-8")
    with patch("src.parsers.candidate_parser.MAX_JSONL_LINE_BYTES", 10):
        assert count_candidates(p) == 0


def test_parses_minus_one_sentinel_line(tmp_path):
    p = tmp_path / "sentinel.jsonl"
    row = _minimal_candidate_raw(github_activity_score=-1, offer_acceptance_rate=-1)
    p.write_text(json.dumps(row) + "\n", encoding="utf-8")
    assert count_candidates(p) == 1
