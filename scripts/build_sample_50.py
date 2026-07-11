#!/usr/bin/env python3
"""Build a 50-candidate sandbox sample from the curated demo JSONL."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "DataSet" / "sample_candidates_demo.jsonl"
OUTPUT = REPO / "DataSet" / "sample_candidates_50.jsonl"
LIMIT = 50


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit(f"Missing source file: {SOURCE}")

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    if len(lines) < LIMIT:
        raise SystemExit(f"Expected at least {LIMIT} rows in {SOURCE}, got {len(lines)}")

    OUTPUT.write_text("\n".join(lines[:LIMIT]) + "\n", encoding="utf-8")
    print(f"Wrote {LIMIT} candidates to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
