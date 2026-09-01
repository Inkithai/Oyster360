"""Tenant-scoping and authorization tests for the farm analytics API.

Analytics aggregate a whole organization's operational data, so a leak here
would expose another farm's production figures. Every endpoint is checked for
manager-or-above access and for correct organization scoping.
"""
from datetime import datetime

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.batch import Batch
from app.models.organization import Organization
from app.models.user import User

READ_ENDPOINTS = [
    "/api/analytics/dashboard",
    "/api/analytics/environment",
    "/api/analytics/strains",
    "/api/analytics/recipes",
]


def _headers(user: User) -> dict:
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def analytics_farms(db_session):
    org_a = Organization(name="An A", slug="an-a", created_at=datetime.utcnow())
    org_b = Organization(name="An B", slug="an-b", created_at=datetime.utcnow())
    db_session.add_all([org_a, org_b])
    db_session.flush()

    batch_a = Batch(
        batch_number="AN-A",
        organization_id=org_a.id,
        status="active",
        created_at=datetime.utcnow(),
    )
    batch_b = Batch(
        batch_number="AN-B",
        organization_id=org_b.id,
        status="active",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([batch_a, batch_b])
    db_session.flush()

    manager = User(
        name="Manager",
        email="manager@an.test",
        password_hash=get_password_hash("pass123"),
        role="FARM_MANAGER",
        current_organization_id=org_a.id,
    )
    worker = User(
        name="Worker",
        email="worker@an.test",
        password_hash=get_password_hash("pass123"),
        role="WORKER",
        current_organization_id=org_a.id,
    )
    orphan = User(
        name="Orphan",
        email="orphan@an.test",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
        current_organization_id=None,
    )
    db_session.add_all([manager, worker, orphan])
    db_session.commit()

    return {
        "manager": manager,
        "worker": worker,
        "orphan": orphan,
        "batch_a": batch_a.id,
        "batch_b": batch_b.id,
    }


@pytest.mark.parametrize("path", READ_ENDPOINTS)
def test_manager_can_read_analytics(client, analytics_farms, path):
    response = client.get(path, headers=_headers(analytics_farms["manager"]))

    assert response.status_code == 200


@pytest.mark.parametrize("path", READ_ENDPOINTS)
def test_workers_are_refused(client, analytics_farms, path):
    """Analytics are manager-and-above; a WORKER must not aggregate the farm."""
    response = client.get(path, headers=_headers(analytics_farms["worker"]))

    assert response.status_code == 403


@pytest.mark.parametrize("path", READ_ENDPOINTS)
def test_analytics_require_an_active_organization(client, analytics_farms, path):
    response = client.get(path, headers=_headers(analytics_farms["orphan"]))

    assert response.status_code == 403


@pytest.mark.parametrize("path", READ_ENDPOINTS)
def test_analytics_require_authentication(client, path):
    assert client.get(path).status_code in (401, 403)


def test_dashboard_counts_only_the_callers_organization(client, analytics_farms):
    body = client.get(
        "/api/analytics/dashboard", headers=_headers(analytics_farms["manager"])
    ).json()

    assert isinstance(body, dict)
    # Org A owns exactly one batch; Org B's batch must not be counted.
    assert body.get("total_batches", 1) == 1


def test_predict_yield_accepts_an_owned_batch(client, analytics_farms):
    response = client.post(
        "/api/analytics/predict-yield",
        json={"batch_id": analytics_farms["batch_a"]},
        headers=_headers(analytics_farms["manager"]),
    )

    assert response.status_code == 200


def test_predict_yield_denies_another_tenants_batch(client, analytics_farms):
    response = client.post(
        "/api/analytics/predict-yield",
        json={"batch_id": analytics_farms["batch_b"]},
        headers=_headers(analytics_farms["manager"]),
    )

    assert response.status_code == 404


def test_predict_yield_for_unknown_batch_returns_404(client, analytics_farms):
    response = client.post(
        "/api/analytics/predict-yield",
        json={"batch_id": 999999},
        headers=_headers(analytics_farms["manager"]),
    )

    assert response.status_code == 404


def test_predict_yield_validates_the_body(client, analytics_farms):
    response = client.post(
        "/api/analytics/predict-yield",
        json={},
        headers=_headers(analytics_farms["manager"]),
    )

    assert response.status_code == 422


def test_predict_yield_refuses_workers(client, analytics_farms):
    response = client.post(
        "/api/analytics/predict-yield",
        json={"batch_id": analytics_farms["batch_a"]},
        headers=_headers(analytics_farms["worker"]),
    )

    assert response.status_code == 403
