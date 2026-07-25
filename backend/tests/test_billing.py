import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_checkout_session():
    """Test checkout session creation"""
    response = client.post("/api/billing/create-checkout-session", json={
        "price_id": "price_test123",
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel"
    })
    # Should require authentication
    assert response.status_code in [401, 403]

def test_get_subscription():
    """Test getting subscription"""
    response = client.get("/api/billing/subscription")
    # Should require authentication
    assert response.status_code in [401, 403]