#!/usr/bin/env python3
"""Offline evaluation helpers: honeypot rate, calibration NDCG@k, pipeline timing."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.detectors.honeypot_detector import is_honeypot  # noqa: E402
from src.models import CandidateModel  # noqa: E402
from src.parsers.candidate_parser import stream_candidates  # noqa: E402
from src.parsers.jd_parser import load_job_requirements  # noqa: E402
from src.ranker import Ranker  # noqa: E402

REAL_IDEAL_IDS = frozenset({"CAND_0071974", "CAND_0006567", "CAND_0005538", "CAND_0002025"})


def _ndcg_at_k(ranked_ids: list[str], ideal_ids: list[str], k: int = 10) -> float:
    if not ideal_ids:
        return 0.0
    ideal_set = {cid: (len(ideal_ids) - i) for i, cid in enumerate(ideal_ids)}
    dcg = 0.0
    for i, cid in enumerate(ranked_ids[:k]):
        rel = ideal_set.get(cid, 0)
        if rel:
            dcg += rel / math.log2(i + 2)
    idcg = sum((len(ideal_ids) - i) / math.log2(i + 2) for i in range(min(k, len(ideal_ids))))
    return dcg / idcg if idcg else 0.0


def precision_at_k(ranked_ids: list[str], ideal_ids: list[str], k: int) -> float:
    if k <= 0:
        return 0.0
    ideal_set = set(ideal_ids)
    hits = sum(1 for cid in ranked_ids[:k] if cid in ideal_set)
    return hits / k


def recovery_at_k(ranked_ids: list[str], ideal_ids: list[str], k: int = 10) -> tuple[int, int]:
    ideal_set = set(ideal_ids)
    found = sum(1 for cid in ranked_ids[:k] if cid in ideal_set)
    return found, len(ideal_set)


def honeypot_rate_in_submission(submission_csv: Path, candidates_path: Path) -> dict[str, float | int]:
    ranked_ids: list[str] = []
    with submission_csv.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            ranked_ids.append(row["candidate_id"])

    wanted = set(ranked_ids)
    by_id: dict[str, CandidateModel] = {}
    for cand in stream_candidates(candidates_path):
        if cand.candidate_id in wanted:
            by_id[cand.candidate_id] = cand
        if len(by_id) >= len(wanted):
            break

    traps = 0
    for cid in ranked_ids:
        cand = by_id.get(cid)
        if cand and is_honeypot(cand):
            traps += 1

    return {
        "top_k": len(ranked_ids),
        "honeypots_in_top_k": traps,
        "honeypot_rate": traps / len(ranked_ids) if ranked_ids else 0.0,
    }


def run_benchmark(candidates_path: Path, jd_path: Path | None, limit: int | None) -> dict[str, float | int]:
    job_reqs = load_job_requirements(jd_path)
    ranker = Ranker(job_reqs)
    t0 = time.perf_counter()
    results = ranker.rank(stream_candidates(candidates_path, limit=limit), top_k=100, require_exact_count=limit is None)
    wall_ms = int((time.perf_counter() - t0) * 1000)
    stats = dict(ranker.last_pipeline_stats)
    stats["wall_ms"] = wall_ms
    stats["top_score"] = results[0][0] if results else 0.0
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Avera offline eval")
    parser.add_argument("--submission", type=Path, default=REPO / "submission.csv")
    parser.add_argument("--candidates", type=Path, default=REPO / "DataSet" / "candidates.jsonl")
    parser.add_argument("--jd", type=Path, default=None)
    parser.add_argument("--calibration", type=Path, default=REPO / "tests" / "fixtures" / "calibration_batch.json")
    parser.add_argument("--honest-ndcg", action="store_true", help="Strip non-real ideal IDs before NDCG")
    parser.add_argument("--benchmark", action="store_true", help="Run ranking benchmark (may take minutes)")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    print("=== Honeypot rate (submission) ===")
    if args.submission.exists():
        hp = honeypot_rate_in_submission(args.submission, args.candidates)
        for key, val in hp.items():
            print(f"  {key}: {val}")
    else:
        print(f"  submission not found: {args.submission}")

    print("\n=== Calibration metrics ===")
    if args.calibration.exists():
        data = json.loads(args.calibration.read_text(encoding="utf-8"))
        ideal = data.get("ranked_ids", [])
        if args.honest_ndcg:
            ideal = [cid for cid in ideal if cid in REAL_IDEAL_IDS]
        if args.submission.exists():
            ranked: list[str] = []
            with args.submission.open(encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    ranked.append(row["candidate_id"])
            ndcg = _ndcg_at_k(ranked, ideal, k=10)
            p5 = precision_at_k(ranked, ideal, k=5)
            p10 = precision_at_k(ranked, ideal, k=10)
            found, total = recovery_at_k(ranked, ideal, k=10)
            print(f"  ideal_ids: {len(ideal)}")
            print(f"  ndcg@10: {ndcg:.4f}")
            print(f"  precision@5: {p5:.4f}")
            print(f"  precision@10: {p10:.4f}")
            print(f"  recovery@10: {found}/{total} real ideal candidates in top-10")
        else:
            print("  submission.csv required for calibration metrics")
    else:
        print(f"  calibration fixture missing: {args.calibration}")

    if args.benchmark:
        print("\n=== Pipeline benchmark ===")
        stats = run_benchmark(args.candidates, args.jd, args.limit)
        for key, val in stats.items():
            print(f"  {key}: {val}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
