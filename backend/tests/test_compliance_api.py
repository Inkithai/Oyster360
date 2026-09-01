"""Tests for the GDPR compliance endpoints.

These cover Article 15 (right to access) and Article 17 (right to be
forgotten). Both are legally significant and previously had no coverage, so
the assertions below pin the exact data-scoping and anonymisation contract.
"""
from datetime import datetime

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.batch import Batch
from app.models.harvest import Harvest
from app.models.organization import Organization, OrganizationMember
from app.models.user import User


def _headers(user: User) -> dict:
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def gdpr_data(db_session):
    """Two users in separate organizations, each with a batch and a harvest."""
    subject = User(
        name="Data Subject",
        email="subject@gdpr.test",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
        created_at=datetime.utcnow(),
    )
    stranger = User(
        name="Stranger",
        email="stranger@gdpr.test",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([subject, stranger])
    db_session.flush()

    org_a = Organization(name="Subject Farm", slug="subject-farm", created_at=datetime.utcnow())
    org_b = Organization(name="Other Farm", slug="other-farm", created_at=datetime.utcnow())
    db_session.add_all([org_a, org_b])
    db_session.flush()

    db_session.add_all(
        [
            OrganizationMember(
                organization_id=org_a.id,
                user_id=subject.id,
                role="OWNER",
                joined_at=datetime.utcnow(),
            ),
            OrganizationMember(
                organization_id=org_b.id,
                user_id=stranger.id,
                role="OWNER",
                joined_at=datetime.utcnow(),
            ),
        ]
    )

    batch_a = Batch(
        batch_number="GDPR-A",
        organization_id=org_a.id,
        status="active",
        created_at=datetime.utcnow(),
    )
    batch_b = Batch(
        batch_number="GDPR-B",
        organization_id=org_b.id,
        status="active",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([batch_a, batch_b])
    db_session.flush()

    db_session.add_all(
        [
            Harvest(
                batch_id=batch_a.id,
                organization_id=org_a.id,
                quantity_kg=12.5,
                quality_score=91.0,
                harvest_date=datetime.utcnow(),
            ),
            Harvest(
                batch_id=batch_b.id,
                organization_id=org_b.id,
                quantity_kg=99.9,
                quality_score=50.0,
                harvest_date=datetime.utcnow(),
            ),
        ]
    )
    db_session.commit()

    return {"subject": subject, "stranger": stranger, "org_a": org_a.id, "org_b": org_b.id}


# ---------------------------------------------------------------------------
# Article 15 — right to access
# ---------------------------------------------------------------------------


def test_export_returns_the_callers_own_profile(client, gdpr_data):
    response = client.get("/api/compliance/export-data", headers=_headers(gdpr_data["subject"]))

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["user"]["email"] == "subject@gdpr.test"
    assert body["data"]["user"]["name"] == "Data Subject"
    assert body["export_date"]


def test_export_includes_organization_membership_and_role(client, gdpr_data):
    response = client.get("/api/compliance/export-data", headers=_headers(gdpr_data["subject"]))

    orgs = response.json()["data"]["organizations"]
    assert len(orgs) == 1
    assert orgs[0]["name"] == "Subject Farm"
    assert orgs[0]["role"] == "OWNER"


def test_export_includes_batches_and_harvests(client, gdpr_data):
    body = client.get(
        "/api/compliance/export-data", headers=_headers(gdpr_data["subject"])
    ).json()

    assert [b["batch_number"] for b in body["data"]["batches"]] == ["GDPR-A"]
    assert [h["quantity_kg"] for h in body["data"]["harvests"]] == [12.5]


def test_export_never_leaks_another_tenants_records(client, gdpr_data):
    body = client.get(
        "/api/compliance/export-data", headers=_headers(gdpr_data["subject"])
    ).json()

    serialised = str(body)
    assert "GDPR-B" not in serialised
    assert "Other Farm" not in serialised
    assert 99.9 not in [h["quantity_kg"] for h in body["data"]["harvests"]]


def test_export_never_includes_credentials(client, gdpr_data):
    """A GDPR export must not hand back password hashes or MFA secrets."""
    body = client.get(
        "/api/compliance/export-data", headers=_headers(gdpr_data["subject"])
    ).json()

    assert set(body["data"]["user"]) == {"id", "name", "email", "role", "created_at"}
    assert "password" not in str(body).lower()
    assert "mfa_secret" not in str(body)


def test_export_for_user_without_organizations_is_empty_but_valid(client, db_session):
    loner = User(
        name="Loner",
        email="loner@gdpr.test",
        password_hash=get_password_hash("pass123"),
        role="WORKER",
        created_at=datetime.utcnow(),
    )
    db_session.add(loner)
    db_session.commit()

    body = client.get("/api/compliance/export-data", headers=_headers(loner)).json()

    assert body["data"]["organizations"] == []
    assert body["data"]["batches"] == []
    assert body["data"]["harvests"] == []


def test_export_requires_authentication(client):
    assert client.get("/api/compliance/export-data").status_code in (401, 403)


# ---------------------------------------------------------------------------
# Article 17 — right to be forgotten
# ---------------------------------------------------------------------------


def test_delete_anonymises_the_profile(client, db_session, gdpr_data):
    subject = gdpr_data["subject"]

    response = client.delete("/api/compliance/delete-data", headers=_headers(subject))

    assert response.status_code == 200
    db_session.refresh(subject)
    assert subject.name == "[Deleted User]"
    assert subject.email == f"deleted_{subject.id}@example.com"


def test_delete_clears_credentials_and_mfa(client, db_session, gdpr_data):
    subject = gdpr_data["subject"]
    subject.mfa_secret = "ABCDEF123456"
    subject.avatar_url = "https://cdn.test/avatar.png"
    db_session.commit()

    client.delete("/api/compliance/delete-data", headers=_headers(subject))

    db_session.refresh(subject)
    assert subject.password_hash == ""
    assert subject.mfa_secret is None
    assert subject.avatar_url is None


def test_delete_revokes_all_organization_memberships(client, db_session, gdpr_data):
    subject = gdpr_data["subject"]

    client.delete("/api/compliance/delete-data", headers=_headers(subject))

    remaining = (
        db_session.query(OrganizationMember)
        .filter(OrganizationMember.user_id == subject.id)
        .count()
    )
    assert remaining == 0


def test_delete_does_not_affect_other_users(client, db_session, gdpr_data):
    stranger = gdpr_data["stranger"]

    client.delete("/api/compliance/delete-data", headers=_headers(gdpr_data["subject"]))

    db_session.refresh(stranger)
    assert stranger.name == "Stranger"
    assert stranger.email == "stranger@gdpr.test"
    assert (
        db_session.query(OrganizationMember)
        .filter(OrganizationMember.user_id == stranger.id)
        .count()
        == 1
    )


def test_delete_is_idempotent(client, db_session, gdpr_data):
    subject = gdpr_data["subject"]
    headers = _headers(subject)

    assert client.delete("/api/compliance/delete-data", headers=headers).status_code == 200
    second = client.delete("/api/compliance/delete-data", headers=headers)

    assert second.status_code == 200
    db_session.refresh(subject)
    assert subject.name == "[Deleted User]"


def test_delete_requires_authentication(client):
    assert client.delete("/api/compliance/delete-data").status_code in (401, 403)
