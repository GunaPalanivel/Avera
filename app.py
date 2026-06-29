"""Gradio sandbox for HuggingFace Spaces and local Docker demo."""

import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path

import gradio as gr
from src.exceptions import ConfigError
from src.parsers.candidate_parser import count_candidates
from src.path_validation import validate_upload_filename

REPO_ROOT = Path.cwd()
SANDBOX_DIR = Path(os.environ.get("AVERA_SANDBOX_DIR", REPO_ROOT / ".sandbox"))
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


def rank_candidates(file_obj):
    """Run rank.py on an uploaded JSONL file; return table, log, and CSV download."""
    if file_obj is None:
        return None, "Please upload a `.jsonl` file.", None

    try:
        safe_name = validate_upload_filename(Path(file_obj.name).name)
    except ConfigError as exc:
        return None, str(exc), None

    if not safe_name.lower().endswith(".jsonl"):
        return None, "Only `.jsonl` uploads are supported.", None

    input_path = SANDBOX_DIR / safe_name
    output_path = SANDBOX_DIR / "submission.csv"
    shutil.copy2(file_obj.name, input_path)

    candidate_count = count_candidates(input_path, limit=100)
    if candidate_count == 0:
        return None, "No valid candidates found in the uploaded file.", None

    limit = min(100, candidate_count)

    cmd = [
        sys.executable,
        "rank.py",
        "--candidates",
        str(input_path),
        "--limit",
        str(limit),
        "--out",
        str(output_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=Path.cwd())
    except subprocess.CalledProcessError as exc:
        return None, f"Ranking failed:\n{exc.stderr or exc.stdout}", None

    rows: list[list[str]] = []
    with output_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))

    log = f"Ranked {limit} candidate(s) from upload ({candidate_count} valid in file).\nBundled JD: DataSet/job_description.txt\n\n{result.stdout.strip()}"
    return rows, log, str(output_path)


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Avera Ranking Engine Sandbox") as demo:
        gr.Markdown(
            "# Avera Ranking Engine Sandbox\nUpload a `.jsonl` candidate file. The engine scores deterministically and returns a ranked CSV (up to 100 rows). Fictional companies and honeypots are filtered — output may be fewer than upload rows."
        )
        with gr.Row():
            file_in = gr.File(label="Upload candidates.jsonl", file_types=[".jsonl"])
        rank_btn = gr.Button("Rank candidates", variant="primary")
        results_table = gr.Dataframe(
            label="Ranked output",
            headers=["candidate_id", "rank", "score", "reasoning"],
            interactive=False,
        )
        log_out = gr.Textbox(label="Execution log", lines=8)
        csv_out = gr.File(label="Download submission.csv")

        rank_btn.click(
            fn=rank_candidates,
            inputs=file_in,
            outputs=[results_table, log_out, csv_out],
        )
        file_in.upload(
            fn=rank_candidates,
            inputs=file_in,
            outputs=[results_table, log_out, csv_out],
        )
    return demo


if __name__ == "__main__":
    build_demo().launch(server_name="0.0.0.0", server_port=7860)
