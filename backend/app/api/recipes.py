from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import manager_only, worker_access
from app.core.tenant import get_current_organization
from app.database.database import get_db
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.recipe import (
    RecipeCreate,
    RecipeResponse,
    RecipeVersionCreate,
    RecipeVersionResponse,
)
from app.services.recipe_service import (
    create_recipe,
    create_recipe_version,
    get_recipe_performance,
)

router = APIRouter()


@router.get("/", response_model=List[RecipeResponse])
def get_recipes(
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    return db.query(Recipe).filter(Recipe.organization_id == organization_id).all()


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    from app.core.tenant_enforcer import TenantEnforcer

    return TenantEnforcer(db, organization_id).safe_get(Recipe, recipe_id)


@router.post("/", response_model=RecipeResponse)
def create_new_recipe(
    recipe_in: RecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return create_recipe(
        db,
        farm_id=None,
        recipe_in=recipe_in,
        organization_id=organization_id,
    )


@router.post("/{recipe_id}/versions", response_model=RecipeVersionResponse)
def add_recipe_version(
    recipe_id: int,
    version_in: RecipeVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return create_recipe_version(db, recipe_id, version_in, organization_id)


@router.get("/{recipe_id}/performance")
def get_recipe_performance_endpoint(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return get_recipe_performance(db, recipe_id, organization_id)
