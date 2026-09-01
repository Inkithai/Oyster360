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
from types import SimpleNamespace


@pytest.fixture(autouse=True)
def block_outbound_sockets(request, monkeypatch):
    """Fail any test in the default lane that opens a real network connection.

    The unit lane must be runnable in a network-disabled sandbox (verified with
    ``unshare -rn`` and in CI). Rather than relying on every service being
    mocked by convention, this fixture makes an escaped connection a loud test
    failure. Tests marked ``integration`` are exempt because they intentionally
    talk to the Compose-provided PostgreSQL and Redis.
    """
    import socket

    if request.node.get_closest_marker("integration"):
        return

    real_connect = socket.socket.connect

    def guarded_connect(self, address, *args, **kwargs):
        # AF_UNIX and loopback are allowed: TestClient and SQLite need them.
        if self.family in (socket.AF_INET, socket.AF_INET6):
            host = address[0] if isinstance(address, tuple) else address
            if host not in ("127.0.0.1", "::1", "localhost"):
                raise AssertionError(
                    f"Outbound network connection to {host} attempted in a unit test. "
                    "Mock the external service, or mark the test with "
                    "@pytest.mark.integration."
                )
        return real_connect(self, address, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)


@pytest.fixture(autouse=True)
def block_external_services(monkeypatch):
    """Keep every test deterministic and prevent accidental billable API calls.

    Stripe, outbound HTTP (OpenAI/Anthropic/any provider) and Redis are all
    replaced with in-process stubs so the default lane needs no credentials,
    no internet access and no running infrastructure.
    """
    import requests
    import stripe

    def unexpected_network(*args, **kwargs):
        raise AssertionError("External HTTP calls are disabled in tests")

    for verb in ("get", "post", "put", "patch", "delete", "head", "request"):
        monkeypatch.setattr(requests, verb, unexpected_network)
    monkeypatch.setattr(
        stripe.Customer,
        "create",
        lambda **kwargs: SimpleNamespace(id="cus_test", **kwargs),
    )
    monkeypatch.setattr(
        stripe.checkout.Session,
        "create",
        lambda **kwargs: SimpleNamespace(id="cs_test", url="https://stripe.test/checkout"),
    )
    monkeypatch.setattr(
        stripe.billing_portal.Session,
        "create",
        lambda **kwargs: SimpleNamespace(url="https://stripe.test/portal"),
    )
    monkeypatch.setattr(
        stripe.Price,
        "create",
        lambda **kwargs: SimpleNamespace(id="price_test", **kwargs),
    )
    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        lambda payload, signature, secret: {"type": "test.event", "data": {"object": {}}},
    )
    monkeypatch.setattr(
        stripe.Subscription,
        "retrieve",
        lambda subscription_id: SimpleNamespace(id=subscription_id, status="active"),
    )
    monkeypatch.setattr(
        stripe.Subscription,
        "modify",
        lambda subscription_id, **kwargs: SimpleNamespace(id=subscription_id, **kwargs),
    )


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
    engine.dispose()

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