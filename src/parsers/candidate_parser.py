"""Stream-parse candidate JSONL with size guards."""

import json
from collections.abc import Iterator
from pathlib import Path

from pydantic import ValidationError

from src.config import MAX_JSONL_BYTES, MAX_JSONL_LINE_BYTES
from src.exceptions import ConfigError, DataError
from src.logging_config import get_logger
from src.models import CandidateModel

logger = get_logger(__name__)


def stream_candidates(path: Path, limit: int | None = None) -> Iterator[CandidateModel]:
    """Yield validated candidates; skip bad lines with a warning."""
    size = path.stat().st_size
    if size > MAX_JSONL_BYTES:
        raise ConfigError(f"Input file exceeds {MAX_JSONL_BYTES} bytes")

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
                    extra={"extra_fields": {"line_no": line_no, "event": "skip_line"}},
                )
                continue
            try:
                data = json.loads(raw)
                candidate = CandidateModel.model_validate(data)
            except (json.JSONDecodeError, ValidationError, ValueError) as exc:
                logger.warning(
                    "Skipping malformed candidate line (%s): %s",
                    DataError.__name__,
                    type(exc).__name__,
                    extra={"extra_fields": {"line_no": line_no, "event": "parse_skip"}},
                )
                continue
            count += 1
            yield candidate


def count_candidates(path: Path, limit: int | None = None) -> int:
    return sum(1 for _ in stream_candidates(path, limit=limit))
