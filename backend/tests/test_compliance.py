"""Tests for the GDPR compliance API (app.api.compliance)."""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.database import get_db
from app.models.batch import Batch
from app.models.harvest import Harvest
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.core.security import get_password_hash, create_access_token


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def gdpr_data(db_session):
    """One user in two organizations, with a batch and a harvest in the first."""
    org = Organization(name="Export Farms", slug="export-farms", created_at=datetime.utcnow())
    other_org = Organization(name="Other Farms", slug="other-farms", created_at=datetime.utcnow())
    db_session.add_all([org, other_org])
    db_session.flush()

    user = User(
        name="Export User",
        email="export@test.com",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
        current_organization_id=org.id,
    )
    db_session.add(user)
    db_session.flush()

    db_session.add_all(
        [
            OrganizationMember(organization_id=org.id, user_id=user.id, role="OWNER", joined_at=datetime.utcnow()),
            OrganizationMember(organization_id=other_org.id, user_id=user.id, role="MEMBER", joined_at=datetime.utcnow()),
        ]
    )

    batch = Batch(
        batch_number="EXP-1",
        organization_id=org.id,
        status="completed",
        created_at=datetime.utcnow(),
    )
    db_session.add(batch)
    db_session.flush()

    harvest = Harvest(
        batch_id=batch.id,
        organization_id=org.id,
        quantity_kg=12.5,
        quality_score=4.5,
        harvest_date=datetime.utcnow(),
    )
    db_session.add(harvest)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"user": user, "org": org, "other_org": other_org, "batch": batch, "token": token}


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestExportData:
    def test_requires_authentication(self, client):
        response = client.get("/api/compliance/export-data")
        assert response.status_code in (401, 403)

    def test_exports_user_profile(self, client, gdpr_data):
        response = client.get("/api/compliance/export-data", headers=_auth(gdpr_data["token"]))
        assert response.status_code == 200

        body = response.json()
        assert body["data"]["user"]["email"] == "export@test.com"
        assert body["data"]["user"]["name"] == "Export User"
        assert body["export_date"]

    def test_export_includes_memberships(self, client, gdpr_data):
        body = client.get("/api/compliance/export-data", headers=_auth(gdpr_data["token"])).json()
        organizations = body["data"]["organizations"]
        assert len(organizations) == 2
        assert {o["name"] for o in organizations} == {"Export Farms", "Other Farms"}

    def test_export_includes_batches_and_harvests(self, client, gdpr_data):
        body = client.get("/api/compliance/export-data", headers=_auth(gdpr_data["token"])).json()
        batches = body["data"]["batches"]
        harvests = body["data"]["harvests"]

        assert [b["batch_number"] for b in batches] == ["EXP-1"]
        assert batches[0]["status"] == "completed"
        assert harvests[0]["quantity_kg"] == 12.5
        assert harvests[0]["quality_score"] == 4.5


class TestDeleteData:
    def test_requires_authentication(self, client):
        response = client.delete("/api/compliance/delete-data")
        assert response.status_code in (401, 403)

    def test_deletion_anonymizes_user(self, db_session, client, gdpr_data):
        user = gdpr_data["user"]
        response = client.delete("/api/compliance/delete-data", headers=_auth(gdpr_data["token"]))

        assert response.status_code == 200
        assert response.json() == {"message": "Data deletion completed"}

        db_session.expire_all()
        deleted = db_session.query(User).filter(User.id == user.id).one()
        assert deleted.name == "[Deleted User]"
        assert deleted.email == f"deleted_{user.id}@example.com"
        assert deleted.password_hash == ""
        assert deleted.mfa_secret is None

    def test_deletion_removes_organization_memberships(self, db_session, client, gdpr_data):
        user = gdpr_data["user"]
        client.delete("/api/compliance/delete-data", headers=_auth(gdpr_data["token"]))

        db_session.expire_all()
        remaining = (
            db_session.query(OrganizationMember)
            .filter(OrganizationMember.user_id == user.id)
            .count()
        )
        assert remaining == 0

    def test_deletion_keeps_other_tenants_intact(self, db_session, client, gdpr_data):
        other_batch = Batch(
            batch_number="KEEP-1",
            organization_id=gdpr_data["other_org"].id,
            status="active",
            created_at=datetime.utcnow(),
        )
        db_session.add(other_batch)
        db_session.commit()

        client.delete("/api/compliance/delete-data", headers=_auth(gdpr_data["token"]))

        assert db_session.query(Batch).filter(Batch.id == other_batch.id).one() is not None
