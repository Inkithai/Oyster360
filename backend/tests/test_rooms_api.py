"""Tests for rooms API endpoints."""
import pytest
from app.models.room import Room
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.core.security import get_password_hash, create_access_token
from datetime import datetime


@pytest.fixture
def room_fixtures(db_session):
    org_a = Organization(name="Farm A", slug="farm-a", is_active=True, created_at=datetime.utcnow())
    org_b = Organization(name="Farm B", slug="farm-b", is_active=True, created_at=datetime.utcnow())
    db_session.add_all([org_a, org_b])
    db_session.flush()

    user_a = User(
        name="User A",
        email="user_a@room.com",
        password_hash=get_password_hash("password123"),
        role="WORKER",
        current_organization_id=org_a.id,
    )
    db_session.add(user_a)
    db_session.flush()
    db_session.add(OrganizationMember(organization_id=org_a.id, user_id=user_a.id, role="MEMBER", joined_at=datetime.utcnow()))

    r1 = Room(name="Incubation 1", capacity=100, temperature_target=24.0, humidity_target=70.0, organization_id=org_a.id)
    r2 = Room(name="Fruiting 1", capacity=200, temperature_target=18.0, humidity_target=90.0, organization_id=org_a.id)
    r_b = Room(name="Org B Room", capacity=300, temperature_target=20.0, humidity_target=80.0, organization_id=org_b.id)
    db_session.add_all([r1, r2, r_b])
    db_session.commit()

    token_a = create_access_token({"sub": str(user_a.id), "role": user_a.role})
    return {
        "org_a": org_a.id,
        "token_a": token_a,
    }


def test_rooms_requires_auth(client):
    response = client.get("/api/rooms/")
    assert response.status_code == 401


def test_get_rooms_filtered_by_organization(client, room_fixtures):
    headers = {"Authorization": f"Bearer {room_fixtures['token_a']}"}
    response = client.get("/api/rooms/", headers=headers)
    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) == 2
    names = [r["name"] for r in rooms]
    assert "Incubation 1" in names
    assert "Fruiting 1" in names
    assert "Org B Room" not in names
