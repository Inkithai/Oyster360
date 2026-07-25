import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.organization import Organization, OrganizationMember
from app.models.farm import Farm
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

def test_registration_creates_tenant_without_role_escalation(client, db_session):
    response = client.post("/api/auth/register", json={
        "name": "New Owner",
        "email": "owner@example.com",
        "password": "secure-password-123",
        "farm_name": "Sunrise Mushrooms",
        "role": "ADMIN",
    })

    assert response.status_code == 200
    assert response.json()["role"] == "FARM_MANAGER"

    user = db_session.query(User).filter(User.email == "owner@example.com").one()
    organization = db_session.query(Organization).filter(
        Organization.id == user.current_organization_id
    ).one()
    assert organization.name == "Sunrise Mushrooms"
    assert db_session.query(OrganizationMember).filter_by(
        organization_id=organization.id,
        user_id=user.id,
        role="OWNER",
    ).count() == 1
    assert db_session.query(Farm).filter_by(
        organization_id=organization.id,
        owner_id=user.id,
    ).count() == 1


def test_user_login_success(client, auth_test_user):
    """Test successful login"""
    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_login_invalid_credentials(client, auth_test_user):
    """Test login with invalid credentials"""
    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_refresh_token_rejects_invalid_token(client):
    """Test refresh token endpoint rejects an unknown token."""
    response = client.post("/api/auth/refresh-token", json={
        "refresh_token": "invalid_token"
    })
    assert response.status_code == 401


def test_refresh_token_rotates_token(client, auth_test_user):
    login_response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "testpass123"
    })
    original_refresh_token = login_response.json()["refresh_token"]

    response = client.post("/api/auth/refresh-token", json={
        "refresh_token": original_refresh_token
    })
    assert response.status_code == 200
    assert response.json()["refresh_token"] != original_refresh_token

    replay = client.post("/api/auth/refresh-token", json={
        "refresh_token": original_refresh_token
    })
    assert replay.status_code == 401

def test_forgot_password(client, auth_test_user):
    """Test forgot password endpoint"""
    response = client.post("/api/auth/forgot-password", json={
        "email": "test@test.com"
    })
    assert response.status_code == 200
    assert "message" in response.json()

def test_reset_password_flow(client, db_session, auth_test_user):
    response = client.post("/api/auth/forgot-password", json={
        "email": "test@test.com"
    })
    assert response.status_code == 200

    db_session.refresh(auth_test_user)
    reset_token = auth_test_user.password_reset_token
    assert reset_token

    response = client.post("/api/auth/reset-password", json={
        "token": reset_token,
        "new_password": "new-password-123"
    })
    assert response.status_code == 200

    replay = client.post("/api/auth/reset-password", json={
        "token": reset_token,
        "new_password": "another-password-123"
    })
    assert replay.status_code == 400

    login = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "new-password-123"
    })
    assert login.status_code == 200


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