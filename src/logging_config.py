"""Structured JSON logging without PII in extra fields."""

import json
import logging
import sys
from typing import Any

LOG_SAFE_FIELDS = frozenset(
    {
        "run_id",
        "stage",
        "candidate_id",
        "line_no",
        "event",
        "duration_ms",
        "count",
    }
)


class SafeExtraFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            record.extra_fields = {
                k: v for k, v in record.extra_fields.items() if k in LOG_SAFE_FIELDS
            }
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(extra)
        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(SafeExtraFilter())
    root.addHandler(handler)
    root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
