from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.recipe import RecipeCreate, RecipeVersionCreate, RecipeResponse, RecipeVersionResponse
from app.services.recipe_service import create_recipe, create_recipe_version, get_recipe_performance
from app.core.dependencies import manager_only
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=RecipeResponse)
def create_new_recipe(
    recipe_in: RecipeCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only)
):
    # In production, get farm_id from current_user
    return create_recipe(db, farm_id=1, recipe_in=recipe_in)

@router.post("/{recipe_id}/versions", response_model=RecipeVersionResponse)
def add_recipe_version(
    recipe_id: int, 
    version_in: RecipeVersionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only)
):
    return create_recipe_version(db, recipe_id, version_in)

@router.get("/{recipe_id}/performance")
def get_recipe_performance_endpoint(
    recipe_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only)
):
    return get_recipe_performance(db, recipe_id)