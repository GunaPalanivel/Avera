import pytest
from src.exceptions import ConfigError
from src.path_validation import (
    sanitize_cell,
    validate_input_path,
    validate_output_path,
    validate_upload_filename,
)


def test_validate_input_path_rejects_missing(tmp_path):
    with pytest.raises(ConfigError):
        validate_input_path(str(tmp_path / "missing.jsonl"))


def test_validate_input_path_accepts_jsonl(tmp_path):
    f = tmp_path / "c.jsonl"
    f.write_text("{}\n", encoding="utf-8")
    assert validate_input_path(str(f), allowed_root=tmp_path) == f.resolve()


def test_validate_output_path_requires_csv(tmp_path):
    with pytest.raises(ConfigError):
        validate_output_path(str(tmp_path / "out.txt"), allowed_root=tmp_path)


def test_validate_upload_filename_rejects_traversal():
    with pytest.raises(ConfigError):
        validate_upload_filename("../evil.jsonl")


def test_sanitize_cell_prefixes_formula():
    assert sanitize_cell("=1+1").startswith("'")


def test_path_escape_allowed_root(tmp_path):
    outside = tmp_path.parent / "outside.jsonl"
    outside.write_text("{}\n", encoding="utf-8")
    inner = tmp_path / "inside.jsonl"
    inner.write_text("{}\n", encoding="utf-8")
    validate_input_path(str(inner), allowed_root=tmp_path)
    with pytest.raises(ConfigError):
        validate_input_path(str(outside), allowed_root=tmp_path)
