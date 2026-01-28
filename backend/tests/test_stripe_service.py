"""Tests for StripeService using the conftest stripe monkeypatch stubs."""
import pytest
import stripe

from app.services.stripe_service import StripeService


def test_create_customer_returns_stripe_customer():
    customer = StripeService().create_customer("a@b.com", "Acme", organization_id=7)
    assert customer.id == "cus_test"
    assert customer.email == "a@b.com"
    assert customer.metadata == {"organization_id": "7"}


def test_create_checkout_session_builds_subscription():
    session = StripeService().create_checkout_session(
        customer_id="cus_test",
        price_id="price_123",
        success_url="https://app/success",
        cancel_url="https://app/cancel",
        organization_id=3,
        plan="pro",
        trial_days=14,
    )
    assert session.id == "cs_test"
    assert session.url == "https://stripe.test/checkout"


def test_create_customer_portal_session():
    session = StripeService().create_customer_portal_session("cus_test", "https://app/return")
    assert session.url == "https://stripe.test/portal"


def test_get_and_cancel_subscription():
    svc = StripeService()
    sub = svc.get_subscription("sub_123")
    assert sub.status == "active"
    canceled = svc.cancel_subscription("sub_123")
    assert canceled.id == "sub_123"
    assert canceled.cancel_at_period_end is True


def test_create_price():
    price = StripeService().create_price("prod_1", unit_amount=2900, currency="usd", interval="month")
    assert price.id == "price_test"


def test_handle_webhook_returns_event():
    event = StripeService().handle_webhook(b"payload", "sig")
    assert event["type"] == "test.event"


def test_handle_webhook_invalid_signature(monkeypatch):
    def _boom(*args, **kwargs):
        raise stripe.error.SignatureVerificationError("bad", "sig")

    monkeypatch.setattr(stripe.Webhook, "construct_event", _boom)
    with pytest.raises(Exception):
        StripeService().handle_webhook(b"payload", "sig")
