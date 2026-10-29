"""Tests for harvests API endpoints including flush tracking and spoiled/unsold stock."""
from datetime import datetime
import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.batch import Batch, BatchStage
from app.models.organization import Organization, OrganizationMember
from app.models.user import User


@pytest.fixture
def harvest_fixtures(db_session):
    org = Organization(name="Harvest Farm", slug="harvest-farm", is_active=True, created_at=datetime.utcnow())
    other_org = Organization(name="Other Farm", slug="other-farm", is_active=True, created_at=datetime.utcnow())
    db_session.add_all([org, other_org])
    db_session.flush()

    worker = User(
        name="Harvest Worker",
        email="worker@harvest.com",
        password_hash=get_password_hash("password123"),
        role="WORKER",
        current_organization_id=org.id,
    )
    db_session.add(worker)
    db_session.flush()
    db_session.add(OrganizationMember(organization_id=org.id, user_id=worker.id, role="MEMBER", joined_at=datetime.utcnow()))

    batch = Batch(batch_number="BATCH-H-1", status="active", current_stage=BatchStage.FRUITING, organization_id=org.id, created_at=datetime.utcnow())
    other_batch = Batch(batch_number="BATCH-H-2", status="active", current_stage=BatchStage.FRUITING, organization_id=other_org.id, created_at=datetime.utcnow())
    db_session.add_all([batch, other_batch])
    db_session.commit()

    token = create_access_token({"sub": str(worker.id), "role": worker.role})
    return {
        "org_id": org.id,
        "batch_id": batch.id,
        "other_batch_id": other_batch.id,
        "token": token,
    }


def test_harvest_requires_auth(client):
    response = client.post("/api/batches/1/harvest", json={"quantity_kg": 25.0, "quality_score": 92.0, "selling_price": 12.50})
    assert response.status_code == 401


def test_record_harvest_success(client, harvest_fixtures, db_session):
    headers = {"Authorization": f"Bearer {harvest_fixtures['token']}"}
    response = client.post(
        f"/api/batches/{harvest_fixtures['batch_id']}/harvest",
        json={"quantity_kg": 20.0, "quality_score": 90.0, "selling_price": 15.0},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Harvest recorded"
    assert data["total_yield_kg"] == 20.0
    assert data["revenue"] == 300.0

    batch = db_session.get(Batch, harvest_fixtures["batch_id"])
    assert batch.current_stage == BatchStage.COMPLETED


def test_record_multiple_flushes_and_list_harvests(client, harvest_fixtures, db_session):
    headers = {"Authorization": f"Bearer {harvest_fixtures['token']}"}
    res_f1 = client.post(
        f"/api/batches/{harvest_fixtures['batch_id']}/harvest",
        json={
            "quantity_kg": 30.0,
            "spoiled_kg": 2.0,
            "unsold_kg": 3.0,
            "flush_number": 1,
            "quality_score": 94.0,
            "selling_price": 600.0,
            "complete_batch": False,
        },
        headers=headers,
    )
    assert res_f1.status_code == 200
    assert res_f1.json()["flush_number"] == 1
    assert res_f1.json()["sellable_kg"] == 28.0
    assert res_f1.json()["revenue"] == 16800.0

    batch = db_session.get(Batch, harvest_fixtures["batch_id"])
    assert batch.current_stage == BatchStage.HARVEST

    all_harvests = client.get("/api/harvests", headers=headers)
    assert all_harvests.status_code == 200
    assert len(all_harvests.json()) == 1

    batch_harvests = client.get(
        f"/api/batches/{harvest_fixtures['batch_id']}/harvests", headers=headers
    )
    assert batch_harvests.status_code == 200
    assert batch_harvests.json()[0]["flush_number"] == 1


def test_record_harvest_cross_tenant_denied(client, harvest_fixtures):
    headers = {"Authorization": f"Bearer {harvest_fixtures['token']}"}
    response = client.post(
        f"/api/batches/{harvest_fixtures['other_batch_id']}/harvest",
        json={"quantity_kg": 10.0, "quality_score": 85.0, "selling_price": 10.0},
        headers=headers,
    )
    assert response.status_code == 404


def test_record_harvest_validation(client, harvest_fixtures):
    headers = {"Authorization": f"Bearer {harvest_fixtures['token']}"}
    res1 = client.post(
        f"/api/batches/{harvest_fixtures['batch_id']}/harvest",
        json={"quantity_kg": 0.0, "quality_score": 90.0, "selling_price": 15.0},
        headers=headers,
    )
    assert res1.status_code == 422

    # Spoiled + unsold exceeding total quantity
    res2 = client.post(
        f"/api/batches/{harvest_fixtures['batch_id']}/harvest",
        json={"quantity_kg": 10.0, "spoiled_kg": 8.0, "unsold_kg": 5.0, "selling_price": 500.0},
        headers=headers,
    )
    assert res2.status_code == 400
