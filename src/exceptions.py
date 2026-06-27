"""Avera application exceptions (ADR-15)."""


class AveraError(Exception):
    """Base error for recoverable pipeline failures."""


class DataError(AveraError):
    """Malformed or oversized input records; usually skipped with a warning."""


class ValidationError(AveraError):
    """Boundary validation failed before processing."""


class ScoringError(AveraError):
    """Scorer failure on a candidate (P2+)."""


class PipelineError(AveraError):
    """Unrecoverable pipeline stage failure."""


class OutputError(AveraError):
    """Submission output constraint violation (P3+)."""


class ConfigError(AveraError):
    """Invalid configuration or paths at startup or boundary."""


# Backward-compatible alias for parse skips
ParseError = DataError
