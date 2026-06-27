"""Avera application exceptions."""


class AveraError(Exception):
    """Base error for recoverable pipeline failures."""


class ConfigError(AveraError):
    """Invalid configuration or paths at startup or boundary."""


class ParseError(AveraError):
    """Malformed candidate record; usually skipped with a warning."""
