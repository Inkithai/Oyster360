"""Optional production error tracking.

Sentry is disabled by default and never receives test or local data unless a DSN is
explicitly configured.
"""

import logging

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.core.config import settings

logger = logging.getLogger(__name__)


def init_error_tracking() -> bool:
    if not settings.SENTRY_DSN:
        logger.info("Error tracking disabled; SENTRY_DSN is not configured")
        return False

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        release=settings.APP_VERSION,
        integrations=[FastApiIntegration(transaction_style="endpoint")],
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
    )
    logger.info("Sentry error tracking enabled", extra={"environment": settings.APP_ENV})
    return True
