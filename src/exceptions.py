"""Avera application exceptions (ADR-15)."""


class AveraError(Exception):
    """Base error for recoverable pipeline failures."""

    def __init__(
        self,
        message: str = "",
        *,
        candidate_id: str | None = None,
        stage: str | None = None,
        scorer_name: str | None = None,
    ) -> None:
        super().__init__(message)
        self.candidate_id = candidate_id
        self.stage = stage
        self.scorer_name = scorer_name

    def context_fields(self) -> dict[str, str]:
        return {
            k: v
            for k, v in {
                "candidate_id": self.candidate_id,
                "stage": self.stage,
                "scorer_name": self.scorer_name,
            }.items()
            if v is not None
        }


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
