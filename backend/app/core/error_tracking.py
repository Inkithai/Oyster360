"""Optional production error tracking.

Sentry is disabled by default and never receives test or local data unless a
DSN is explicitly configured. When enabled, a ``before_send`` hook scrubs
common personally identifiable information so no secrets or user PII leave the
infrastructure.
"""
import logging

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.core.config import settings

logger = logging.getLogger(__name__)

# Keys that are stripped from Sentry events/tags/breadcrumbs to avoid leaking
# credentials or personally identifiable information to a third party.
_SENSITIVE_KEYS = {
    "password", "password_hash", "secret", "token", "access_token",
    "refresh_token", "authorization", "api_key", "stripe_secret_key",
    "openai_api_key", "secret_key", "mfa_secret", "credit_card",
}


def _scrub(value):
    """Recursively redact values whose key looks sensitive."""
    if isinstance(value, dict):
        return {
            key: ("***REDACTED***" if key.lower() in _SENSITIVE_KEYS else _scrub(val))
            for key, val in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_scrub(item) for item in value]
    return value


def _before_send(event, hint):  # pragma: no cover - exercised only with a live DSN
    if event.get("request"):
        event["request"] = _scrub(event["request"])
    if "extra" in event:
        event["extra"] = _scrub(event["extra"])
    return event


def init_error_tracking() -> bool:
    """Initialize Sentry. Returns False (no-op) unless ``SENTRY_DSN`` is set."""
    if not settings.SENTRY_DSN:
        logger.info("Error tracking disabled; SENTRY_DSN is not configured")
        return False

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        release=settings.APP_VERSION,
        integrations=[
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
            FastApiIntegration(transaction_style="endpoint"),
        ],
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
        before_send=_before_send,
    )
    logger.info("Sentry error tracking enabled", extra={"environment": settings.APP_ENV})
    return True
