#!/usr/bin/env python3
"""Audit submission.csv against JSONL profiles and JD intent signals."""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.detectors.honeypot_detector import is_honeypot  # noqa: E402
from src.models import CandidateModel  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]

CONSULTING = frozenset(
    {
        "TCS",
        "Infosys",
        "Wipro",
        "Accenture",
        "Cognizant",
        "Capgemini",
        "Mindtree",
        "HCL",
        "Mphasis",
        "Tech Mahindra",
        "Genpact",
    }
)
FICTIONAL = frozenset({"Dunder Mifflin", "Globex Inc", "Acme Corp", "Stark Industries", "Wayne Enterprises"})
AI_TITLE_FRAGMENTS = (
    "ai engineer",
    "ml engineer",
    "machine learning",
    "applied ml",
    "data scientist",
    "lead ai",
    "staff machine",
    "nlp engineer",
    "applied scientist",
)
JD_CITIES = ("pune", "noida", "mumbai", "delhi", "hyderabad", "bangalore", "bengaluru", "india")


def load_ranked_ids(submission_path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(submission_path.open(encoding="utf-8")))


def stream_lookup(jsonl_path: Path, ids: set[str]) -> dict[str, dict]:
    lookup: dict[str, dict] = {}
    with jsonl_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            cid = record["candidate_id"]
            if cid in ids:
                lookup[cid] = record
            if len(lookup) == len(ids):
                break
    return lookup


def audit_flags(candidate: dict) -> list[str]:
    profile = candidate["profile"]
    flags: list[str] = []
    if profile.get("current_company") in FICTIONAL:
        flags.append("fictional_co")
    title = (profile.get("current_title") or "").lower()
    if not any(fragment in title for fragment in AI_TITLE_FRAGMENTS):
        flags.append("non_ai_title")
    company = profile.get("current_company") or ""
    if company in CONSULTING or any(name in company for name in CONSULTING):
        flags.append("consulting")
    yoe = float(profile.get("years_of_experience") or 0)
    if yoe < 5 or yoe > 9:
        flags.append("yoe_outside_5_9")
    location = (profile.get("location") or "").lower()
    if not any(city in location for city in JD_CITIES):
        flags.append("location_miss")
    signals = candidate.get("redrob_signals", {})
    if signals.get("recruiter_response_rate", 1) < 0.05:
        flags.append("ghost_response")
    if signals.get("github_activity_score", 100) >= 80:
        flags.append("github_strong")
    return flags


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="JD alignment audit for submission.csv")
    parser.add_argument("--submission", default=str(REPO_ROOT / "submission.csv"))
    parser.add_argument("--candidates", default=str(REPO_ROOT / "DataSet" / "candidates.jsonl"))
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args(argv)

    submission_path = Path(args.submission)
    jsonl_path = Path(args.candidates)
    rows = load_ranked_ids(submission_path)
    ids = {row["candidate_id"] for row in rows}
    lookup = stream_lookup(jsonl_path, ids)

    missing = ids - set(lookup)
    if missing:
        print(f"WARNING: {len(missing)} ranked IDs not found in JSONL", file=sys.stderr)

    honeypot_count = 0
    flag_counter: Counter[str] = Counter()
    for row in rows:
        candidate = lookup[row["candidate_id"]]
        model = CandidateModel.model_validate(candidate)
        if is_honeypot(model):
            honeypot_count += 1
        for flag in audit_flags(candidate):
            flag_counter[flag] += 1

    print(f"Submission: {submission_path}")
    print(f"Rows: {len(rows)} | Honeypots in output: {honeypot_count}")
    print(f"AI/ML-like titles: {len(rows) - flag_counter['non_ai_title']}/{len(rows)}")
    print("\n=== FLAG COUNTS (top 100) ===")
    for name, count in flag_counter.most_common():
        print(f"  {name}: {count}")

    print(f"\n=== TOP {args.top} ===")
    print(f"{'rank':>4} {'id':<14} {'title':<32} {'company':<18} {'yoe':>4} {'score':>7} flags")
    for row in rows[: args.top]:
        candidate = lookup[row["candidate_id"]]
        profile = candidate["profile"]
        flags = audit_flags(candidate)
        print(
            f"{row['rank']:>4} {row['candidate_id']:<14} "
            f"{profile.get('current_title', '')[:32]:<32} "
            f"{profile.get('current_company', '')[:18]:<18} "
            f"{profile.get('years_of_experience', 0):>4} "
            f"{row['score']:>7} {flags}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
