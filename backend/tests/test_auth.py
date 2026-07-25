import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.refresh_token import RefreshToken
from datetime import datetime, timedelta

client = TestClient(app)

@pytest.fixture(scope="function")
def auth_test_user(db_session):
    """Create a test user for authentication tests"""
    user = User(
        name="Test User",
        email="test@test.com",
        password_hash=get_password_hash("testpass123"),
        role="ADMIN"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_user_login_success(client, auth_test_user):
    """Test successful login"""
    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(client, auth_test_user):
    """Test login with invalid credentials"""
    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_refresh_token_without_token(client):
    """Test refresh token endpoint requires valid token"""
    response = client.post("/api/auth/refresh-token", json={
        "refresh_token": "invalid_token"
    })
    assert response.status_code == 422

def test_forgot_password(client, auth_test_user):
    """Test forgot password endpoint"""
    response = client.post("/api/auth/forgot-password", params={
        "email": "test@test.com"
    })
    assert response.status_code == 200
    assert "message" in response.json()

def test_change_password_with_wrong_current_password(client, auth_test_user):
    """Test change password with incorrect current password"""
    # First login to get token
    login_response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    response = client.post(
        "/api/auth/change-password",
        params={"current_password": "wrongpassword", "new_password": "newpass123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_security_headers_present(client):
    """Test security headers are present in responses"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers