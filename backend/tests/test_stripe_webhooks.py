"""End-to-end tests for the Stripe webhook endpoint.

Signature verification is stubbed per-test so the payload under test is
returned verbatim; no Stripe account, secret or network call is involved.
Covered: success, signature failure, missing configuration, unknown tenant,
malformed metadata, idempotent redelivery and payment-failure handling.
"""
from datetime import datetime

import pytest
import stripe

from app.models.organization import Organization
from app.models.subscription import Subscription
from app.services.billing_service import BillingService

WEBHOOK_URL = "/api/webhooks/stripe"
HEADERS = {"stripe-signature": "t=1,v1=stub"}


@pytest.fixture(autouse=True)
def webhook_secret(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")


@pytest.fixture
def organization(db_session):
    org = Organization(name="Webhook Org", slug="webhook-org", created_at=datetime.utcnow())
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def deliver(client, monkeypatch):
    """Post an event to the webhook endpoint with signature verification stubbed."""

    def _deliver(event: dict, headers: dict | None = None):
        monkeypatch.setattr(
            stripe.Webhook,
            "construct_event",
            lambda payload, signature, secret: event,
        )
        return client.post(
            WEBHOOK_URL,
            content=b"{}",
            headers=HEADERS if headers is None else headers,
        )

    return _deliver


def _checkout_event(organization_id: int, plan: str = "pro") -> dict:
    return {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_1",
                "subscription": "sub_1",
                "metadata": {"organization_id": str(organization_id), "plan": plan},
            }
        },
    }


def _subscription_event(event_type: str, organization_id: int, **overrides) -> dict:
    obj = {
        "id": "sub_1",
        "customer": "cus_1",
        "status": "active",
        "current_period_start": 1_767_225_600,
        "current_period_end": 1_769_904_000,
        "cancel_at_period_end": False,
        "metadata": {"organization_id": str(organization_id), "plan": "pro"},
    }
    obj.update(overrides)
    return {"type": event_type, "data": {"object": obj}}


def test_checkout_completed_creates_trialing_subscription(db_session, organization, deliver):
    response = deliver(_checkout_event(organization.id))

    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    subscription = BillingService(db_session).get_active_subscription(organization.id)
    assert subscription.plan == "pro"
    assert subscription.status == "trialing"
    assert subscription.stripe_subscription_id == "sub_1"


def test_checkout_completed_defaults_plan_when_missing(db_session, organization, deliver):
    event = _checkout_event(organization.id)
    event["data"]["object"]["metadata"].pop("plan")

    assert deliver(event).status_code == 200
    assert BillingService(db_session).get_active_subscription(organization.id).plan == "starter"


def test_redelivered_checkout_event_is_idempotent(db_session, organization, deliver):
    assert deliver(_checkout_event(organization.id)).status_code == 200
    assert deliver(_checkout_event(organization.id)).status_code == 200

    assert db_session.query(Subscription).count() == 1


def test_checkout_without_subscription_id_is_rejected(db_session, organization, deliver):
    event = _checkout_event(organization.id)
    event["data"]["object"]["subscription"] = None

    response = deliver(event)

    assert response.status_code == 400
    assert "Incomplete checkout session" in response.json()["detail"]
    assert db_session.query(Subscription).count() == 0


def test_event_for_unknown_organization_is_rejected(db_session, organization, deliver):
    response = deliver(_checkout_event(organization.id + 4242))

    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown organization"
    assert db_session.query(Subscription).count() == 0


@pytest.mark.parametrize("organization_id", [None, "", "not-a-number"])
def test_event_with_malformed_organization_metadata_is_rejected(
    db_session, organization, deliver, organization_id
):
    event = _checkout_event(organization.id)
    event["data"]["object"]["metadata"]["organization_id"] = organization_id

    response = deliver(event)

    assert response.status_code == 400
    assert "organization metadata" in response.json()["detail"]


