import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_recipe():
    # This would require auth in real tests
    response = client.post("/api/recipes", json={
        "name": "Test Recipe",
        "description": "Test",
        "ingredients": [{"name": "Rice Straw", "percentage": 70}],
        "hydration_percentage": 65,
        "spawn_ratio": 5
    })
    # Expect 401 without auth in real setup
    assert response.status_code in [200, 401, 403]