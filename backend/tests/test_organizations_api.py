"""Tenancy tests for the organization membership API.

These cover the boundary that matters most in a multi-tenant SaaS: a user may
only see and switch into organizations they are an active member of.
"""
from datetime import datetime

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.organization import Organization, OrganizationMember
from app.models.user import User


@pytest.fixture
def members(db_session):
    alice = User(
        name="Alice",
        email="alice@orgs.test",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
    )
    bob = User(
        name="Bob",
        email="bob@orgs.test",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
    )
    db_session.add_all([alice, bob])
    db_session.flush()

    org_a = Organization(
        name="Alice Farm", slug="alice-farm", owner_id=alice.id, created_at=datetime.utcnow()
    )
    org_b = Organization(
        name="Bob Farm", slug="bob-farm", owner_id=bob.id, created_at=datetime.utcnow()
    )
    db_session.add_all([org_a, org_b])
    db_session.flush()

    db_session.add_all(
        [
            OrganizationMember(
                organization_id=org_a.id,
                user_id=alice.id,
                role="OWNER",
                joined_at=datetime.utcnow(),
            ),
            OrganizationMember(
                organization_id=org_b.id,
                user_id=bob.id,
                role="OWNER",
                joined_at=datetime.utcnow(),
            ),
        ]
    )
    alice.current_organization_id = org_a.id
    bob.current_organization_id = org_b.id
    db_session.commit()

    return {
        "alice": alice,
        "bob": bob,
        "org_a": org_a.id,
        "org_b": org_b.id,
        "alice_headers": {
            "Authorization": f"Bearer {create_access_token({'sub': str(alice.id), 'role': alice.role})}"
        },
        "bob_headers": {
            "Authorization": f"Bearer {create_access_token({'sub': str(bob.id), 'role': bob.role})}"
        },
    }


def test_create_organization_makes_caller_the_owner(client, db_session, members):
    response = client.post(
        "/api/organizations/",
        json={"name": "New Farm", "slug": "new-farm"},
        headers=members["alice_headers"],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "new-farm"

    membership = (
        db_session.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == body["id"],
            OrganizationMember.user_id == members["alice"].id,
        )
        .one()
    )
    assert membership.role == "OWNER"


def test_create_organization_switches_current_organization(client, db_session, members):
    response = client.post(
        "/api/organizations/",
        json={"name": "Second Farm", "slug": "second-farm"},
        headers=members["alice_headers"],
    )

    db_session.refresh(members["alice"])
    assert members["alice"].current_organization_id == response.json()["id"]


def test_create_organization_rejects_duplicate_slug(client, members):
    response = client.post(
        "/api/organizations/",
        json={"name": "Copycat", "slug": "bob-farm"},
        headers=members["alice_headers"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Organization slug already taken"


def test_create_organization_requires_authentication(client):
    response = client.post("/api/organizations/", json={"name": "X", "slug": "x"})

    assert response.status_code in (401, 403)


def test_my_organizations_lists_only_own_memberships(client, members):
    response = client.get("/api/organizations/my-organizations", headers=members["alice_headers"])

    assert response.status_code == 200
    slugs = {org["slug"] for org in response.json()}
    assert slugs == {"alice-farm"}
    assert response.json()[0]["is_current"] is True
    assert response.json()[0]["role"] == "OWNER"


def test_my_organizations_requires_authentication(client):
    assert client.get("/api/organizations/my-organizations").status_code in (401, 403)


def test_switch_organization_succeeds_for_a_member(client, db_session, members):
    new_org = Organization(
        name="Shared Farm", slug="shared-farm", created_at=datetime.utcnow()
    )
    db_session.add(new_org)
    db_session.flush()
    db_session.add(
        OrganizationMember(
            organization_id=new_org.id,
            user_id=members["alice"].id,
            role="MANAGER",
            joined_at=datetime.utcnow(),
        )
    )
    db_session.commit()

    response = client.post(
        f"/api/organizations/switch/{new_org.id}", headers=members["alice_headers"]
    )

    assert response.status_code == 200
    db_session.refresh(members["alice"])
    assert members["alice"].current_organization_id == new_org.id


def test_switch_organization_denies_non_members(client, db_session, members):
    response = client.post(
        f"/api/organizations/switch/{members['org_b']}", headers=members["alice_headers"]
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not a member of this organization"
    db_session.refresh(members["alice"])
    assert members["alice"].current_organization_id == members["org_a"]


def test_switch_organization_denies_unknown_organization(client, members):
    response = client.post("/api/organizations/switch/999999", headers=members["alice_headers"])

    assert response.status_code == 403


def test_switch_organization_denies_deactivated_membership(client, db_session, members):
    membership = OrganizationMember(
        organization_id=members["org_b"],
        user_id=members["alice"].id,
        role="VIEWER",
        joined_at=datetime.utcnow(),
        is_active=False,
    )
    db_session.add(membership)
    db_session.commit()

    response = client.post(
        f"/api/organizations/switch/{members['org_b']}", headers=members["alice_headers"]
    )

    assert response.status_code == 403
    assert (
        members["org_b"]
        not in {
            org["id"]
            for org in client.get(
                "/api/organizations/my-organizations", headers=members["alice_headers"]
            ).json()
        }
    )


def test_switch_organization_requires_authentication(client, members):
    assert client.post(f"/api/organizations/switch/{members['org_a']}").status_code in (401, 403)
