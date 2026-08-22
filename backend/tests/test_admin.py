"""
Admin API Tests

Covers the /api/admin router: role enforcement, system statistics, user and
organization listings, audit-log retrieval, and the feature-flag lifecycle.
"""
from datetime import datetime

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.admin import FeatureFlag
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.user import User, UserRole
from app.services.admin_service import AdminService


@pytest.fixture
def admin_user(db_session):
    user = User(
        name="Platform Admin",
        email="admin@oyster360.test",
        password_hash=get_password_hash("adminpass123"),
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def worker_user(db_session):
    user = User(
        name="Farm Worker",
        email="worker@oyster360.test",
        password_hash=get_password_hash("workerpass123"),
        role=UserRole.WORKER,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token({"sub": str(admin_user.id), "role": admin_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def worker_headers(worker_user):
    token = create_access_token({"sub": str(worker_user.id), "role": worker_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def platform_data(db_session):
    """One organization with one active and one canceled subscription."""
    org = Organization(name="Admin Test Org", slug="admin-test-org",
                       created_at=datetime.utcnow())
    db_session.add(org)
    db_session.flush()
    db_session.add_all([
        Subscription(organization_id=org.id, plan="starter", status="active",
                     created_at=datetime.utcnow()),
        Subscription(organization_id=org.id, plan="pro", status="canceled",
                     created_at=datetime.utcnow()),
    ])
    db_session.commit()
    return org


class TestAdminAccessControl:
    def test_endpoints_require_authentication(self, client):
        for endpoint in ("/api/admin/stats", "/api/admin/users",
                         "/api/admin/organizations", "/api/admin/audit-logs",
                         "/api/admin/feature-flags"):
            assert client.get(endpoint).status_code == 401

    def test_non_admin_roles_are_rejected(self, client, worker_headers):
        for endpoint in ("/api/admin/stats", "/api/admin/users",
                         "/api/admin/audit-logs"):
            assert client.get(endpoint, headers=worker_headers).status_code == 403

    def test_invalid_token_is_rejected(self, client):
        response = client.get(
            "/api/admin/stats", headers={"Authorization": "Bearer not-a-jwt"}
        )
        assert response.status_code == 401


class TestSystemStats:
    def test_counts_users_organizations_and_subscriptions(
        self, client, db_session, admin_headers, admin_user, worker_user,
        platform_data
    ):
        response = client.get("/api/admin/stats", headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["total_users"] == 2  # admin + worker
        assert body["total_organizations"] == 1
        assert body["total_subscriptions"] == 2
        assert body["active_subscriptions"] == 1
        assert "timestamp" in body


class TestUserAndOrganizationListings:
    def test_lists_users_with_roles(self, client, admin_headers, worker_user):
        response = client.get("/api/admin/users", headers=admin_headers)

        assert response.status_code == 200
        users = response.json()
        emails = {user["email"] for user in users}
        assert "worker@oyster360.test" in emails
        worker = next(u for u in users if u["email"] == "worker@oyster360.test")
        assert worker["role"] == "WORKER"

    def test_lists_organizations_with_active_flag(
        self, client, admin_headers, platform_data
    ):
        response = client.get("/api/admin/organizations", headers=admin_headers)

        assert response.status_code == 200
        orgs = response.json()
        assert len(orgs) == 1
        assert orgs[0]["slug"] == "admin-test-org"
        assert orgs[0]["is_active"] is True


class TestAuditLogs:
    def test_returns_most_recent_actions_first(
        self, client, db_session, admin_headers, admin_user
    ):
        service = AdminService(db_session)
        service.log_action(admin_user.id, "login", "user",
                           resource_id=admin_user.id)
        service.log_action(admin_user.id, "update", "organization",
                           new_values={"name": "Renamed"})

        response = client.get("/api/admin/audit-logs", headers=admin_headers)

        assert response.status_code == 200
        logs = response.json()
        assert len(logs) == 2
        assert logs[0]["action"] == "update"
        assert logs[0]["resource"] == "organization"
        assert logs[1]["action"] == "login"


class TestFeatureFlags:
    def test_toggle_creates_updates_and_lists_flags(
        self, client, db_session, admin_headers
    ):
        created = client.post(
            "/api/admin/feature-flags/ai-insights?enabled=true",
            headers=admin_headers,
        )
        assert created.status_code == 200
        assert created.json() == {"name": "ai-insights", "enabled": True}

        disabled = client.post(
            "/api/admin/feature-flags/ai-insights?enabled=false",
            headers=admin_headers,
        )
        assert disabled.status_code == 200
        assert disabled.json() == {"name": "ai-insights", "enabled": False}

        listed = client.get("/api/admin/feature-flags", headers=admin_headers)
        assert listed.status_code == 200
        flags = {flag["name"]: flag["enabled"] for flag in listed.json()}
        assert flags["ai-insights"] is False

    def test_flag_state_persists_in_database(
        self, client, db_session, admin_headers
    ):
        client.post("/api/admin/feature-flags/beta-ui?enabled=true",
                    headers=admin_headers)

        flag = db_session.query(FeatureFlag).filter_by(name="beta-ui").first()
        assert flag is not None
        assert flag.enabled is True
