"""Path validation at CLI and upload boundaries."""

from pathlib import Path

from src.exceptions import ConfigError

ALLOWED_INPUT_SUFFIXES = (".jsonl", ".json")
MAX_UPLOAD_FILENAME_LEN = 255

_FORMULA_PREFIXES = frozenset(("=", "+", "-", "@", "|", "%", "\t", "\r"))


def validate_input_path(raw: str, allowed_root: Path | None = None) -> Path:
    """Reject traversal and unsupported extensions before open()."""
    p = Path(raw).resolve()
    if allowed_root is not None:
        root = allowed_root.resolve()
        if not p.is_relative_to(root):
            raise ConfigError(f"Path escapes allowed directory: {p}")
    if not p.exists():
        raise ConfigError(f"Input file not found: {p}")
    if not p.is_file():
        raise ConfigError(f"Input path is not a file: {p}")
    if p.suffix.lower() not in ALLOWED_INPUT_SUFFIXES:
        raise ConfigError(f"Unsupported file type: {p.suffix}")
    return p


def validate_output_path(raw: str, allowed_root: Path | None = None) -> Path:
    """Ensure output is a .csv under allowed root when provided."""
    p = Path(raw).resolve()
    if allowed_root is not None:
        root = allowed_root.resolve()
        if not p.is_relative_to(root):
            raise ConfigError(f"Path escapes allowed directory: {p}")
    if p.suffix.lower() != ".csv":
        raise ConfigError("Output must be a .csv file")
    if p.exists() and not p.is_file():
        raise ConfigError(f"Output path is not a file: {p}")
    return p


def validate_upload_filename(name: str) -> str:
    """Reject path segments in uploaded filenames."""
    if not name or len(name) > MAX_UPLOAD_FILENAME_LEN:
        raise ConfigError("Invalid upload filename")
    if ".." in name or "/" in name or "\\" in name:
        raise ConfigError("Invalid upload filename")
    return name


def sanitize_cell(value: str) -> str:
    """Prevent CSV formula injection in string cells."""
    s = str(value).strip()
    if s and s[0] in _FORMULA_PREFIXES:
        return "'" + s.replace("|", "\\|")
    return s
