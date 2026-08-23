"""
Integration Tests for Oyster360
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.models.batch import Batch
from datetime import datetime

# End-to-end lifecycle flows. CI runs these in the dedicated docker-integration
# job; the fast unit lane excludes them with `pytest -m "not integration"`.
pytestmark = pytest.mark.integration

@pytest.fixture
def test_organization(db_session):
    """Create test organization"""
    org = Organization(name="Test Org", slug="test-org", created_at=datetime.utcnow())
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org

@pytest.fixture
def test_user(db_session, test_organization):
    """Create test user"""
    user = User(
        name="Test User",
        email="integration@test.com",
        password_hash=get_password_hash("testpass123"),
        role="ADMIN",
        current_organization_id=test_organization.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Add to organization
    member = OrganizationMember(
        organization_id=test_organization.id,
        user_id=user.id,
        role="OWNER",
        joined_at=datetime.utcnow()
    )
    db_session.add(member)
    db_session.commit()
    
    return user

def test_complete_batch_lifecycle(client, db_session, test_user, test_organization):
    """Test complete batch creation and management flow"""
    token = create_access_token({"sub": str(test_user.id), "role": test_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create batch
    response = client.post("/api/batches", json={
        "batch_number": "INTEGRATION-001",
        "farm_id": 1,
        "room_id": 1,
        "strain_id": 1,
        "recipe_version_id": 1,
        "start_date": "2026-01-01T00:00:00"
    }, headers=headers)
    
    assert response.status_code == 200
    batch_id = response.json()["id"]
    
    # 2. Update batch stage
    response = client.patch(
        f"/api/batches/{batch_id}/stage",
        json={"stage": "INOCULATION"},
        headers=headers
    )
    assert response.status_code == 200
    
    # 3. Verify batch exists
    response = client.get(f"/api/batches/{batch_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["current_stage"] == "INOCULATION"

def test_organization_isolation(client, db_session, test_user, test_organization):
    """Test that users cannot access other organizations' data"""
    # Create another organization
    other_org = Organization(name="Other Org", slug="other-org", created_at=datetime.utcnow())
    db_session.add(other_org)
    db_session.commit()
    db_session.refresh(other_org)
    
    # Create user in other organization
    other_user = User(
        name="Other User",
        email="other@test.com",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
        current_organization_id=other_org.id
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)
    
    # Add membership
    member = OrganizationMember(
        organization_id=other_org.id,
        user_id=other_user.id,
        role="OWNER",
        joined_at=datetime.utcnow()
    )
    db_session.add(member)
    db_session.commit()
    
    token_a = create_access_token({"sub": str(test_user.id), "role": test_user.role})
    token_b = create_access_token({"sub": str(other_user.id), "role": other_user.role})
    
    # Create batch in Org A
    response = client.post("/api/batches", json={
        "batch_number": "ORG-A-BATCH",
        "farm_id": 1,
        "room_id": 1,
        "strain_id": 1,
        "recipe_version_id": 1,
        "start_date": "2026-01-01T00:00:00"
    }, headers={"Authorization": f"Bearer {token_a}"})
    
    batch_id = response.json()["id"]
    
    # User B should not access Org A's batch
    response = client.get(
        f"/api/batches/{batch_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code in [403, 404]