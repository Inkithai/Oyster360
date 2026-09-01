"""Tests for the AI and assistant HTTP endpoints.

All inference is the in-process rule-based/simulated provider, and the autouse
fixtures in conftest block outbound HTTP, so these run fully offline. The focus
is the tenant boundary and the error contract, which is where the routers add
behaviour beyond the services.
"""
from datetime import datetime

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.batch import Batch
from app.models.document import KnowledgeDocument
from app.models.organization import Organization
from app.models.user import User
from app.models.yield_prediction import YieldPrediction


def _headers(user: User) -> dict:
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def ai_farms(db_session):
    org_a = Organization(name="AI A", slug="ai-api-a", created_at=datetime.utcnow())
    org_b = Organization(name="AI B", slug="ai-api-b", created_at=datetime.utcnow())
    db_session.add_all([org_a, org_b])
    db_session.flush()

    batch_a = Batch(
        batch_number="AIAPI-A",
        organization_id=org_a.id,
        status="active",
        created_at=datetime.utcnow(),
    )
    batch_b = Batch(
        batch_number="AIAPI-B",
        organization_id=org_b.id,
        status="active",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([batch_a, batch_b])
    db_session.flush()

    user_a = User(
        name="A",
        email="a@aiapi.test",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
        current_organization_id=org_a.id,
    )
    orphan = User(
        name="Orphan",
        email="orphan@aiapi.test",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
        current_organization_id=None,
    )
    db_session.add_all([user_a, orphan])
    db_session.commit()

    return {
        "user_a": user_a,
        "orphan": orphan,
        "batch_a": batch_a.id,
        "batch_b": batch_b.id,
    }


# ---------------------------------------------------------------------------
# /api/ai
# ---------------------------------------------------------------------------


def test_predict_yield_returns_a_prediction(client, db_session, ai_farms):
    response = client.post(
        "/api/ai/predict-yield",
        json={"batch_id": ai_farms["batch_a"]},
        headers=_headers(ai_farms["user_a"]),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["predicted_yield_kg"] > 0
    assert body["model"] == "v1-rule-based"
    assert db_session.query(YieldPrediction).count() == 1


def test_predict_yield_denies_another_tenants_batch(client, db_session, ai_farms):
    response = client.post(
        "/api/ai/predict-yield",
        json={"batch_id": ai_farms["batch_b"]},
        headers=_headers(ai_farms["user_a"]),
    )

    assert response.status_code == 404
    assert db_session.query(YieldPrediction).count() == 0


def test_predict_yield_requires_an_active_organization(client, ai_farms):
    response = client.post(
        "/api/ai/predict-yield",
        json={"batch_id": ai_farms["batch_a"]},
        headers=_headers(ai_farms["orphan"]),
    )

    assert response.status_code == 403


def test_analyze_image_returns_findings(client, ai_farms):
    response = client.post(
        "/api/ai/analyze-image",
        json={"batch_id": ai_farms["batch_a"], "image_url": "https://cdn.test/x.jpg"},
        headers=_headers(ai_farms["user_a"]),
    )

    assert response.status_code == 200
    assert response.json()["stage"]
    assert response.json()["recommendations"]


def test_analyze_image_denies_another_tenants_batch(client, ai_farms):
    response = client.post(
        "/api/ai/analyze-image",
        json={"batch_id": ai_farms["batch_b"], "image_url": "https://cdn.test/x.jpg"},
        headers=_headers(ai_farms["user_a"]),
    )

    assert response.status_code == 404


def test_chat_answers_a_general_question(client, ai_farms):
    response = client.post(
        "/api/ai/chat",
        json={"question": "Which recipe gives the best yield?"},
        headers=_headers(ai_farms["user_a"]),
    )

    assert response.status_code == 200
    assert response.json()["answer"]


def test_chat_denies_another_tenants_batch(client, ai_farms):
    response = client.post(
        "/api/ai/chat",
        json={"question": "Why is it slow?", "batch_id": ai_farms["batch_b"]},
        headers=_headers(ai_farms["user_a"]),
    )

    assert response.status_code == 404


def test_chat_validates_the_request_body(client, ai_farms):
    response = client.post("/api/ai/chat", json={}, headers=_headers(ai_farms["user_a"]))

    assert response.status_code == 422


@pytest.mark.parametrize(
    "path,payload",
    [
        ("/api/ai/predict-yield", {"batch_id": 1}),
        ("/api/ai/analyze-image", {"batch_id": 1, "image_url": "x"}),
        ("/api/ai/chat", {"question": "hi"}),
    ],
)
def test_ai_endpoints_require_authentication(client, path, payload):
    assert client.post(path, json=payload).status_code in (401, 403)


# ---------------------------------------------------------------------------
# /api/assistant
# ---------------------------------------------------------------------------


def test_assistant_chat_returns_answer_with_sources(client, ai_farms):
    response = client.post(
        "/api/assistant/chat",
        json={"question": "How do I raise humidity?"},
        headers=_headers(ai_farms["user_a"]),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert body["sources"]
    assert 0 < body["confidence"] <= 1


def test_assistant_chat_accepts_a_batch_from_the_same_tenant(client, ai_farms):
    response = client.post(
        "/api/assistant/chat",
        json={"question": "Why is growth slow?", "batch_id": ai_farms["batch_a"]},
        headers=_headers(ai_farms["user_a"]),
    )

    assert response.status_code == 200
    assert str(ai_farms["batch_a"]) in response.json()["answer"]


def test_assistant_chat_denies_another_tenants_batch(client, ai_farms):
    response = client.post(
        "/api/assistant/chat",
        json={"question": "Why is growth slow?", "batch_id": ai_farms["batch_b"]},
        headers=_headers(ai_farms["user_a"]),
    )

    assert response.status_code in (403, 404)


def test_document_upload_registers_the_document(client, db_session, ai_farms):
    response = client.post(
        "/api/assistant/documents/upload",
        files={"file": ("guide.txt", b"humidity guidance", "text/plain")},
        headers=_headers(ai_farms["user_a"]),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "uploaded"
    stored = db_session.query(KnowledgeDocument).filter_by(id=body["document_id"]).one()
    assert stored.filename == "guide.txt"
    assert stored.uploaded_by == ai_farms["user_a"].id


def test_document_upload_requires_authentication(client):
    response = client.post(
        "/api/assistant/documents/upload",
        files={"file": ("guide.txt", b"x", "text/plain")},
    )

    assert response.status_code in (401, 403)
