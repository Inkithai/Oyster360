"""
Test Configuration and Fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import get_db
from app.models.base import Base
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.models.batch import Batch
from app.models.recipe import Recipe
from app.models.room import Room
from app.models.inventory import InventoryItem
from app.core.security import get_password_hash, create_access_token
from datetime import datetime

# Use SQLite in-memory database for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

from sqlalchemy.pool import StaticPool

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory database for each test"""
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def tenant_test_data(db_session):
    """Create two isolated organizations with data using the test database"""
    db = db_session
    
    # Organizations
    org_a = Organization(name="Org A", slug="org-a", created_at=datetime.utcnow())
    org_b = Organization(name="Org B", slug="org-b", created_at=datetime.utcnow())
    db.add_all([org_a, org_b])
    db.flush()
    
    # Users
    user_a = User(
        name="User A", email="user_a@test.com", 
        password_hash=get_password_hash("pass123"), role="ADMIN",
        current_organization_id=org_a.id
    )
    user_b = User(
        name="User B", email="user_b@test.com", 
        password_hash=get_password_hash("pass123"), role="ADMIN",
        current_organization_id=org_b.id
    )
    db.add_all([user_a, user_b])
    db.flush()
    
    # Memberships
    db.add_all([
        OrganizationMember(organization_id=org_a.id, user_id=user_a.id, role="OWNER", joined_at=datetime.utcnow()),
        OrganizationMember(organization_id=org_b.id, user_id=user_b.id, role="OWNER", joined_at=datetime.utcnow())
    ])
    
    # Org A Resources
    batch_a = Batch(batch_number="BATCH-A", organization_id=org_a.id, status="active", created_at=datetime.utcnow())
    recipe_a = Recipe(name="Recipe A", organization_id=org_a.id, created_at=datetime.utcnow())
    room_a = Room(name="Room A", organization_id=org_a.id, capacity=100)
    inventory_a = InventoryItem(name="Spawn A", category="SPAWN", organization_id=org_a.id, created_at=datetime.utcnow())
    
    # Org B Resources
    batch_b = Batch(batch_number="BATCH-B", organization_id=org_b.id, status="active", created_at=datetime.utcnow())
    recipe_b = Recipe(name="Recipe B", organization_id=org_b.id, created_at=datetime.utcnow())
    room_b = Room(name="Room B", organization_id=org_b.id, capacity=200)
    inventory_b = InventoryItem(name="Spawn B", category="SPAWN", organization_id=org_b.id, created_at=datetime.utcnow())
    
    db.add_all([batch_a, recipe_a, room_a, inventory_a, batch_b, recipe_b, room_b, inventory_b])
    db.commit()
    
    # Generate tokens
    token_a = create_access_token({"sub": str(user_a.id), "role": user_a.role})
    token_b = create_access_token({"sub": str(user_b.id), "role": user_b.role})
    
    return {
        "org_a": org_a.id, "org_b": org_b.id,
        "user_a": user_a.id, "user_b": user_b.id,
        "token_a": token_a, "token_b": token_b,
        "batch_a": batch_a.id, "batch_b": batch_b.id,
        "recipe_a": recipe_a.id, "recipe_b": recipe_b.id,
        "room_a": room_a.id, "room_b": room_b.id,
        "inventory_a": inventory_a.id, "inventory_b": inventory_b.id
    }

@pytest.fixture(scope="function")
def auth_test_data(db_session):
    """Create test user for authentication tests"""
    db = db_session
    
    user = User(
        name="Test User", 
        email="test@test.com", 
        password_hash=get_password_hash("testpass123"), 
        role="ADMIN"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate token
    token = create_access_token({"sub": str(user.id), "role": user.role})
    
    return {
        "user": user,
        "token": token,
        "email": "test@test.com",
        "password": "testpass123"
    }

@pytest.fixture(scope="function")
def auth_client(db_session):
    """Create test client with overridden database for auth tests"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()