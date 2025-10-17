"""Tests for structured (JSON) logging configuration (app.core.logging)."""
import json
import logging

from app.core.logging import StructuredJsonFormatter, configure_logging


def test_configure_logging_is_idempotent():
    """Calling configure_logging repeatedly must not stack duplicate handlers."""
    configure_logging()
    configure_logging()
    configure_logging()
    marked = [
        h for h in logging.getLogger().handlers
        if getattr(h, "_oyster360_handler", False)
    ]
    assert len(marked) == 1


def test_json_formatter_emits_structured_payload():
    formatter = StructuredJsonFormatter()
    record = logging.LogRecord(
        name="oyster360",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-abc"
    record.method = "GET"
    record.path = "/health"
    record.status_code = 200
    record.duration_ms = 12.5

    payload = json.loads(formatter.format(record))
    assert payload["message"] == "request completed"
    assert payload["service"] == "oyster360-backend"
    assert payload["level"] == "INFO"
    assert payload["logger"] == "oyster360"
    assert payload["request_id"] == "req-abc"
    assert payload["method"] == "GET"
    assert payload["path"] == "/health"
    assert payload["status_code"] == 200
    assert payload["duration_ms"] == 12.5
    assert "timestamp" in payload


def test_json_formatter_serializes_exceptions():
    formatter = StructuredJsonFormatter()
    try:
        raise ValueError("boom")
    except ValueError:
        import sys
        record = logging.LogRecord(
            name="oyster360", level=logging.ERROR, pathname=__file__,
            lineno=1, msg="failed", args=(), exc_info=sys.exc_info(),
        )
    payload = json.loads(formatter.format(record))
    assert payload["message"] == "failed"
    assert "exception" in payload or "exc_info" in payload
