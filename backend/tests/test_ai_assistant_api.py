"""Tests for AI Assistant Chat endpoint."""
import pytest
from app.models.batch import Batch
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.core.security import get_password_hash, create_access_token
from datetime import datetime


@pytest.fixture
def ai_assistant_fixtures(db_session):
    org = Organization(name="AI Chat Farm", slug="ai-chat-farm", is_active=True, created_at=datetime.utcnow())
    db_session.add(org)
    db_session.flush()

    worker = User(
        name="Chat Worker",
        email="worker@aichat.com",
        password_hash=get_password_hash("password123"),
        role="WORKER",
        current_organization_id=org.id,
    )
    db_session.add(worker)
    db_session.flush()
    db_session.add(OrganizationMember(organization_id=org.id, user_id=worker.id, role="MEMBER", joined_at=datetime.utcnow()))

    batch = Batch(batch_number="BATCH-CHAT-1", status="active", organization_id=org.id, created_at=datetime.utcnow())
    db_session.add(batch)
    db_session.commit()

    token = create_access_token({"sub": str(worker.id), "role": worker.role})
    return {
        "org_id": org.id,
        "batch_id": batch.id,
        "token": token,
    }


def test_ai_assistant_chat_unauthenticated(client):
    response = client.post("/api/ai/assistant/chat", json={"question": "How do I optimize humidity?"})
    assert response.status_code == 401


def test_ai_assistant_chat_success(client, ai_assistant_fixtures):
    headers = {"Authorization": f"Bearer {ai_assistant_fixtures['token']}"}
    response = client.post(
        "/api/ai/assistant/chat",
        json={"question": "What is the optimal humidity for fruiting oyster mushrooms?", "batch_id": ai_assistant_fixtures["batch_id"]},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
