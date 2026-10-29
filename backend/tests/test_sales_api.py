"""Tests for Sri Lankan Harvest Sales, Buyers, Payment Status & Stock Summary API."""
from datetime import datetime

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.batch import Batch, BatchStage
from app.models.harvest import Harvest
from app.models.organization import Organization, OrganizationMember
from app.models.user import User


@pytest.fixture
def sales_farm(db_session):
    org_a = Organization(name="Colombo Mushroom Co", slug="colombo-mush", created_at=datetime.utcnow())
    org_b = Organization(name="Galle Mushroom Co", slug="galle-mush", created_at=datetime.utcnow())
    db_session.add_all([org_a, org_b])
    db_session.flush()

    worker_a = User(
        name="Sales Worker A",
        email="sales_a@farm.lk",
        password_hash=get_password_hash("password123"),
        role="FARM_MANAGER",
        current_organization_id=org_a.id,
    )
    worker_b = User(
        name="Sales Worker B",
        email="sales_b@farm.lk",
        password_hash=get_password_hash("password123"),
        role="FARM_MANAGER",
        current_organization_id=org_b.id,
    )
    db_session.add_all([worker_a, worker_b])
    db_session.flush()

    db_session.add_all([
        OrganizationMember(organization_id=org_a.id, user_id=worker_a.id, role="OWNER"),
        OrganizationMember(organization_id=org_b.id, user_id=worker_b.id, role="OWNER"),
    ])

    batch_a = Batch(
        batch_number="SALE-BATCH-1",
        organization_id=org_a.id,
        current_stage=BatchStage.HARVEST,
        status="active",
        start_date=datetime.utcnow(),
    )
    db_session.add(batch_a)
    db_session.flush()

    harvest_a = Harvest(
        batch_id=batch_a.id,
        organization_id=org_a.id,
        flush_number=1,
        quantity_kg=100.0,
        unsold_kg=10.0,
        spoiled_kg=5.0,
        quality_score=95.0,
        selling_price=650.0,
        harvest_date=datetime.utcnow(),
    )
    db_session.add(harvest_a)
    db_session.commit()

    token_a = create_access_token({"sub": str(worker_a.id), "role": worker_a.role})
    token_b = create_access_token({"sub": str(worker_b.id), "role": worker_b.role})
    return {
        "batch_a": batch_a.id,
        "harvest_a": harvest_a.id,
        "headers_a": {"Authorization": f"Bearer {token_a}"},
        "headers_b": {"Authorization": f"Bearer {token_b}"},
    }


def test_buyer_and_sale_lifecycle_with_payment_tracking(client, sales_farm):
    # 1. Create a buyer
    buyer_res = client.post(
        "/api/sales/buyers",
        json={
            "name": "Cargills Food City — Nugegoda",
            "buyer_type": "RETAILER",
            "phone": "011-2820000",
            "location": "Nugegoda",
            "notes": "Weekly 200g packs",
        },
        headers=sales_farm["headers_a"],
    )
    assert buyer_res.status_code == 200
    buyer_id = buyer_res.json()["id"]

    # 2. Record a partial-payment sale (40 kg @ 650 LKR = 26,000 LKR; 16,000 paid)
    sale_res = client.post(
        "/api/sales/orders",
        json={
            "buyer_id": buyer_id,
            "batch_id": sales_farm["batch_a"],
            "harvest_id": sales_farm["harvest_a"],
            "quantity_kg": 40.0,
            "price_per_kg_lkr": 650.0,
            "amount_paid_lkr": 16000.0,
            "notes": "Morning delivery",
        },
        headers=sales_farm["headers_a"],
    )
    assert sale_res.status_code == 200
    sale_data = sale_res.json()
    assert sale_data["total_amount_lkr"] == 26000.0
    assert sale_data["amount_paid_lkr"] == 16000.0
    assert sale_data["balance_due_lkr"] == 10000.0
    assert sale_data["payment_status"] == "PARTIAL"

    # 3. Check buyer summary & repeat order history
    buyers = client.get("/api/sales/buyers", headers=sales_farm["headers_a"]).json()
    assert len(buyers) == 1
    assert buyers[0]["order_count"] == 1
    assert buyers[0]["outstanding_balance_lkr"] == 10000.0

    buyer_orders = client.get(
        f"/api/sales/buyers/{buyer_id}/orders", headers=sales_farm["headers_a"]
    ).json()
    assert len(buyer_orders) == 1

    # 4. Settle the remaining 10,000 LKR balance
    pay_res = client.patch(
        f"/api/sales/orders/{sale_data['id']}/payment",
        json={"payment_amount_lkr": 10000.0},
        headers=sales_farm["headers_a"],
    )
    assert pay_res.status_code == 200
    assert pay_res.json()["balance_due_lkr"] == 0.0
    assert pay_res.json()["payment_status"] == "PAID"

    # 5. Check stock summary (100 harvested - 5 spoiled - 40 sold = 55 kg available)
    stock = client.get("/api/sales/stock-summary", headers=sales_farm["headers_a"]).json()
    assert stock["total_harvested_kg"] == 100.0
    assert stock["total_spoiled_kg"] == 5.0
    assert stock["total_sold_kg"] == 40.0
    assert stock["available_for_sale_kg"] == 55.0
    assert stock["outstanding_balance_lkr"] == 0.0


def test_cross_tenant_buyer_and_sale_isolation(client, sales_farm):
    buyer_res = client.post(
        "/api/sales/buyers",
        json={"name": "Hotel Galadari", "buyer_type": "HOTEL"},
        headers=sales_farm["headers_a"],
    )
    buyer_id = buyer_res.json()["id"]

    # Org B cannot view Org A's buyers or record sales against Org A's buyer
    org_b_buyers = client.get("/api/sales/buyers", headers=sales_farm["headers_b"]).json()
    assert org_b_buyers == []

    forbid_sale = client.post(
        "/api/sales/orders",
        json={"buyer_id": buyer_id, "quantity_kg": 10.0, "price_per_kg_lkr": 600.0},
        headers=sales_farm["headers_b"],
    )
    assert forbid_sale.status_code == 404
