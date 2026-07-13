"""Tests for Sentry error tracking wiring (app.core.error_tracking)."""
import logging

import sentry_sdk

from app.core import error_tracking
from app.core.config import settings


def test_init_is_noop_without_dsn(monkeypatch):
    """With SENTRY_DSN unset, init must be a no-op and return False."""
    monkeypatch.setattr(settings, "SENTRY_DSN", None)

    called = {"count": 0}

    def fake_init(*args, **kwargs):
        called["count"] += 1

    monkeypatch.setattr(sentry_sdk, "init", fake_init)

    assert error_tracking.init_error_tracking() is False
    assert called["count"] == 0


def test_init_calls_sentry_when_dsn_set(monkeypatch):
    """With SENTRY_DSN configured, init must call sentry_sdk.init and return True."""
    monkeypatch.setattr(settings, "SENTRY_DSN", "https://abc@example.io/123")

    captured = {}

    def fake_init(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(sentry_sdk, "init", fake_init)

    assert error_tracking.init_error_tracking() is True
    assert captured["dsn"] == "https://abc@example.io/123"
    assert captured["send_default_pii"] is False
    assert callable(captured["before_send"])
    # PII scrubbing must be wired in.
    assert captured["before_send"] is error_tracking._before_send


def test_scrub_redacts_sensitive_keys():
    scrubbed = error_tracking._scrub({
        "password": "hunter2",
        "email": "user@example.com",  # not sensitive -> kept
        "nested": {"api_key": "sk_live", "ok": 1},
        "list": [{"token": "t"}, {"keep": 2}],
    })
    assert scrubbed["password"] == "***REDACTED***"
    assert scrubbed["email"] == "user@example.com"
    assert scrubbed["nested"]["api_key"] == "***REDACTED***"
    assert scrubbed["nested"]["ok"] == 1
    assert scrubbed["list"][0]["token"] == "***REDACTED***"
    assert scrubbed["list"][1]["keep"] == 2


def test_before_send_invokes_scrub(monkeypatch):
    monkeypatch.setattr(settings, "SENTRY_DSN", "https://k@host/1")
    event = {"request": {"headers": {"authorization": "Bearer x"}}, "extra": {}}
    cleaned = error_tracking._before_send(event, {})
    assert cleaned["request"]["headers"]["authorization"] == "***REDACTED***"
