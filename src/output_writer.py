from pathlib import Path
from typing import Any

import defusedcsv.csv as csv
import openpyxl

from src.exceptions import OutputError
from src.models import CandidateModel

EXPECTED_SUBMISSION_ROWS = 100

RankResult = tuple[float, float, CandidateModel, str]


def sanitize_cell(value: Any) -> str:
    """Sanitizes a cell value to prevent CSV injection (OWASP A03)."""
    val_str = str(value)
    if val_str.startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{val_str}"
    return val_str


def validate_output_canary(
    results: list[RankResult],
    input_ids: set[str] | None = None,
    expected_rows: int = EXPECTED_SUBMISSION_ROWS,
) -> None:
    """ADR-16: ranked IDs must be unique, count must match, and subset of input pool."""
    if len(results) != expected_rows:
        raise OutputError(f"Output canary failed: expected {expected_rows} rows, got {len(results)}")

    seen_ids: set[str] = set()
    for _, _jp, candidate, _ in results:
        cid = candidate.candidate_id
        if cid in seen_ids:
            raise OutputError(f"Output canary failed: duplicate candidate_id {cid}")
        if input_ids is not None and cid not in input_ids:
            raise OutputError(f"Output canary failed: {cid} not in input candidate pool")
        seen_ids.add(cid)


def write_submission(
    output_path: str | Path,
    results: list[RankResult],
    input_ids: set[str] | None = None,
    expected_rows: int | None = None,
) -> None:
    """Writes CSV + XLSX submission files after ADR-16 canary validation."""
    rows = expected_rows if expected_rows is not None else EXPECTED_SUBMISSION_ROWS
    validate_output_canary(results, input_ids=input_ids, expected_rows=rows)

    path = Path(output_path)
    csv_path = path.with_suffix(".csv")
    xlsx_path = path.with_suffix(".xlsx")

    csv_headers = ["candidate_id", "rank", "score", "reasoning"]
    xlsx_headers = ["candidate_id", "rank", "score", "join_probability", "reasoning"]

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for rank_idx, (score, _join_prob, candidate, reasoning) in enumerate(results, start=1):
            writer.writerow(
                [
                    sanitize_cell(candidate.candidate_id),
                    sanitize_cell(rank_idx),
                    sanitize_cell(f"{score:.4f}"),
                    sanitize_cell(reasoning),
                ]
            )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ranking Results"
    ws.append(xlsx_headers)

    for rank_idx, (score, join_prob, candidate, reasoning) in enumerate(results, start=1):
        ws.append(
            [
                sanitize_cell(candidate.candidate_id),
                sanitize_cell(rank_idx),
                sanitize_cell(f"{score:.4f}"),
                sanitize_cell(f"{join_prob:.4f}"),
                sanitize_cell(reasoning),
            ]
        )

    wb.save(xlsx_path)
