"""Tests for the Sri Lankan LKR Cost & Profit Calculator API and service."""
from datetime import datetime

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.batch import Batch, BatchStage
from app.models.harvest import Harvest
from app.models.organization import Organization, OrganizationMember
from app.models.user import User


@pytest.fixture
def finance_farm(db_session):
    org_a = Organization(name="Maharagama Farm", slug="maharagama-farm", created_at=datetime.utcnow())
    org_b = Organization(name="Kandy Farm", slug="kandy-farm", created_at=datetime.utcnow())
    db_session.add_all([org_a, org_b])
    db_session.flush()

    manager_a = User(
        name="Manager A",
        email="mgr_a@farm.lk",
        password_hash=get_password_hash("password123"),
        role="FARM_MANAGER",
        current_organization_id=org_a.id,
    )
    manager_b = User(
        name="Manager B",
        email="mgr_b@farm.lk",
        password_hash=get_password_hash("password123"),
        role="FARM_MANAGER",
        current_organization_id=org_b.id,
    )
    db_session.add_all([manager_a, manager_b])
    db_session.flush()

    db_session.add_all([
        OrganizationMember(organization_id=org_a.id, user_id=manager_a.id, role="OWNER"),
        OrganizationMember(organization_id=org_b.id, user_id=manager_b.id, role="OWNER"),
    ])

    batch_a = Batch(
        batch_number="SL-BATCH-001",
        organization_id=org_a.id,
        current_stage=BatchStage.FRUITING,
        bags_prepared=1000,
        bags_inoculated=1000,
        bags_contaminated=50,
        bags_harvested=950,
        status="active",
        start_date=datetime.utcnow(),
    )
    batch_b = Batch(
        batch_number="SL-BATCH-002",
        organization_id=org_b.id,
        current_stage=BatchStage.COLONIZATION,
        bags_prepared=500,
        status="active",
        start_date=datetime.utcnow(),
    )
    db_session.add_all([batch_a, batch_b])
    db_session.flush()

    db_session.add(
        Harvest(
            batch_id=batch_a.id,
            organization_id=org_a.id,
            flush_number=1,
            quantity_kg=210.0,
            unsold_kg=5.0,
            spoiled_kg=10.0,
            quality_score=92.0,
            selling_price=600.0,
            harvest_date=datetime.utcnow(),
        )
    )
    db_session.commit()

    token_a = create_access_token({"sub": str(manager_a.id), "role": manager_a.role})
    token_b = create_access_token({"sub": str(manager_b.id), "role": manager_b.role})
    return {
        "org_a": org_a.id,
        "org_b": org_b.id,
        "batch_a": batch_a.id,
        "batch_b": batch_b.id,
        "headers_a": {"Authorization": f"Bearer {token_a}"},
        "headers_b": {"Authorization": f"Bearer {token_b}"},
    }


def test_record_and_list_expenses_in_lkr(client, finance_farm):
    res1 = client.post(
        "/api/finance/expenses",
        json={
            "category": "SUBSTRATE",
            "amount_lkr": 18000.0,
            "description": "Sawdust and rice bran",
            "batch_id": finance_farm["batch_a"],
        },
        headers=finance_farm["headers_a"],
    )
    assert res1.status_code == 200
    body = res1.json()
    assert body["category"] == "SUBSTRATE"
    assert body["amount_lkr"] == 18000.0

    res2 = client.post(
        "/api/finance/expenses",
        json={
            "category": "LABOUR",
            "amount_lkr": 12000.0,
            "description": "Steaming and bagging labour",
        },
        headers=finance_farm["headers_a"],
    )
    assert res2.status_code == 200

    list_res = client.get("/api/finance/expenses", headers=finance_farm["headers_a"])
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) == 2

    batch_filtered = client.get(
        f"/api/finance/expenses?batch_id={finance_farm['batch_a']}",
        headers=finance_farm["headers_a"],
    )
    assert len(batch_filtered.json()) == 1


def test_cross_tenant_expense_isolation(client, finance_farm):
    # Org A cannot record expense against Org B's batch
    res = client.post(
        "/api/finance/expenses",
        json={
            "category": "SPAWN",
            "amount_lkr": 5000.0,
            "batch_id": finance_farm["batch_b"],
        },
        headers=finance_farm["headers_a"],
    )
    assert res.status_code == 404


def test_profitability_calculator_computes_cost_per_bag_and_profit(client, finance_farm):
    client.post(
        "/api/finance/expenses",
        json={
            "category": "SUBSTRATE",
            "amount_lkr": 20000.0,
            "batch_id": finance_farm["batch_a"],
        },
        headers=finance_farm["headers_a"],
    )
    client.post(
        "/api/finance/expenses",
        json={
            "category": "ELECTRICITY",
            "amount_lkr": 10000.0,
        },
        headers=finance_farm["headers_a"],
    )

    res = client.get("/api/finance/profitability", headers=finance_farm["headers_a"])
    assert res.status_code == 200
    summary = res.json()

    assert summary["currency"] == "LKR"
    assert summary["total_expenses_lkr"] == 30000.0
    assert summary["total_bags_prepared"] == 1000
    assert summary["cost_per_bag_lkr"] == 30.0  # 30,000 LKR / 1,000 bags
    assert summary["total_harvested_kg"] == 210.0
    assert summary["sellable_harvest_kg"] == 200.0  # 210 - 10 spoiled
    # Harvest revenue: 200 sellable kg * 600 LKR = 120,000 LKR
    assert summary["harvest_revenue_lkr"] == 120000.0
    assert summary["gross_profit_lkr"] == 100000.0  # 120,000 - 20,000 direct substrate
    assert summary["estimated_net_profit_lkr"] == 90000.0  # 120,000 - 30,000 total
    assert len(summary["batch_profitability"]) == 1
    assert summary["batch_profitability"][0]["batch_number"] == "SL-BATCH-001"
    assert summary["batch_profitability"][0]["net_profit_lkr"] == 90000.0
