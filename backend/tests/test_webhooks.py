"""Tests for the verified Stripe webhook API (app.api.webhooks)."""
import pytest
import stripe
from fastapi.testclient import TestClient

from app.main import app
from app.database.database import get_db
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.api import webhooks as webhooks_module


@pytest.fixture()
def client(db_session, monkeypatch):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_wh")
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _event(event_type: str, obj: dict) -> dict:
    return {"type": event_type, "data": {"object": obj}}


def _post(client, event):
    """Post a webhook request with a stubbed valid Stripe signature."""
    original = stripe.Webhook.construct_event
    stripe.Webhook.construct_event = lambda *a, **k: event
    try:
        return client.post(
            "/api/webhooks/stripe",
            content=b"{}",
            headers={"stripe-signature": "t=1,v1=stub"},
        )
    finally:
        stripe.Webhook.construct_event = original


@pytest.fixture()
def org_with_subscription(db_session):
    org = Organization(name="Hooked Farms", slug="hooked-farms")
    db_session.add(org)
    db_session.flush()
    sub = Subscription(organization_id=org.id, plan="starter", status="incomplete")
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(org)
    db_session.refresh(sub)
    return org, sub


class TestWebhookVerification:
    def test_returns_503_when_webhooks_not_configured(self, db_session, client, monkeypatch):
        monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
        response = client.post("/api/webhooks/stripe", content=b"{}")
        assert response.status_code == 503
        assert "not configured" in response.json()["detail"]

    def test_returns_400_when_signature_header_missing(self, client):
        response = client.post("/api/webhooks/stripe", content=b"{}")
        assert response.status_code == 400
        assert response.json()["detail"] == "Missing Stripe signature"

    def test_returns_400_on_invalid_signature(self, client, monkeypatch):
        def reject(*args, **kwargs):
            raise stripe.SignatureVerificationError("bad sig", "payload")

        monkeypatch.setattr(stripe.Webhook, "construct_event", reject)
        response = client.post(
            "/api/webhooks/stripe",
            content=b"{}",
            headers={"stripe-signature": "t=1,v1=bad"},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid signature"

    def test_returns_400_on_invalid_payload(self, client, monkeypatch):
        def reject(*args, **kwargs):
            raise ValueError("not json")

        monkeypatch.setattr(stripe.Webhook, "construct_event", reject)
        response = client.post(
            "/api/webhooks/stripe",
            content=b"not-json",
            headers={"stripe-signature": "t=1,v1=bad"},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid payload"


class TestWebhookEvents:
    def test_checkout_completed_creates_subscription(self, client, org_with_subscription):
        org, _ = org_with_subscription
        response = _post(
            client,
            _event(
                "checkout.session.completed",
                {
                    "customer": "cus_hook",
                    "subscription": "sub_hook",
                    "metadata": {"organization_id": str(org.id), "plan": "pro"},
                },
            ),
        )
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

    def test_missing_organization_metadata_is_rejected(self, client):
        response = _post(
            client,
            _event("checkout.session.completed", {"customer": "cus_x"}),
        )
        assert response.status_code == 400
        assert "organization metadata" in response.json()["detail"]

    def test_unknown_organization_is_rejected(self, client):
        response = _post(
            client,
            _event(
                "checkout.session.completed",
                {"customer": "cus_x", "metadata": {"organization_id": "99999"}},
            ),
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Unknown organization"

    def test_incomplete_checkout_session_is_rejected(self, client, org_with_subscription):
        org, _ = org_with_subscription
        response = _post(
            client,
            _event(
                "checkout.session.completed",
                {"customer": "cus_hook", "metadata": {"organization_id": str(org.id)}},
            ),
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Incomplete checkout session"

    def test_subscription_updated_syncs_status_and_period(self, db_session, client, org_with_subscription):
        org, _ = org_with_subscription
        response = _post(
            client,
            _event(
                "customer.subscription.updated",
                {
                    "id": "sub_hook",
                    "customer": "cus_hook",
                    "status": "active",
                    "metadata": {"organization_id": str(org.id), "plan": "pro"},
                    "current_period_start": 1700000000,
                    "current_period_end": 1702592000,
                    "cancel_at_period_end": True,
                },
            ),
        )
        assert response.status_code == 200

        subscription = (
            db_session.query(Subscription)
            .filter(Subscription.organization_id == org.id)
            .one()
        )
        assert subscription.status == "active"
        assert subscription.plan == "pro"
        assert subscription.stripe_subscription_id == "sub_hook"
        assert subscription.current_period_start.year == 2023
        assert subscription.cancel_at_period_end is True

    def test_invoice_paid_marks_subscription_active(self, client, org_with_subscription, monkeypatch):
        org, sub = org_with_subscription
        synced = {}
        monkeypatch.setattr(
            webhooks_module.BillingService,
            "update_subscription_status",
            lambda self, sid, status: synced.update(sid=sid, status=status) or True,
        )
        response = _post(
            client,
            _event("invoice.paid", {"subscription": "sub_hook"}),
        )
        assert response.status_code == 200
        assert synced == {"sid": "sub_hook", "status": "active"}

    def test_invoice_payment_failed_marks_past_due(self, client, monkeypatch):
        synced = {}
        monkeypatch.setattr(
            webhooks_module.BillingService,
            "update_subscription_status",
            lambda self, sid, status: synced.update(sid=sid, status=status) or True,
        )
        response = _post(
            client,
            _event("invoice.payment_failed", {"subscription": "sub_late"}),
        )
        assert response.status_code == 200
        assert synced == {"sid": "sub_late", "status": "past_due"}

    def test_ignored_event_types_succeed_without_side_effects(self, client):
        response = _post(client, _event("charge.dispute.created", {"id": "dp_1"}))
        assert response.status_code == 200


class TestTimestampHelper:
    def test_timestamp_converts_to_utc_naive(self):
        result = webhooks_module._timestamp(1700000000)
        assert result is not None
        assert result.tzinfo is None
        assert result.year == 2023

    def test_timestamp_handles_missing_values(self):
        assert webhooks_module._timestamp(None) is None
        assert webhooks_module._timestamp(0) is None
