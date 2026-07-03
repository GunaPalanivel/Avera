#!/usr/bin/env python3
"""Avera ranking CLI (foundation: health check and path validation)."""

import argparse
import os
import sys
import time
import uuid
from pathlib import Path

from src.exceptions import ConfigError
from src.logging_config import configure_logging, get_logger
from src.output_writer import write_submission
from src.parsers.candidate_parser import stream_candidates
from src.parsers.jd_parser import load_job_requirements
from src.path_validation import validate_input_path, validate_output_path
from src.ranker import Ranker

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank candidates for Redrob Track 01")
    parser.add_argument(
        "--health",
        action="store_true",
        help="Verify imports, config, and logging (no data required)",
    )
    parser.add_argument("--candidates", help="Path to candidates.jsonl")
    parser.add_argument("--jd", help="Path to job_description.txt")
    parser.add_argument("--out", help="Output submission.csv path")
    parser.add_argument("--limit", type=int, default=None, help="Max candidates to read (smoke tests)")
    return parser


def run_health() -> int:
    import src.config  # noqa: F401  # side effect: ConfigError if weights/lists invalid at import

    requirements = load_job_requirements()
    if not requirements.must_have_skills:
        print("error: job requirements must-have list is empty", file=sys.stderr)
        return 2

    print(f"[OK] avera foundation ready ({len(requirements.must_have_skills)} must-have skills loaded)")
    return 0


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    run_id = str(uuid.uuid4())
    args = build_parser().parse_args(argv)

    if args.health:
        logger.info("health check", extra={"extra_fields": {"run_id": run_id, "event": "health"}})
        return run_health()

    if not args.candidates:
        print("error: --candidates required unless --health", file=sys.stderr)
        return 2

    repo_root = Path.cwd()
    try:
        candidates_path = validate_input_path(args.candidates, allowed_root=repo_root)
        if args.out:
            validate_output_path(args.out, allowed_root=repo_root)
    except ConfigError as exc:
        # User-facing errors stay generic; run_id in logs links to the full trace
        print(f"error: {exc}", file=sys.stderr)
        return 2

    logger.info(
        "ranking candidates",
        extra={
            "extra_fields": {
                "run_id": run_id,
                "event": "ranking_start",
                "trace_id": run_id,
                "jd_path": str(args.jd or "DataSet/job_description.txt"),
            }
        },
    )

    job_reqs = load_job_requirements(args.jd)
    ranker = Ranker(job_reqs)
    requested_top_k = args.limit if args.limit else 100
    input_ids: set[str] = set()

    def track_stream():
        for candidate in stream_candidates(candidates_path, limit=args.limit):
            input_ids.add(candidate.candidate_id)
            yield candidate

    use_semantic_prefill = os.environ.get("AVERA_SKIP_SEMANTIC", "").lower() not in ("1", "true", "yes")
    if use_semantic_prefill and args.limit is None:
        t_prefill = time.perf_counter()
        encoded = ranker.prefill_semantic_stream(stream_candidates(candidates_path))
        prefill_ms = int((time.perf_counter() - t_prefill) * 1000)
    else:
        encoded = 0
        prefill_ms = 0

    t0 = time.perf_counter()
    top_k = ranker.rank(track_stream(), top_k=requested_top_k, require_exact_count=(args.limit is None))
    wall_ms = int((time.perf_counter() - t0) * 1000)
    stats = ranker.last_pipeline_stats

    logger.info(
        "ranked candidates",
        extra={
            "extra_fields": {
                "run_id": run_id,
                "trace_id": run_id,
                "event": "ranking_done",
                "stage": "pipeline_complete",
                "input_count": stats.get("input_count", len(input_ids)),
                "output_count": stats.get("output_count", len(top_k)),
                "scored_count": stats.get("scored_count", 0),
                "filtered_zero": stats.get("filtered_zero", 0),
                "prefill_ms": prefill_ms,
                "semantic_encoded": encoded,
                "score_ms": stats.get("score_ms", wall_ms),
                "latency_ms": stats.get("total_ms", wall_ms),
                "seniority_level": job_reqs.seniority_level,
            }
        },
    )

    if args.out:
        expected_rows = requested_top_k if not args.limit else len(top_k)
        write_submission(args.out, top_k, input_ids=input_ids, expected_rows=expected_rows)
        print(f"Ranked {len(top_k)} candidates and wrote to {args.out}")
    else:
        print(f"Ranked {len(top_k)} candidates. Top 5:")
        for i, (score, _jp, cand, _reasoning) in enumerate(top_k[:5], start=1):
            print(f"{i}. {cand.candidate_id} - Score: {score:.4f} ({cand.profile.current_title} at {cand.profile.current_company})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
