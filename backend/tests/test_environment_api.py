"""Tests for environment logging API endpoints."""
import pytest
from app.models.room import Room
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.core.security import get_password_hash, create_access_token
from datetime import datetime


@pytest.fixture
def env_fixtures(db_session):
    org = Organization(name="Env Farm", slug="env-farm", is_active=True, created_at=datetime.utcnow())
    other_org = Organization(name="Other Farm", slug="other-farm", is_active=True, created_at=datetime.utcnow())
    db_session.add_all([org, other_org])
    db_session.flush()

    worker = User(
        name="Env Worker",
        email="worker@env.com",
        password_hash=get_password_hash("password123"),
        role="WORKER",
        current_organization_id=org.id,
    )
    db_session.add(worker)
    db_session.flush()
    db_session.add(OrganizationMember(organization_id=org.id, user_id=worker.id, role="MEMBER", joined_at=datetime.utcnow()))

    room = Room(name="Fruiting Room 1", capacity=500, organization_id=org.id)
    other_room = Room(name="Other Room", capacity=200, organization_id=other_org.id)
    db_session.add_all([room, other_room])
    db_session.commit()

    token = create_access_token({"sub": str(worker.id), "role": worker.role})
    return {
        "org_id": org.id,
        "other_org_id": other_org.id,
        "room_id": room.id,
        "other_room_id": other_room.id,
        "token": token,
    }


def test_environment_endpoints_require_auth(client):
    res1 = client.post("/api/rooms/1/environment", json={"temperature": 22.5, "humidity": 85.0, "co2": 800.0})
    assert res1.status_code == 401

    res2 = client.get("/api/rooms/1/environment/history")
    assert res2.status_code == 401


def test_record_environment_success(client, env_fixtures):
    headers = {"Authorization": f"Bearer {env_fixtures['token']}"}
    response = client.post(
        f"/api/rooms/{env_fixtures['room_id']}/environment",
        json={"temperature": 23.5, "humidity": 88.0, "co2": 750.0},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Environment recorded"


def test_record_environment_denies_other_org_room(client, env_fixtures):
    headers = {"Authorization": f"Bearer {env_fixtures['token']}"}
    response = client.post(
        f"/api/rooms/{env_fixtures['other_room_id']}/environment",
        json={"temperature": 23.5, "humidity": 88.0, "co2": 750.0},
        headers=headers,
    )
    assert response.status_code == 404


def test_record_environment_validation(client, env_fixtures):
    headers = {"Authorization": f"Bearer {env_fixtures['token']}"}
    # Humidity > 100
    response = client.post(
        f"/api/rooms/{env_fixtures['room_id']}/environment",
        json={"temperature": 23.5, "humidity": 150.0, "co2": 750.0},
        headers=headers,
    )
    assert response.status_code == 422


def test_get_environment_history(client, env_fixtures):
    headers = {"Authorization": f"Bearer {env_fixtures['token']}"}
    # Record 2 entries
    client.post(
        f"/api/rooms/{env_fixtures['room_id']}/environment",
        json={"temperature": 21.0, "humidity": 80.0, "co2": 600.0},
        headers=headers,
    )
    client.post(
        f"/api/rooms/{env_fixtures['room_id']}/environment",
        json={"temperature": 22.0, "humidity": 85.0, "co2": 700.0},
        headers=headers,
    )

    response = client.get(
        f"/api/rooms/{env_fixtures['room_id']}/environment/history",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert "temperature" in data[0]
    assert "humidity" in data[0]
    assert "co2" in data[0]
