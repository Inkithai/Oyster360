"""Subscription lifecycle tests for :class:`BillingService`.

These exercise the database synchronisation layer that Stripe webhooks drive.
Everything runs against the in-memory SQLite session from ``conftest.py`` — no
Stripe credentials, no network access.
"""
from datetime import datetime, timedelta

import pytest

from app.models.organization import Organization
from app.models.subscription import Subscription
from app.services.billing_service import BillingService


@pytest.fixture
def organizations(db_session):
    org_a = Organization(name="Org A", slug="billing-org-a", created_at=datetime.utcnow())
    org_b = Organization(name="Org B", slug="billing-org-b", created_at=datetime.utcnow())
    db_session.add_all([org_a, org_b])
    db_session.commit()
    return org_a, org_b


def test_create_subscription_persists_trial_period(db_session, organizations):
    org, _ = organizations
    service = BillingService(db_session)

    subscription = service.create_subscription(
        organization_id=org.id,
        stripe_customer_id="cus_1",
        stripe_subscription_id="sub_1",
        plan="pro",
    )

    assert subscription.id is not None
    assert subscription.plan == "pro"
    assert subscription.status == "trialing"
    assert subscription.current_period_end > subscription.current_period_start
    delta = subscription.current_period_end - subscription.current_period_start
    assert delta == timedelta(days=30)


def test_create_subscription_is_idempotent_for_webhook_retries(db_session, organizations):
    """Stripe retries deliveries; a retry must update, never duplicate."""
    org, _ = organizations
    service = BillingService(db_session)

    first = service.create_subscription(org.id, "cus_1", "sub_1", "starter")
    second = service.create_subscription(org.id, "cus_1", "sub_1", "pro", status="active")

    assert first.id == second.id
    assert second.plan == "pro"
    assert second.status == "active"
    assert db_session.query(Subscription).count() == 1


def test_create_subscription_replaces_plan_on_upgrade(db_session, organizations):
    """An organization upgrading gets a new Stripe subscription id, not a new row."""
    org, _ = organizations
    service = BillingService(db_session)

    service.create_subscription(org.id, "cus_1", "sub_old", "starter", status="active")
    upgraded = service.create_subscription(org.id, "cus_1", "sub_new", "enterprise", status="active")

    assert db_session.query(Subscription).count() == 1
    assert upgraded.stripe_subscription_id == "sub_new"
    assert upgraded.plan == "enterprise"


def test_subscriptions_are_isolated_per_organization(db_session, organizations):
    org_a, org_b = organizations
    service = BillingService(db_session)

    service.create_subscription(org_a.id, "cus_a", "sub_a", "pro", status="active")
    service.create_subscription(org_b.id, "cus_b", "sub_b", "starter", status="active")

    assert service.get_active_subscription(org_a.id).plan == "pro"
    assert service.get_active_subscription(org_b.id).plan == "starter"


def test_sync_subscription_applies_stripe_period_and_cancellation(db_session, organizations):
    org, _ = organizations
    service = BillingService(db_session)
    period_start = datetime(2026, 1, 1)
    period_end = datetime(2026, 2, 1)

    subscription = service.sync_subscription(
        organization_id=org.id,
        stripe_customer_id="cus_1",
        stripe_subscription_id="sub_1",
        plan="pro",
        status="active",
        current_period_start=period_start,
        current_period_end=period_end,
        cancel_at_period_end=True,
    )

    assert subscription.current_period_start == period_start
    assert subscription.current_period_end == period_end
    assert subscription.cancel_at_period_end is True


def test_sync_subscription_keeps_default_period_when_stripe_omits_it(db_session, organizations):
    org, _ = organizations
    service = BillingService(db_session)

    subscription = service.sync_subscription(
        organization_id=org.id,
        stripe_customer_id="cus_1",
        stripe_subscription_id="sub_1",
        plan="pro",
        status="active",
    )

    assert subscription.current_period_start is not None
    assert subscription.current_period_end is not None
    assert subscription.cancel_at_period_end is False


def test_update_subscription_status_marks_payment_failure(db_session, organizations):
    org, _ = organizations
    service = BillingService(db_session)
    service.create_subscription(org.id, "cus_1", "sub_1", "pro", status="active")

    updated = service.update_subscription_status("sub_1", "past_due")

    assert updated.status == "past_due"
    assert service.get_active_subscription(org.id) is None


def test_update_subscription_status_for_unknown_subscription_returns_none(db_session):
    assert BillingService(db_session).update_subscription_status("sub_missing", "active") is None


@pytest.mark.parametrize("status", ["active", "trialing"])
def test_get_active_subscription_accepts_entitled_states(db_session, organizations, status):
    org, _ = organizations
    service = BillingService(db_session)
    service.create_subscription(org.id, "cus_1", "sub_1", "pro", status=status)

    assert service.get_active_subscription(org.id) is not None


@pytest.mark.parametrize("status", ["canceled", "incomplete", "past_due", "unpaid"])
def test_get_active_subscription_rejects_unentitled_states(db_session, organizations, status):
    org, _ = organizations
    service = BillingService(db_session)
    service.create_subscription(org.id, "cus_1", "sub_1", "pro", status=status)

    assert service.get_active_subscription(org.id) is None


def test_get_active_subscription_without_any_subscription(db_session, organizations):
    org, _ = organizations
    assert BillingService(db_session).get_active_subscription(org.id) is None
