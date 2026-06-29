#!/usr/bin/env python3
"""Run ranking pipeline against alternate JDs to prove parameterization (zero code edits)."""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CANDIDATES = REPO / "tests" / "fixtures" / "sample.jsonl"
CASES = [
    ("AI/ML (bundled)", REPO / "DataSet" / "job_description.txt", REPO / ".sandbox" / "generalization_ai.csv"),
    (
        "DevOps/SRE (alt)",
        REPO / "DataSet" / "job_description_devops.txt",
        REPO / ".sandbox" / "generalization_devops.csv",
    ),
]


def main() -> int:
    (REPO / ".sandbox").mkdir(parents=True, exist_ok=True)
    env = {**dict(**__import__("os").environ), "AVERA_SKIP_SEMANTIC": "1"}

    for label, jd_path, out_path in CASES:
        if not jd_path.exists():
            print(f"SKIP {label}: missing {jd_path}", file=sys.stderr)
            return 1
        cmd = [
            sys.executable,
            str(REPO / "rank.py"),
            "--candidates",
            str(CANDIDATES),
            "--jd",
            str(jd_path),
            "--limit",
            "10",
            "--out",
            str(out_path),
        ]
        print(f"=== {label} ===")
        subprocess.run(cmd, cwd=REPO, env=env, check=True)
        lines = out_path.read_text(encoding="utf-8").strip().splitlines()
        print(f"Wrote {len(lines) - 1} ranked rows to {out_path.name}\n")

    print("Generalization smoke OK: same rank.py, two JD files, no code changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
