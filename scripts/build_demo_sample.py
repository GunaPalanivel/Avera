#!/usr/bin/env python3
"""Build a curated, AI-dense demo sample for the sandbox.

Pulls real records from the official pool so the hosted Space shows a strong shortlist
instead of the noisy first-100 slice: the strongest candidates (by the committed
submission.csv) plus a few real honeypots and fictional-company profiles so the demo
also shows the filtering at work. Every record is a real row from candidates.jsonl.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.config import FICTIONAL_COMPANIES  # noqa: E402
from src.detectors.honeypot_detector import is_honeypot  # noqa: E402
from src.models import CandidateModel  # noqa: E402

CANDIDATES = REPO / "DataSet" / "candidates.jsonl"
SUBMISSION = REPO / "submission.csv"
OUT = REPO / "DataSet" / "sample_candidates_demo.jsonl"

STRONG_COUNT = 85
FICTIONAL_COUNT = 8
HONEYPOT_COUNT = 7


def _strong_ids() -> list[str]:
    with SUBMISSION.open(encoding="utf-8", newline="") as f:
        ids = [row["candidate_id"] for row in csv.DictReader(f)]
    return ids[:STRONG_COUNT]


def main() -> int:
    strong_ids = set(_strong_ids())
    strong: dict[str, str] = {}
    fictional: list[str] = []
    honeypots: list[str] = []

    with CANDIDATES.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            cid = obj.get("candidate_id")
            if cid in strong_ids and cid not in strong:
                strong[cid] = line
                continue
            if len(fictional) < FICTIONAL_COUNT or len(honeypots) < HONEYPOT_COUNT:
                try:
                    model = CandidateModel.model_validate(obj)
                except Exception:
                    continue
                if len(fictional) < FICTIONAL_COUNT and model.profile.current_company in FICTIONAL_COMPANIES:
                    fictional.append(line)
                elif len(honeypots) < HONEYPOT_COUNT and is_honeypot(model):
                    honeypots.append(line)
            if len(strong) == len(strong_ids) and len(fictional) >= FICTIONAL_COUNT and len(honeypots) >= HONEYPOT_COUNT:
                break

    # Interleave traps among the strong rows so filtering is visible anywhere in the file
    ordered_strong = [strong[c] for c in _strong_ids() if c in strong]
    traps = fictional + honeypots
    lines: list[str] = []
    trap_every = max(1, len(ordered_strong) // max(1, len(traps)))
    ti = 0
    for i, row in enumerate(ordered_strong):
        lines.append(row)
        if ti < len(traps) and (i + 1) % trap_every == 0:
            lines.append(traps[ti])
            ti += 1
    lines.extend(traps[ti:])

    with OUT.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(line if line.endswith("\n") else line + "\n")

    print(f"Wrote {len(lines)} records to {OUT.name} (strong={len(ordered_strong)}, fictional={len(fictional)}, honeypots={len(honeypots)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
