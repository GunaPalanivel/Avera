import json
import logging

from src.logging_config import JsonFormatter, SafeExtraFilter, configure_logging


def test_json_formatter_includes_timestamp_and_module():
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    payload = json.loads(JsonFormatter().format(record))
    assert "timestamp" in payload
    assert payload["timestamp"].endswith("+00:00")
    assert payload["module"] == record.module
    assert payload["message"] == "hello"


def test_safe_extra_filter_strips_unsafe_fields():
    record = logging.LogRecord(
        name="test",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="warn",
        args=(),
        exc_info=None,
    )
    record.extra_fields = {
        "run_id": "abc",
        "email": "secret@example.com",
        "stage": "parse",
    }
    SafeExtraFilter().filter(record)
    assert record.extra_fields == {"run_id": "abc", "stage": "parse"}


def test_configure_logging_emits_structured_json(capsys):
    configure_logging()
    log = logging.getLogger("test.logging_config")
    log.info("structured", extra={"extra_fields": {"event": "test", "run_id": "r1"}})
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload["timestamp"]
    assert payload["module"]
    assert payload["event"] == "test"
    assert payload["run_id"] == "r1"
    assert "email" not in payload
