import csv
from pathlib import Path
from typing import Any

from src.exceptions import DataError
from src.models import CandidateModel


def write_submission(output_path: str | Path, results: list[tuple[float, CandidateModel, str]]) -> None:
    """
    Writes the final ranking to a CSV file matching the organizer's exact specification.
    
    Format:
    candidate_id,rank,score,reasoning
    """
    path = Path(output_path)
    
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for rank_idx, (score, candidate, reasoning) in enumerate(results, start=1):
            writer.writerow([
                candidate.candidate_id,
                rank_idx,
                f"{score:.4f}",
                reasoning
            ])
