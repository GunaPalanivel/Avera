from pathlib import Path
from typing import Any

import defusedcsv.csv as csv
import openpyxl

from src.models import CandidateModel


def sanitize_cell(value: Any) -> str:
    """Sanitizes a cell value to prevent CSV injection (OWASP A03)."""
    val_str = str(value)
    if val_str.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{val_str}"
    return val_str


def write_submission(output_path: str | Path, results: list[tuple[float, CandidateModel, str]]) -> None:
    """
    Writes the final ranking to a CSV and XLSX file matching the organizer's exact specification.

    Format:
    candidate_id,rank,score,reasoning
    """
    path = Path(output_path)
    csv_path = path.with_suffix(".csv")
    xlsx_path = path.with_suffix(".xlsx")

    # ADR-16: Output canary
    seen_ids = set()
    for _, candidate, _ in results:
        if candidate.candidate_id in seen_ids:
            raise ValueError(f"Output canary failed: Duplicate candidate_id {candidate.candidate_id}")
        seen_ids.add(candidate.candidate_id)

    headers = ["candidate_id", "rank", "score", "reasoning"]

    # 1. Write defused CSV
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for rank_idx, (score, candidate, reasoning) in enumerate(results, start=1):
            writer.writerow(
                [
                    sanitize_cell(candidate.candidate_id),
                    sanitize_cell(rank_idx),
                    sanitize_cell(f"{score:.4f}"),
                    sanitize_cell(reasoning),
                ]
            )

    # 2. Write XLSX (for safe consumption by business users)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ranking Results"
    ws.append(headers)

    for rank_idx, (score, candidate, reasoning) in enumerate(results, start=1):
        ws.append([candidate.candidate_id, rank_idx, f"{score:.4f}", reasoning])

    wb.save(xlsx_path)
