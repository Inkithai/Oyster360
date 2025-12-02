import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_organization():
    """Test organization creation"""
    response = client.post("/api/organizations", json={
        "name": "Test Org",
        "slug": "test-org"
    })
    # Should require authentication
    assert response.status_code in [401, 403]

def test_get_user_organizations():
    """Test getting user organizations"""
    response = client.get("/api/organizations/my-organizations")
    # Should require authentication
    assert response.status_code in [401, 403]