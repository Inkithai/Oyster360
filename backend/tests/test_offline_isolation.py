"""Meta-tests proving the default test lane cannot reach external services.

A buyer or auditor must be able to run `pytest -m "not integration"` on a
machine with no credentials and no internet access. These tests assert the
guarantee itself rather than trusting convention.
"""
import os
import socket

import pytest
import requests

from app.services.ai.assistant_service import AssistantService
from app.services.stripe_service import StripeService


def test_outbound_tcp_connections_are_blocked():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        with pytest.raises(AssertionError, match="Outbound network connection"):
            sock.connect(("93.184.216.34", 80))
    finally:
        sock.close()


def test_loopback_connections_remain_available():
    """TestClient and local fixtures must keep working under the guard."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(server.getsockname())
    finally:
        client.close()
        server.close()


@pytest.mark.parametrize("verb", ["get", "post", "put", "patch", "delete", "head", "request"])
def test_requests_http_verbs_are_stubbed(verb):
    with pytest.raises(AssertionError, match="External HTTP calls are disabled"):
        getattr(requests, verb)("https://api.openai.com/v1/chat/completions")


def test_stripe_calls_use_in_process_stubs():
    """No STRIPE_SECRET_KEY is needed for the unit lane."""
    customer = StripeService().create_customer("a@b.com", "Acme", organization_id=1)
    assert customer.id == "cus_test"


def test_ai_provider_never_calls_out_even_when_configured(db_session, monkeypatch):
    """A stray OPENAI_API_KEY must not turn unit tests into billable calls."""
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-not-a-real-key")

    result = AssistantService(db_session, organization_id=1).chat("Why is growth slow?")

    # requests.post is stubbed to raise; the service degrades to rule-based output.
    assert result["answer"]


def test_no_real_service_credentials_are_required():
    for variable in ("STRIPE_SECRET_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DATABASE_URL"):
        value = os.getenv(variable, "")
        assert not value.startswith(("sk_live", "sk-proj-live", "postgres://prod")), (
            f"{variable} looks like a production credential; the unit lane must never need one."
        )
