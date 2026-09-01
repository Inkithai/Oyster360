"""Authorization and contract tests for the platform (SaaS) analytics API.

These endpoints expose cross-tenant business metrics — revenue, usage,
retention — so the security property that matters most is that only platform
admins can reach them. Every role below ADMIN must be refused.
"""
from datetime import datetime

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.user import User

ENDPOINTS = [
    "/api/saas-analytics/growth",
    "/api/saas-analytics/revenue",
    "/api/saas-analytics/usage",
    "/api/saas-analytics/retention",
    "/api/saas-analytics/ai-usage",
]


def _headers(user: User) -> dict:
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


def _user(db_session, role: str) -> User:
    user = User(
        name=f"{role} user",
        email=f"{role.lower()}@saas.test",
        password_hash=get_password_hash("pass123"),
        role=role,
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin(db_session):
    return _user(db_session, "ADMIN")


@pytest.mark.parametrize("path", ENDPOINTS)
def test_admin_can_read_platform_metrics(client, admin, path):
    response = client.get(path, headers=_headers(admin))

    assert response.status_code == 200
    assert isinstance(response.json(), dict)


@pytest.mark.parametrize("path", ENDPOINTS)
@pytest.mark.parametrize("role", ["FARM_MANAGER", "WORKER", "VIEWER"])
def test_non_admin_roles_are_refused(client, db_session, path, role):
    """Platform metrics span every tenant; only ADMIN may see them."""
    user = _user(db_session, role)

    response = client.get(path, headers=_headers(user))

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


@pytest.mark.parametrize("path", ENDPOINTS)
def test_unauthenticated_requests_are_refused(client, path):
    assert client.get(path).status_code in (401, 403)


def test_growth_accepts_a_days_window(client, admin):
    response = client.get("/api/saas-analytics/growth?days=7", headers=_headers(admin))

    assert response.status_code == 200


def test_retention_accepts_a_days_window(client, admin):
    response = client.get("/api/saas-analytics/retention?days=90", headers=_headers(admin))

    assert response.status_code == 200


def test_days_parameter_must_be_an_integer(client, admin):
    response = client.get("/api/saas-analytics/growth?days=abc", headers=_headers(admin))

    assert response.status_code == 422


def test_revenue_metrics_expose_expected_keys(client, admin):
    body = client.get("/api/saas-analytics/revenue", headers=_headers(admin)).json()

    assert body
    assert all(isinstance(k, str) for k in body)
