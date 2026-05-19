"""Tests for recipe creation and versioning (app.services.recipe_service)."""
import pytest
from fastapi import HTTPException

from app.schemas.recipe import Ingredient, RecipeCreate, RecipeVersionCreate
from app.services import recipe_service


def _recipe_in(name="Oyster substrate"):
    return RecipeCreate(
        name=name,
        description="A classic mix",
        ingredients=[Ingredient(name="sawdust", percentage=80.0)],
        hydration_percentage=62.5,
        spawn_ratio=3.0,
    )


def test_create_recipe_persists_initial_version(db_session):
    recipe = recipe_service.create_recipe(db_session, farm_id=None, recipe_in=_recipe_in(), organization_id=1)
    assert recipe.id
    assert recipe.organization_id == 1
    assert recipe.latest_version_id is not None
    assert recipe.versions[0].version == 1


def test_create_recipe_version_increments(db_session):
    recipe = recipe_service.create_recipe(db_session, None, _recipe_in(), 1)
    v2 = recipe_service.create_recipe_version(
        db_session,
        recipe.id,
        RecipeVersionCreate(
            ingredients=[Ingredient(name="sawdust", percentage=70.0)],
            hydration_percentage=65.0,
            spawn_ratio=2.5,
            notes="drier mix",
        ),
        organization_id=1,
    )
    assert v2.version == 2


def test_create_version_cross_tenant_denied(db_session):
    recipe = recipe_service.create_recipe(db_session, None, _recipe_in(), 1)
    with pytest.raises(HTTPException) as exc:
        recipe_service.create_recipe_version(
            db_session, recipe.id,
            RecipeVersionCreate(
                ingredients=[Ingredient(name="sawdust", percentage=70.0)],
                hydration_percentage=65.0, spawn_ratio=2.5,
            ),
            organization_id=99,
        )
    assert exc.value.status_code == 404


def test_recipe_performance_summary(db_session):
    recipe = recipe_service.create_recipe(db_session, None, _recipe_in(), 1)
    perf = recipe_service.get_recipe_performance(db_session, recipe.id, 1)
    assert {"total_batches", "average_yield", "success_rate"} <= set(perf)
