"""Tests for Stripe webhook API endpoints."""
import pytest
from app.models.organization import Organization
from app.models.subscription import Subscription
from datetime import datetime, timezone


@pytest.fixture
def webhook_fixtures(db_session):
    org = Organization(name="Webhook Org", slug="webhook-org", is_active=True, created_at=datetime.utcnow())
    db_session.add(org)
    db_session.commit()
    return {"org_id": org.id}


def test_webhook_missing_secret(client, monkeypatch):
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    response = client.post("/api/webhooks/stripe", content=b"{}", headers={"stripe-signature": "sig123"})
    assert response.status_code == 503


def test_webhook_missing_signature(client, monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    response = client.post("/api/webhooks/stripe", content=b"{}")
    assert response.status_code == 400


def test_checkout_session_completed_webhook(client, webhook_fixtures, monkeypatch, db_session):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")

    import stripe
    monkeypatch.setattr(stripe.Webhook, "construct_event", lambda payload, sig, secret: {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_hook123",
                "subscription": "sub_hook123",
                "metadata": {
                    "organization_id": str(webhook_fixtures["org_id"]),
                    "plan": "pro",
                },
            }
        }
    })

    response = client.post("/api/webhooks/stripe", content=b"{}", headers={"stripe-signature": "sig123"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    sub = db_session.query(Subscription).filter_by(organization_id=webhook_fixtures["org_id"]).first()
    assert sub is not None
    assert sub.stripe_customer_id == "cus_hook123"
    assert sub.stripe_subscription_id == "sub_hook123"
    assert sub.plan == "pro"


def test_subscription_updated_webhook(client, webhook_fixtures, monkeypatch, db_session):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")

    import stripe
    now_ts = int(datetime.now(timezone.utc).timestamp())
    monkeypatch.setattr(stripe.Webhook, "construct_event", lambda payload, sig, secret: {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_hook123",
                "customer": "cus_hook123",
                "status": "active",
                "current_period_start": now_ts,
                "current_period_end": now_ts + 86400 * 30,
                "cancel_at_period_end": False,
                "metadata": {
                    "organization_id": str(webhook_fixtures["org_id"]),
                    "plan": "enterprise",
                },
            }
        }
    })

    response = client.post("/api/webhooks/stripe", content=b"{}", headers={"stripe-signature": "sig123"})
    assert response.status_code == 200

    sub = db_session.query(Subscription).filter_by(organization_id=webhook_fixtures["org_id"]).first()
    assert sub is not None
    assert sub.plan == "enterprise"
    assert sub.status == "active"


def test_invoice_paid_and_failed_webhook(client, webhook_fixtures, monkeypatch, db_session):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    import stripe

    # Setup subscription in DB
    sub = Subscription(
        organization_id=webhook_fixtures["org_id"],
        stripe_customer_id="cus_invoice",
        stripe_subscription_id="sub_invoice",
        plan="pro",
        status="past_due",
        created_at=datetime.utcnow(),
    )
    db_session.add(sub)
    db_session.commit()

    # Invoice paid
    monkeypatch.setattr(stripe.Webhook, "construct_event", lambda payload, sig, secret: {
        "type": "invoice.paid",
        "data": {"object": {"subscription": "sub_invoice"}}
    })
    res1 = client.post("/api/webhooks/stripe", content=b"{}", headers={"stripe-signature": "sig123"})
    assert res1.status_code == 200

    db_session.refresh(sub)
    assert sub.status == "active"

    # Invoice payment failed
    monkeypatch.setattr(stripe.Webhook, "construct_event", lambda payload, sig, secret: {
        "type": "invoice.payment_failed",
        "data": {"object": {"subscription": "sub_invoice"}}
    })
    res2 = client.post("/api/webhooks/stripe", content=b"{}", headers={"stripe-signature": "sig123"})
    assert res2.status_code == 200

    db_session.refresh(sub)
    assert sub.status == "past_due"
