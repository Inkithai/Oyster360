"""Central structured (JSON) logging configuration for API and worker processes.

Logs are emitted as one JSON object per line so they can be ingested directly by
log aggregation platforms (Loki, Datadog, CloudWatch, etc.). The structured
output is produced by ``python-json-logger`` and is what every service entry
point (``app.main``, Celery workers) configures via :func:`configure_logging`.
"""
import logging
import sys
from datetime import datetime, timezone

try:
    from pythonjsonlogger import json as jsonlogger
except ImportError:
    from pythonjsonlogger import jsonlogger  # type: ignore[no-redef]


class StructuredJsonFormatter(jsonlogger.JsonFormatter):
    """Add service metadata and a stable UTC timestamp to every log record."""

    _RESERVED = jsonlogger.JsonFormatter.default_msec_format

    def add_fields(self, log_record, record, message_dict):  # type: ignore[override]
        super().add_fields(log_record, record, message_dict)
        # Rename the default "message"/"asctime" keys to the canonical names
        # expected by our log pipeline.
        log_record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        log_record.setdefault("level", record.levelname)
        log_record.setdefault("logger", record.name)
        log_record["service"] = "oyster360-backend"
        # request_id / duration_ms are passed via logger.info(..., extra=...)
        for extra_key in ("request_id", "method", "path", "status_code", "duration_ms"):
            value = getattr(record, extra_key, None)
            if value is not None:
                log_record.setdefault(extra_key, value)


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger once; application modules use normal logging APIs.

    Repeated calls are idempotent: a handler is only attached the first time so
    importing the app from multiple entry points (uvicorn, celery, pytest) never
    produces duplicate log lines.
    """
    root = logging.getLogger()
    if any(getattr(handler, "_oyster360_handler", False) for handler in root.handlers):
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())
    handler._oyster360_handler = True  # type: ignore[attr-defined]
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


logger = logging.getLogger("oyster360")
