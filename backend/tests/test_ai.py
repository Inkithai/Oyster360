import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ai_chat_endpoint():
    response = client.post("/api/ai/assistant/chat", json={
        "question": "Why is this batch growing slowly?",
        "batch_id": 1
    })
    # Should return 200 or 401 (if auth required)
    assert response.status_code in [200, 401]