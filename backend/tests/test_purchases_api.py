"""Tests for purchases and supplier API endpoints."""
import pytest
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.core.security import get_password_hash, create_access_token
from datetime import datetime, timedelta


@pytest.fixture
def purchase_fixtures(db_session):
    org = Organization(name="Purchase Farm", slug="purchase-farm", is_active=True, created_at=datetime.utcnow())
    other_org = Organization(name="Other Farm", slug="other-farm", is_active=True, created_at=datetime.utcnow())
    db_session.add_all([org, other_org])
    db_session.flush()

    manager = User(
        name="Purchasing Manager",
        email="manager@purchase.com",
        password_hash=get_password_hash("password123"),
        role="FARM_MANAGER",
        current_organization_id=org.id,
    )
    worker = User(
        name="Purchasing Worker",
        email="worker@purchase.com",
        password_hash=get_password_hash("password123"),
        role="WORKER",
        current_organization_id=org.id,
    )
    db_session.add_all([manager, worker])
    db_session.flush()

    db_session.add(OrganizationMember(organization_id=org.id, user_id=manager.id, role="OWNER", joined_at=datetime.utcnow()))
    db_session.add(OrganizationMember(organization_id=org.id, user_id=worker.id, role="MEMBER", joined_at=datetime.utcnow()))
    db_session.commit()

    mgr_token = create_access_token({"sub": str(manager.id), "role": manager.role})
    wrk_token = create_access_token({"sub": str(worker.id), "role": worker.role})

    return {
        "org_id": org.id,
        "mgr_token": mgr_token,
        "wrk_token": wrk_token,
    }


def test_purchases_auth(client):
    res1 = client.get("/api/purchases/suppliers")
    assert res1.status_code == 401

    res2 = client.get("/api/purchases/orders")
    assert res2.status_code == 401


def test_create_and_get_suppliers(client, purchase_fixtures):
    headers = {"Authorization": f"Bearer {purchase_fixtures['mgr_token']}"}
    supplier_payload = {
        "name": "Myco Supply Co",
        "contact_person": "Jane Doe",
        "phone": "+1-555-0100",
        "email": "jane@mycosupply.com",
    }
    create_res = client.post("/api/purchases/suppliers", json=supplier_payload, headers=headers)
    assert create_res.status_code == 200
    supplier = create_res.json()
    assert supplier["name"] == "Myco Supply Co"

    wrk_headers = {"Authorization": f"Bearer {purchase_fixtures['wrk_token']}"}
    list_res = client.get("/api/purchases/suppliers", headers=wrk_headers)
    assert list_res.status_code == 200
    suppliers = list_res.json()
    assert len(suppliers) >= 1
    assert any(s["name"] == "Myco Supply Co" for s in suppliers)


def test_create_and_get_purchase_orders(client, purchase_fixtures):
    headers = {"Authorization": f"Bearer {purchase_fixtures['mgr_token']}"}
    # Create supplier first
    supplier = client.post("/api/purchases/suppliers", json={
        "name": "Grain Master",
        "contact_person": "Bob",
        "phone": "555-0199",
        "email": "bob@grain.com",
    }, headers=headers).json()

    expected = (datetime.utcnow() + timedelta(days=7)).isoformat()
    order_payload = {
        "supplier_id": supplier["id"],
        "items": [
            {"name": "Millet 50lb bag", "quantity": 10.0, "unit_price": 25.0},
            {"name": "Rye Grain 50lb bag", "quantity": 5.0, "unit_price": 30.0},
        ],
        "expected_date": expected,
    }
    create_res = client.post("/api/purchases/orders", json=order_payload, headers=headers)
    assert create_res.status_code == 200
    order = create_res.json()
    assert order["total_amount"] == (10.0 * 25.0) + (5.0 * 30.0)

    list_res = client.get("/api/purchases/orders", headers=headers)
    assert list_res.status_code == 200
    orders = list_res.json()
    assert len(orders) >= 1
