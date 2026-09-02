"""Tests for billing and subscription API endpoints."""
import pytest
from app.models.subscription import Subscription
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.core.security import get_password_hash, create_access_token
from datetime import datetime, timedelta


@pytest.fixture
def billing_fixtures(db_session):
    org = Organization(name="Billing Farm", slug="billing-farm", is_active=True, created_at=datetime.utcnow())
    other_org = Organization(name="Other Farm", slug="other-farm", is_active=True, created_at=datetime.utcnow())
    db_session.add_all([org, other_org])
    db_session.flush()

    manager = User(
        name="Manager User",
        email="manager@billing.com",
        password_hash=get_password_hash("password123"),
        role="FARM_MANAGER",
        current_organization_id=org.id,
    )
    worker = User(
        name="Worker User",
        email="worker@billing.com",
        password_hash=get_password_hash("password123"),
        role="WORKER",
        current_organization_id=org.id,
    )
    db_session.add_all([manager, worker])
    db_session.flush()

    db_session.add(OrganizationMember(organization_id=org.id, user_id=manager.id, role="OWNER", joined_at=datetime.utcnow()))
    db_session.add(OrganizationMember(organization_id=org.id, user_id=worker.id, role="MEMBER", joined_at=datetime.utcnow()))
    db_session.commit()

    manager_token = create_access_token({"sub": str(manager.id), "role": manager.role})
    worker_token = create_access_token({"sub": str(worker.id), "role": worker.role})

    return {
        "org_id": org.id,
        "manager_token": manager_token,
        "worker_token": worker_token,
        "manager_id": manager.id,
    }


def test_unauthenticated_requests_are_rejected(client):
    res1 = client.post("/api/billing/create-checkout-session", json={
        "plan": "starter",
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
    })
    assert res1.status_code == 401

    res2 = client.get("/api/billing/subscription")
    assert res2.status_code == 401

    res3 = client.post("/api/billing/cancel-subscription")
    assert res3.status_code == 401


def test_workers_are_rejected_from_billing(client, billing_fixtures):
    headers = {"Authorization": f"Bearer {billing_fixtures['worker_token']}"}

    res1 = client.post("/api/billing/create-checkout-session", json={
        "plan": "pro",
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
    }, headers=headers)
    assert res1.status_code == 403

    res2 = client.get("/api/billing/subscription", headers=headers)
    assert res2.status_code == 403


def test_create_checkout_session_new_customer(client, billing_fixtures):
    headers = {"Authorization": f"Bearer {billing_fixtures['manager_token']}"}
    response = client.post("/api/billing/create-checkout-session", json={
        "plan": "starter",
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
    }, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "checkout_url" in data
    assert "stripe.test" in data["checkout_url"]


def test_create_checkout_session_existing_customer(client, billing_fixtures, db_session):
    org_id = billing_fixtures["org_id"]
    sub = Subscription(
        organization_id=org_id,
        stripe_customer_id="cus_existing123",
        plan="starter",
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        created_at=datetime.utcnow(),
    )
    db_session.add(sub)
    db_session.commit()

    headers = {"Authorization": f"Bearer {billing_fixtures['manager_token']}"}
    response = client.post("/api/billing/create-checkout-session", json={
        "plan": "enterprise",
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
    }, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "checkout_url" in data


def test_get_subscription_not_found(client, billing_fixtures):
    headers = {"Authorization": f"Bearer {billing_fixtures['manager_token']}"}
    response = client.get("/api/billing/subscription", headers=headers)
    assert response.status_code == 404


def test_get_subscription_success(client, billing_fixtures, db_session):
    org_id = billing_fixtures["org_id"]
    sub = Subscription(
        organization_id=org_id,
        stripe_customer_id="cus_sub123",
        stripe_subscription_id="sub_123",
        plan="pro",
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        cancel_at_period_end=False,
        created_at=datetime.utcnow(),
    )
    db_session.add(sub)
    db_session.commit()

    headers = {"Authorization": f"Bearer {billing_fixtures['manager_token']}"}
    response = client.get("/api/billing/subscription", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["plan"] == "pro"
    assert data["status"] == "active"
    assert data["cancel_at_period_end"] is False


def test_cancel_subscription_success(client, billing_fixtures, db_session):
    org_id = billing_fixtures["org_id"]
    sub = Subscription(
        organization_id=org_id,
        stripe_customer_id="cus_cancel123",
        stripe_subscription_id="sub_cancel123",
        plan="pro",
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        cancel_at_period_end=False,
        created_at=datetime.utcnow(),
    )
    db_session.add(sub)
    db_session.commit()

    headers = {"Authorization": f"Bearer {billing_fixtures['manager_token']}"}
    response = client.post("/api/billing/cancel-subscription", headers=headers)
    assert response.status_code == 200
    assert "canceled at the end" in response.json()["message"]

    db_session.refresh(sub)
    assert sub.cancel_at_period_end is True


def test_cancel_subscription_not_found(client, billing_fixtures):
    headers = {"Authorization": f"Bearer {billing_fixtures['manager_token']}"}
    response = client.post("/api/billing/cancel-subscription", headers=headers)
    assert response.status_code == 404
