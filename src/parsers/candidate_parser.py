"""Stream-parse candidate JSONL with size guards."""

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.config import MAX_JSONL_BYTES, MAX_JSONL_LINE_BYTES
from src.exceptions import ConfigError, DataError
from src.logging_config import get_logger
from src.models import CandidateModel

logger = get_logger(__name__)

_PARSE_STAGE = "parse"


def _candidate_id_from_raw(data: Any) -> str | None:
    if isinstance(data, dict):
        raw_id = data.get("candidate_id")
        if isinstance(raw_id, str):
            return raw_id
    return None


def stream_candidates(path: Path, limit: int | None = None) -> Iterator[CandidateModel]:
    """Yield validated candidates; skip bad lines with a warning."""
    size = path.stat().st_size
    if size > MAX_JSONL_BYTES:
        raise ConfigError(
            f"Input file exceeds {MAX_JSONL_BYTES} bytes",
            stage=_PARSE_STAGE,
        )

    count = 0
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            if limit is not None and count >= limit:
                break
            raw = line.strip()
            if not raw:
                continue
            if len(line.encode("utf-8")) > MAX_JSONL_LINE_BYTES:
                logger.warning(
                    "Skipping oversized line",
                    extra={
                        "extra_fields": {
                            "line_no": line_no,
                            "event": "skip_line",
                            "stage": _PARSE_STAGE,
                        }
                    },
                )
                continue
            candidate_id: str | None = None
            try:
                data = json.loads(raw)
                candidate_id = _candidate_id_from_raw(data)
                candidate = CandidateModel.model_validate(data)
            except (json.JSONDecodeError, ValidationError, ValueError) as exc:
                # At 100K rows a few bad lines are normal, log and continue
                err = DataError(
                    type(exc).__name__,
                    candidate_id=candidate_id,
                    stage=_PARSE_STAGE,
                )
                extra_fields = {
                    "line_no": line_no,
                    "event": "parse_skip",
                    "stage": _PARSE_STAGE,
                }
                if err.candidate_id:
                    extra_fields["candidate_id"] = err.candidate_id
                logger.warning(
                    "Skipping malformed candidate line (%s): %s",
                    err.__class__.__name__,
                    str(exc),
                    extra={"extra_fields": extra_fields},
                )
                continue
            count += 1
            yield candidate


def count_candidates(path: Path, limit: int | None = None) -> int:
    return sum(1 for _ in stream_candidates(path, limit=limit))
