#!/usr/bin/env python3
"""Avera ranking CLI (foundation: health check and path validation)."""

import argparse
import sys
import uuid
from pathlib import Path

from src.exceptions import ConfigError
from src.logging_config import configure_logging, get_logger
from src.parsers.candidate_parser import count_candidates
from src.parsers.jd_parser import load_job_requirements
from src.path_validation import validate_input_path, validate_output_path

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank candidates for Redrob Track 01")
    parser.add_argument(
        "--health",
        action="store_true",
        help="Verify imports, config, and logging (no data required)",
    )
    parser.add_argument("--candidates", help="Path to candidates.jsonl")
    parser.add_argument("--out", help="Output submission.csv path")
    parser.add_argument(
        "--limit", type=int, default=None, help="Max candidates to read (smoke tests)"
    )
    return parser


def run_health() -> int:
    import src.config  # noqa: F401  # side effect: ConfigError if weights/lists invalid at import

    requirements = load_job_requirements()
    if not requirements.must_have_skills:
        print("error: job requirements must-have list is empty", file=sys.stderr)
        return 2

    print(
        f"[OK] avera foundation ready "
        f"({len(requirements.must_have_skills)} must-have skills loaded)"
    )
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

    n = count_candidates(candidates_path, limit=args.limit)
    logger.info(
        "parsed candidates",
        extra={"extra_fields": {"run_id": run_id, "count": n, "event": "parse_done"}},
    )
    if args.out:
        # TODO: ranker + output_writer not wired yet; --out only validates paths for now
        print(
            "error: ranking pipeline not wired yet (foundation milestone)",
            file=sys.stderr,
        )
        return 2
    print(f"parsed {n} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
