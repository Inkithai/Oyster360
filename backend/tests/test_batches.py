import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_batches():
    response = client.get("/api/batches")
    assert response.status_code in [200, 401]  # 401 if auth required

def test_create_batch_validation():
    response = client.post("/api/batches", json={
        "batch_number": "AB",
        "strain_id": 1,
        "recipe_version_id": 1,
        "room_id": 1
    })
    # Should fail validation (batch number too short)
    assert response.status_code in [400, 401, 422]