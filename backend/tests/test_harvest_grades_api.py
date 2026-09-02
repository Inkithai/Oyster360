"""Tests for harvest grading API endpoints."""
import pytest
from app.models.batch import Batch
from app.models.harvest import Harvest
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.core.security import get_password_hash, create_access_token
from datetime import datetime


@pytest.fixture
def grading_fixtures(db_session):
    org = Organization(name="Grade Farm", slug="grade-farm", is_active=True, created_at=datetime.utcnow())
    other_org = Organization(name="Other Grade Farm", slug="other-grade-farm", is_active=True, created_at=datetime.utcnow())
    db_session.add_all([org, other_org])
    db_session.flush()

    manager = User(
        name="Grade Manager",
        email="manager@grade.com",
        password_hash=get_password_hash("password123"),
        role="FARM_MANAGER",
        current_organization_id=org.id,
    )
    worker = User(
        name="Grade Worker",
        email="worker@grade.com",
        password_hash=get_password_hash("password123"),
        role="WORKER",
        current_organization_id=org.id,
    )
    db_session.add_all([manager, worker])
    db_session.flush()

    db_session.add(OrganizationMember(organization_id=org.id, user_id=manager.id, role="OWNER", joined_at=datetime.utcnow()))
    db_session.add(OrganizationMember(organization_id=org.id, user_id=worker.id, role="MEMBER", joined_at=datetime.utcnow()))

    batch = Batch(batch_number="BATCH-G-1", status="active", organization_id=org.id, created_at=datetime.utcnow())
    other_batch = Batch(batch_number="BATCH-G-2", status="active", organization_id=other_org.id, created_at=datetime.utcnow())
    db_session.add_all([batch, other_batch])
    db_session.flush()

    harvest = Harvest(batch_id=batch.id, organization_id=org.id, quantity_kg=50.0, quality_score=95.0, harvest_date=datetime.utcnow(), selling_price=10.0)
    other_harvest = Harvest(batch_id=other_batch.id, organization_id=other_org.id, quantity_kg=30.0, quality_score=85.0, harvest_date=datetime.utcnow(), selling_price=10.0)
    db_session.add_all([harvest, other_harvest])
    db_session.commit()

    manager_token = create_access_token({"sub": str(manager.id), "role": manager.role})
    worker_token = create_access_token({"sub": str(worker.id), "role": worker.role})

    return {
        "org_id": org.id,
        "batch_id": batch.id,
        "harvest_id": harvest.id,
        "other_batch_id": other_batch.id,
        "other_harvest_id": other_harvest.id,
        "manager_token": manager_token,
        "worker_token": worker_token,
    }


def test_harvest_grade_auth(client):
    res1 = client.post("/api/harvest-grades/", json={"harvest_id": 1, "batch_id": 1, "grade": "A", "quantity_kg": 10.0, "price_per_kg": 15.0})
    assert res1.status_code == 401

    res2 = client.get("/api/harvest-grades/batches/1")
    assert res2.status_code == 401


def test_record_harvest_grade_success(client, grading_fixtures):
    headers = {"Authorization": f"Bearer {grading_fixtures['manager_token']}"}
    response = client.post(
        "/api/harvest-grades/",
        json={
            "harvest_id": grading_fixtures["harvest_id"],
            "batch_id": grading_fixtures["batch_id"],
            "grade": "A",
            "quantity_kg": 25.0,
            "price_per_kg": 18.0,
            "notes": "Premium quality caps",
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["grade"] == "A"
    assert data["quantity_kg"] == 25.0


def test_record_harvest_grade_mismatch_batch(client, grading_fixtures):
    headers = {"Authorization": f"Bearer {grading_fixtures['manager_token']}"}
    # Pass harvest of batch 1 with batch_id of another batch from same org
    response = client.post(
        "/api/harvest-grades/",
        json={
            "harvest_id": grading_fixtures["harvest_id"],
            "batch_id": grading_fixtures["other_batch_id"],
            "grade": "B",
            "quantity_kg": 10.0,
            "price_per_kg": 12.0,
        },
        headers=headers,
    )
    assert response.status_code == 404


def test_get_grades_by_batch(client, grading_fixtures):
    manager_headers = {"Authorization": f"Bearer {grading_fixtures['manager_token']}"}
    client.post(
        "/api/harvest-grades/",
        json={
            "harvest_id": grading_fixtures["harvest_id"],
            "batch_id": grading_fixtures["batch_id"],
            "grade": "A",
            "quantity_kg": 30.0,
            "price_per_kg": 20.0,
        },
        headers=manager_headers,
    )

    worker_headers = {"Authorization": f"Bearer {grading_fixtures['worker_token']}"}
    response = client.get(
        f"/api/harvest-grades/batches/{grading_fixtures['batch_id']}",
        headers=worker_headers,
    )
    assert response.status_code == 200
    grades = response.json()
    assert len(grades) >= 1
    assert grades[0]["grade"] == "A"
