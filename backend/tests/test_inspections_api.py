"""Tests for the image-inspection endpoints.

Inspections hang off a batch, so every route must enforce the tenant boundary
via the batch's organization. Vision analysis is the simulated in-process
provider, so no AI vendor is contacted.
"""
from datetime import datetime

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.batch import Batch
from app.models.image_inspection import ImageInspection
from app.models.organization import Organization
from app.models.room import Room
from app.models.user import User


def _headers(user: User) -> dict:
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def farms(db_session):
    org_a = Organization(name="Insp A", slug="insp-a", created_at=datetime.utcnow())
    org_b = Organization(name="Insp B", slug="insp-b", created_at=datetime.utcnow())
    db_session.add_all([org_a, org_b])
    db_session.flush()

    room_a = Room(name="Room A", organization_id=org_a.id, capacity=50)
    room_b = Room(name="Room B", organization_id=org_b.id, capacity=50)
    other_room_a = Room(name="Room A2", organization_id=org_a.id, capacity=50)
    db_session.add_all([room_a, room_b, other_room_a])
    db_session.flush()

    batch_a = Batch(
        batch_number="INSP-A",
        organization_id=org_a.id,
        room_id=room_a.id,
        status="active",
        created_at=datetime.utcnow(),
    )
    batch_b = Batch(
        batch_number="INSP-B",
        organization_id=org_b.id,
        room_id=room_b.id,
        status="active",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([batch_a, batch_b])
    db_session.flush()

    user_a = User(
        name="Worker A",
        email="worker_a@insp.test",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
        current_organization_id=org_a.id,
    )
    user_b = User(
        name="Worker B",
        email="worker_b@insp.test",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
        current_organization_id=org_b.id,
    )
    orphan = User(
        name="No Org",
        email="noorg@insp.test",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
        current_organization_id=None,
    )
    db_session.add_all([user_a, user_b, orphan])
    db_session.commit()

    return {
        "user_a": user_a,
        "user_b": user_b,
        "orphan": orphan,
        "batch_a": batch_a.id,
        "batch_b": batch_b.id,
        "room_a": room_a.id,
        "room_b": room_b.id,
        "other_room_a": other_room_a.id,
    }


def test_upload_creates_a_pending_inspection(client, db_session, farms):
    response = client.post(
        "/api/inspections/upload",
        json={
            "batch_id": farms["batch_a"],
            "room_id": farms["room_a"],
            "image_url": "https://cdn.test/a.jpg",
        },
        headers=_headers(farms["user_a"]),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending"
    stored = db_session.query(ImageInspection).filter_by(id=body["inspection_id"]).one()
    assert stored.image_url == "https://cdn.test/a.jpg"
    assert stored.uploaded_by == farms["user_a"].id


def test_upload_rejects_a_room_that_does_not_belong_to_the_batch(client, farms):
    response = client.post(
        "/api/inspections/upload",
        json={
            "batch_id": farms["batch_a"],
            "room_id": farms["other_room_a"],
            "image_url": "https://cdn.test/a.jpg",
        },
        headers=_headers(farms["user_a"]),
    )

    assert response.status_code == 400
    assert "Room does not match" in response.json()["detail"]


def test_upload_denies_a_batch_from_another_tenant(client, db_session, farms):
    response = client.post(
        "/api/inspections/upload",
        json={
            "batch_id": farms["batch_b"],
            "room_id": farms["room_b"],
            "image_url": "https://cdn.test/leak.jpg",
        },
        headers=_headers(farms["user_a"]),
    )

    assert response.status_code in (403, 404)
    assert db_session.query(ImageInspection).count() == 0


def test_upload_requires_an_active_organization(client, farms):
    response = client.post(
        "/api/inspections/upload",
        json={
            "batch_id": farms["batch_a"],
            "room_id": farms["room_a"],
            "image_url": "https://cdn.test/a.jpg",
        },
        headers=_headers(farms["orphan"]),
    )

    assert response.status_code == 403
    assert "active organization" in response.json()["detail"].lower()


def test_upload_requires_authentication(client, farms):
    response = client.post(
        "/api/inspections/upload",
        json={"batch_id": farms["batch_a"], "room_id": farms["room_a"], "image_url": "x"},
    )

    assert response.status_code in (401, 403)


def _create_inspection(client, farms) -> int:
    return client.post(
        "/api/inspections/upload",
        json={
            "batch_id": farms["batch_a"],
            "room_id": farms["room_a"],
            "image_url": "https://cdn.test/a.jpg",
        },
        headers=_headers(farms["user_a"]),
    ).json()["inspection_id"]


def test_analyze_returns_vision_findings(client, farms):
    inspection_id = _create_inspection(client, farms)

    response = client.post(
        f"/api/inspections/{inspection_id}/analyze", headers=_headers(farms["user_a"])
    )

    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["health_score"] <= 100
    assert body["detected_stage"]
    assert isinstance(body["findings"], list)


def test_analyze_marks_the_inspection_completed(client, db_session, farms):
    inspection_id = _create_inspection(client, farms)

    client.post(f"/api/inspections/{inspection_id}/analyze", headers=_headers(farms["user_a"]))

    stored = db_session.query(ImageInspection).filter_by(id=inspection_id).one()
    assert stored.ai_status == "completed"


def test_analyze_denies_another_tenants_inspection(client, farms):
    inspection_id = _create_inspection(client, farms)

    response = client.post(
        f"/api/inspections/{inspection_id}/analyze", headers=_headers(farms["user_b"])
    )

    assert response.status_code == 404


def test_analyze_unknown_inspection_returns_404(client, farms):
    response = client.post("/api/inspections/999999/analyze", headers=_headers(farms["user_a"]))

    assert response.status_code == 404


def test_history_lists_inspections_for_the_batch(client, farms):
    first = _create_inspection(client, farms)
    second = _create_inspection(client, farms)

    response = client.get(
        f"/api/inspections/batches/{farms['batch_a']}/history",
        headers=_headers(farms["user_a"]),
    )

    assert response.status_code == 200
    returned = {item["id"] for item in response.json()}
    assert {first, second} <= returned


def test_history_denies_a_batch_from_another_tenant(client, farms):
    response = client.get(
        f"/api/inspections/batches/{farms['batch_b']}/history",
        headers=_headers(farms["user_a"]),
    )

    assert response.status_code in (403, 404)


def test_history_for_a_batch_without_inspections_is_empty(client, farms):
    response = client.get(
        f"/api/inspections/batches/{farms['batch_a']}/history",
        headers=_headers(farms["user_a"]),
    )

    assert response.status_code == 200
    assert response.json() == []
