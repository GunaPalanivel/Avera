#!/usr/bin/env python3
"""Rebuild the HuggingFace Space staging directory (space_deploy/) from the current repo.

Refreshes the runtime code and JD files while preserving the Space README frontmatter and the
runtime-only requirements. Run before pushing the Space:

    python scripts/sync_space.py
    hf auth login
    hf upload gp5901/avera-ranker . --repo-type=space --local-dir space_deploy --commit-message "sync current codebase"
"""

from __future__ import annotations

import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPACE = REPO / "space_deploy"

DIR_COPIES: tuple[tuple[str, str], ...] = (("src", "src"),)

FILE_COPIES: tuple[tuple[str, str], ...] = (
    ("rank.py", "rank.py"),
    ("app.py", "app.py"),
    ("scripts/download_model.py", "scripts/download_model.py"),
    ("DataSet/job_description.txt", "DataSet/job_description.txt"),
    ("DataSet/job_description_devops.txt", "DataSet/job_description_devops.txt"),
    ("DataSet/sample_candidates_demo.jsonl", "DataSet/sample_candidates_demo.jsonl"),
    ("DataSet/sample_candidates_50.jsonl", "DataSet/sample_candidates_50.jsonl"),
)

RUNTIME_REQUIREMENTS = "pydantic>=2.9,<3\ndefusedcsv>=2.0.0\ngradio>=5.0.0\nopenpyxl>=3.1.0\nsentence-transformers>=3.0.0\ntorch>=2.4.0\n"

DEFAULT_README = (
    "---\n"
    "title: Avera Ranking Engine Sandbox\n"
    "emoji: dart\n"
    "colorFrom: blue\n"
    "colorTo: green\n"
    "sdk: gradio\n"
    "app_file: app.py\n"
    "pinned: false\n"
    "license: mit\n"
    "---\n\n"
    "# Avera Redrob Track 1 Sandbox\n\n"
    "Upload a `.jsonl` candidate file (1-100 rows). Hybrid semantic + deterministic ranker "
    "with explainable reasoning.\n\n"
    "- GitHub: https://github.com/GunaPalanivel/Avera\n"
    "- Model: all-MiniLM-L6-v2 (downloaded on first rank; cached by HuggingFace)\n"
)


def _ignore_pycache(_dir: str, names: list[str]) -> set[str]:
    return {n for n in names if n == "__pycache__" or n.endswith(".pyc")}


def main() -> int:
    SPACE.mkdir(parents=True, exist_ok=True)

    for src_rel, dst_rel in DIR_COPIES:
        dst = SPACE / dst_rel
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(REPO / src_rel, dst, ignore=_ignore_pycache)

    for src_rel, dst_rel in FILE_COPIES:
        dst = SPACE / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / src_rel, dst)

    # Preserve an existing Space README (frontmatter) and requirements; only seed defaults if missing
    requirements = SPACE / "requirements.txt"
    if not requirements.exists():
        requirements.write_text(RUNTIME_REQUIREMENTS, encoding="utf-8")

    readme = SPACE / "README.md"
    if not readme.exists():
        readme.write_text(DEFAULT_README, encoding="utf-8")

    print(f"Synced space_deploy from {REPO}")
    print("Next steps:")
    print("  hf auth login")
    print('  hf upload gp5901/avera-ranker . --repo-type=space --local-dir space_deploy --commit-message "sync current codebase"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
