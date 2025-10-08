import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def test_user_a_can_access_own_batch(client, tenant_test_data):
    """User A should be able to access their own batch"""
    data = tenant_test_data
    
    response = client.get(
        f"/api/batches/{data['batch_a']}",
        headers={"Authorization": f"Bearer {data['token_a']}"}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_user_a_cannot_access_org_b_batch(client, tenant_test_data):
    """User A should NOT be able to access Org B's batch"""
    data = tenant_test_data
    
    response = client.get(
        f"/api/batches/{data['batch_b']}",
        headers={"Authorization": f"Bearer {data['token_a']}"}
    )
    
    assert response.status_code in [403, 404], f"Expected 403/404, got {response.status_code}"

def test_user_b_cannot_access_org_a_recipe(client, tenant_test_data):
    """User B should NOT be able to access Org A's recipe"""
    data = tenant_test_data
    
    response = client.get(
        f"/api/recipes/{data['recipe_a']}",
        headers={"Authorization": f"Bearer {data['token_b']}"}
    )
    
    assert response.status_code in [403, 404], f"Expected 403/404, got {response.status_code}"

def test_user_b_can_access_own_inventory(client, tenant_test_data):
    """User B should only see inventory owned by organization B."""
    data = tenant_test_data

    response = client.get(
        "/api/inventory/items",
        headers={"Authorization": f"Bearer {data['token_b']}"}
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    returned_ids = {item["id"] for item in response.json()}
    assert data["inventory_b"] in returned_ids
    assert data["inventory_a"] not in returned_ids