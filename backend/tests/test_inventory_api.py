"""Tests for inventory API endpoints."""
import pytest
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.core.security import get_password_hash, create_access_token
from datetime import datetime


@pytest.fixture
def inv_fixtures(db_session):
    org = Organization(name="Inv Farm", slug="inv-farm", is_active=True, created_at=datetime.utcnow())
    other_org = Organization(name="Other Inv Farm", slug="other-inv-farm", is_active=True, created_at=datetime.utcnow())
    db_session.add_all([org, other_org])
    db_session.flush()

    manager = User(
        name="Inventory Manager",
        email="manager@inv.com",
        password_hash=get_password_hash("password123"),
        role="FARM_MANAGER",
        current_organization_id=org.id,
    )
    worker = User(
        name="Inventory Worker",
        email="worker@inv.com",
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


def test_inventory_auth(client):
    res1 = client.get("/api/inventory/items")
    assert res1.status_code == 401

    res2 = client.get("/api/inventory/low-stock")
    assert res2.status_code == 401


def test_create_and_get_items(client, inv_fixtures):
    headers = {"Authorization": f"Bearer {inv_fixtures['mgr_token']}"}
    item_payload = {
        "name": "Oyster Grain Spawn",
        "category": "SPAWN",
        "unit": "kg",
        "reorder_level": 10.0,
    }
    create_res = client.post("/api/inventory/items", json=item_payload, headers=headers)
    assert create_res.status_code == 200
    item = create_res.json()
    assert item["name"] == "Oyster Grain Spawn"
    assert item["current_stock"] == 0.0

    wrk_headers = {"Authorization": f"Bearer {inv_fixtures['wrk_token']}"}
    list_res = client.get("/api/inventory/items", headers=wrk_headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 1


def test_record_inventory_transactions(client, inv_fixtures):
    mgr_headers = {"Authorization": f"Bearer {inv_fixtures['mgr_token']}"}
    item = client.post("/api/inventory/items", json={
        "name": "Autoclave Bags",
        "category": "GROW_BAG",
        "unit": "units",
        "reorder_level": 50.0,
    }, headers=mgr_headers).json()

    wrk_headers = {"Authorization": f"Bearer {inv_fixtures['wrk_token']}"}
    # Transaction IN
    tx1 = client.post("/api/inventory/transactions", json={
        "item_id": item["id"],
        "transaction_type": "IN",
        "quantity": 100.0,
        "notes": "Received shipment",
    }, headers=wrk_headers)
    assert tx1.status_code == 200

    # Transaction OUT
    tx2 = client.post("/api/inventory/transactions", json={
        "item_id": item["id"],
        "transaction_type": "OUT",
        "quantity": 60.0,
        "notes": "Used in batch inoculation",
    }, headers=wrk_headers)
    assert tx2.status_code == 200

    # Check low stock endpoint (40 left, reorder level is 50 -> low stock!)
    low_res = client.get("/api/inventory/low-stock", headers=mgr_headers)
    assert low_res.status_code == 200
    low_items = low_res.json()
    assert any(i["id"] == item["id"] for i in low_items)
