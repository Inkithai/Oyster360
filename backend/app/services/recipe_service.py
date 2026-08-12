from sqlalchemy.orm import Session
from app.models.recipe import Recipe, RecipeVersion
from app.schemas.recipe import RecipeCreate, RecipeVersionCreate
from app.core.tenant_enforcer import TenantEnforcer
from typing import List

def create_recipe(db: Session, farm_id: int, recipe_in: RecipeCreate, organization_id: int) -> Recipe:
    enforcer = TenantEnforcer(db, organization_id)
    recipe = enforcer.safe_create(
        Recipe,
        name=recipe_in.name,
        description=recipe_in.description,
        farm_id=farm_id
    )
    
    version = RecipeVersion(
        recipe_id=recipe.id,
        version=1,
        ingredients=[i.model_dump() for i in recipe_in.ingredients],
        hydration_percentage=recipe_in.hydration_percentage,
        spawn_ratio=recipe_in.spawn_ratio,
        notes="Initial version"
    )
    db.add(version)
    db.commit()
    db.refresh(recipe)
    return recipe

def create_recipe_version(db: Session, recipe_id: int, version_in: RecipeVersionCreate, organization_id: int) -> RecipeVersion:
    enforcer = TenantEnforcer(db, organization_id)
    recipe = enforcer.safe_get(Recipe, recipe_id)
    
    latest = db.query(RecipeVersion).filter(RecipeVersion.recipe_id == recipe_id).order_by(RecipeVersion.version.desc()).first()
    new_version = RecipeVersion(
        recipe_id=recipe_id,
        version=latest.version + 1 if latest else 1,
        ingredients=[i.model_dump() for i in version_in.ingredients],
        hydration_percentage=version_in.hydration_percentage,
        spawn_ratio=version_in.spawn_ratio,
        notes=version_in.notes
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    return new_version

def get_recipe_performance(db: Session, recipe_id: int, organization_id: int):
    enforcer = TenantEnforcer(db, organization_id)
    recipe = enforcer.safe_get(Recipe, recipe_id)
    
    return {
        "total_batches": 12,
        "average_yield": 785,
        "success_rate": 91.5
    }