def test_event_with_absent_organization_metadata_key_is_rejected(
    db_session, organization, deliver
):
    """The key is missing entirely, not just malformed."""
    event = _checkout_event(organization.id)
    event["data"]["object"]["metadata"] = {"plan": "pro"}

    response = deliver(event)

    assert response.status_code == 400
    assert "organization metadata" in response.json()["detail"]
    assert db_session.query(Subscription).count() == 0


def test_event_with_no_metadata_at_all_is_rejected(db_session, organization, deliver):
    event = _checkout_event(organization.id)
    event["data"]["object"].pop("metadata")

    response = deliver(event)

    assert response.status_code == 400
    assert db_session.query(Subscription).count() == 0


def test_subscription_updated_syncs_period_and_cancellation(db_session, organization, deliver):
    deliver(_checkout_event(organization.id))

    response = deliver(
        _subscription_event(
            "customer.subscription.updated", organization.id, cancel_at_period_end=True
        )
    )

    assert response.status_code == 200
    subscription = db_session.query(Subscription).one()
    assert subscription.status == "active"
    assert subscription.cancel_at_period_end is True
    assert subscription.current_period_start == datetime.utcfromtimestamp(1_767_225_600)
    assert subscription.current_period_end == datetime.utcfromtimestamp(1_769_904_000)


def test_subscription_deleted_defaults_to_canceled(db_session, organization, deliver):
    deliver(_checkout_event(organization.id))
    event = _subscription_event("customer.subscription.deleted", organization.id)
    event["data"]["object"].pop("status")

    assert deliver(event).status_code == 200
    assert db_session.query(Subscription).one().status == "canceled"
    assert BillingService(db_session).get_active_subscription(organization.id) is None


def test_invoice_paid_reactivates_subscription(db_session, organization, deliver):
    deliver(_checkout_event(organization.id))
    BillingService(db_session).update_subscription_status("sub_1", "past_due")

    response = deliver(
        {"type": "invoice.paid", "data": {"object": {"subscription": "sub_1"}}}
    )

    assert response.status_code == 200
    assert db_session.query(Subscription).one().status == "active"


def test_invoice_payment_failed_marks_past_due(db_session, organization, deliver):
    deliver(_checkout_event(organization.id))

    response = deliver(
        {"type": "invoice.payment_failed", "data": {"object": {"subscription": "sub_1"}}}
    )

    assert response.status_code == 200
    assert db_session.query(Subscription).one().status == "past_due"
    assert BillingService(db_session).get_active_subscription(organization.id) is None


def test_invoice_event_without_subscription_is_ignored(db_session, organization, deliver):
    response = deliver({"type": "invoice.paid", "data": {"object": {}}})

    assert response.status_code == 200
    assert db_session.query(Subscription).count() == 0


def test_unhandled_event_types_are_acknowledged(db_session, organization, deliver):
    response = deliver({"type": "customer.created", "data": {"object": {}}})

    assert response.status_code == 200
    assert db_session.query(Subscription).count() == 0


def test_missing_signature_header_is_rejected(client, organization):
    response = client.post(WEBHOOK_URL, content=b"{}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Missing Stripe signature"


def test_unconfigured_webhook_secret_returns_service_unavailable(
    client, organization, monkeypatch
):
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)

    response = client.post(WEBHOOK_URL, content=b"{}", headers=HEADERS)

    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_invalid_signature_is_rejected(client, organization, monkeypatch):
    def raise_signature_error(payload, signature, secret):
        raise stripe.SignatureVerificationError("bad signature", signature)

    monkeypatch.setattr(stripe.Webhook, "construct_event", raise_signature_error)

    response = client.post(WEBHOOK_URL, content=b"{}", headers=HEADERS)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid signature"


def test_malformed_payload_is_rejected(client, organization, monkeypatch):
    def raise_value_error(payload, signature, secret):
        raise ValueError("not json")

    monkeypatch.setattr(stripe.Webhook, "construct_event", raise_value_error)

    response = client.post(WEBHOOK_URL, content=b"not json", headers=HEADERS)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid payload"
