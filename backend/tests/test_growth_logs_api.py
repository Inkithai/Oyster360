"""Tests for growth logs and timeline API endpoints."""
import pytest
from app.models.batch import Batch
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.core.security import get_password_hash, create_access_token
from datetime import datetime


@pytest.fixture
def growth_fixtures(db_session):
    org = Organization(name="Growth Farm", slug="growth-farm", is_active=True, created_at=datetime.utcnow())
    other_org = Organization(name="Other Farm", slug="other-farm", is_active=True, created_at=datetime.utcnow())
    db_session.add_all([org, other_org])
    db_session.flush()

    worker = User(
        name="Growth Worker",
        email="worker@growth.com",
        password_hash=get_password_hash("password123"),
        role="WORKER",
        current_organization_id=org.id,
    )
    db_session.add(worker)
    db_session.flush()
    db_session.add(OrganizationMember(organization_id=org.id, user_id=worker.id, role="MEMBER", joined_at=datetime.utcnow()))

    batch = Batch(batch_number="BATCH-GROWTH-1", status="active", organization_id=org.id, created_at=datetime.utcnow())
    other_batch = Batch(batch_number="BATCH-OTHER-1", status="active", organization_id=other_org.id, created_at=datetime.utcnow())
    db_session.add_all([batch, other_batch])
    db_session.commit()

    token = create_access_token({"sub": str(worker.id), "role": worker.role})
    return {
        "org_id": org.id,
        "batch_id": batch.id,
        "other_batch_id": other_batch.id,
        "token": token,
    }


def test_growth_logs_require_auth(client):
    res1 = client.post("/api/batches/1/growth-logs", json={"stage": "COLONIZATION", "notes": "Healthy", "health_score": 90.0})
    assert res1.status_code == 401

    res2 = client.get("/api/batches/1/timeline")
    assert res2.status_code == 401


def test_create_growth_log_success(client, growth_fixtures):
    headers = {"Authorization": f"Bearer {growth_fixtures['token']}"}
    response = client.post(
        f"/api/batches/{growth_fixtures['batch_id']}/growth-logs",
        json={"stage": "PINNING", "notes": "Primordia forming nicely", "health_score": 95.0, "image_url": "https://img.test/1.jpg"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Growth log recorded"


def test_create_growth_log_denies_cross_tenant(client, growth_fixtures):
    headers = {"Authorization": f"Bearer {growth_fixtures['token']}"}
    response = client.post(
        f"/api/batches/{growth_fixtures['other_batch_id']}/growth-logs",
        json={"stage": "PINNING", "notes": "Unauthorized", "health_score": 80.0},
        headers=headers,
    )
    assert response.status_code == 404


def test_create_growth_log_validation(client, growth_fixtures):
    headers = {"Authorization": f"Bearer {growth_fixtures['token']}"}
    # Health score > 100
    response = client.post(
        f"/api/batches/{growth_fixtures['batch_id']}/growth-logs",
        json={"stage": "PINNING", "notes": "Invalid score", "health_score": 150.0},
        headers=headers,
    )
    assert response.status_code == 422


def test_get_batch_timeline(client, growth_fixtures):
    headers = {"Authorization": f"Bearer {growth_fixtures['token']}"}
    client.post(
        f"/api/batches/{growth_fixtures['batch_id']}/growth-logs",
        json={"stage": "INOCULATION", "notes": "Inoculated with Pearl Oyster", "health_score": 100.0},
        headers=headers,
    )
    client.post(
        f"/api/batches/{growth_fixtures['batch_id']}/growth-logs",
        json={"stage": "COLONIZATION", "notes": "Mycelium running fast", "health_score": 98.0},
        headers=headers,
    )

    response = client.get(
        f"/api/batches/{growth_fixtures['batch_id']}/timeline",
        headers=headers,
    )
    assert response.status_code == 200
    timeline = response.json()
    assert len(timeline) >= 2
    assert timeline[0]["stage"] == "INOCULATION"
    assert timeline[1]["stage"] == "COLONIZATION"
