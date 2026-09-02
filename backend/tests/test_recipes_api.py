"""Tests for recipes API endpoints."""
import pytest
from app.models.recipe import Recipe
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.core.security import get_password_hash, create_access_token
from datetime import datetime


@pytest.fixture
def recipe_fixtures(db_session):
    org_a = Organization(name="Recipe Farm A", slug="recipe-farm-a", is_active=True, created_at=datetime.utcnow())
    org_b = Organization(name="Recipe Farm B", slug="recipe-farm-b", is_active=True, created_at=datetime.utcnow())
    db_session.add_all([org_a, org_b])
    db_session.flush()

    manager_a = User(
        name="Recipe Manager",
        email="manager@recipe.com",
        password_hash=get_password_hash("password123"),
        role="FARM_MANAGER",
        current_organization_id=org_a.id,
    )
    worker_a = User(
        name="Recipe Worker",
        email="worker@recipe.com",
        password_hash=get_password_hash("password123"),
        role="WORKER",
        current_organization_id=org_a.id,
    )
    db_session.add_all([manager_a, worker_a])
    db_session.flush()

    db_session.add(OrganizationMember(organization_id=org_a.id, user_id=manager_a.id, role="OWNER", joined_at=datetime.utcnow()))
    db_session.add(OrganizationMember(organization_id=org_a.id, user_id=worker_a.id, role="MEMBER", joined_at=datetime.utcnow()))

    r_a = Recipe(name="Standard Sawdust", description="Hardwood sawdust substrate", organization_id=org_a.id, created_at=datetime.utcnow())
    r_b = Recipe(name="Straw Substrate", description="Wheat straw substrate", organization_id=org_b.id, created_at=datetime.utcnow())
    db_session.add_all([r_a, r_b])
    db_session.commit()

    mgr_token = create_access_token({"sub": str(manager_a.id), "role": manager_a.role})
    wrk_token = create_access_token({"sub": str(worker_a.id), "role": worker_a.role})

    return {
        "org_a": org_a.id,
        "recipe_a_id": r_a.id,
        "recipe_b_id": r_b.id,
        "mgr_token": mgr_token,
        "wrk_token": wrk_token,
    }


def test_get_recipes(client, recipe_fixtures):
    headers = {"Authorization": f"Bearer {recipe_fixtures['wrk_token']}"}
    response = client.get("/api/recipes/", headers=headers)
    assert response.status_code == 200
    recipes = response.json()
    assert len(recipes) == 1
    assert recipes[0]["name"] == "Standard Sawdust"


def test_get_recipe_by_id(client, recipe_fixtures):
    headers = {"Authorization": f"Bearer {recipe_fixtures['wrk_token']}"}
    response = client.get(f"/api/recipes/{recipe_fixtures['recipe_a_id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Standard Sawdust"

    # Cross-tenant access denied
    res_b = client.get(f"/api/recipes/{recipe_fixtures['recipe_b_id']}", headers=headers)
    assert res_b.status_code == 404


def test_create_recipe(client, recipe_fixtures):
    headers = {"Authorization": f"Bearer {recipe_fixtures['mgr_token']}"}
    payload = {
        "name": "Master's Mix",
        "description": "50% oak sawdust and 50% soybean hulls",
        "ingredients": [{"name": "Oak sawdust", "percentage": 50.0}, {"name": "Soy hulls", "percentage": 50.0}],
        "hydration_percentage": 60.0,
        "spawn_ratio": 10.0,
    }
    response = client.post("/api/recipes/", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Master's Mix"


def test_create_recipe_version(client, recipe_fixtures):
    headers = {"Authorization": f"Bearer {recipe_fixtures['mgr_token']}"}
    payload = {
        "ingredients": [{"name": "Oak sawdust", "percentage": 60.0}, {"name": "Soy hulls", "percentage": 40.0}],
        "hydration_percentage": 62.0,
        "spawn_ratio": 12.0,
        "notes": "Increased oak proportion",
    }
    response = client.post(
        f"/api/recipes/{recipe_fixtures['recipe_a_id']}/versions",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["version"] >= 1


def test_get_recipe_performance(client, recipe_fixtures):
    headers = {"Authorization": f"Bearer {recipe_fixtures['mgr_token']}"}
    response = client.get(
        f"/api/recipes/{recipe_fixtures['recipe_a_id']}/performance",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_batches" in data
    assert "average_yield" in data
    assert "success_rate" in data
