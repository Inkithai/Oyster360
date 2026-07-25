from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Ingredient(BaseModel):
    name: str
    percentage: float

class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: List[Ingredient]
    hydration_percentage: float
    spawn_ratio: float

class RecipeVersionCreate(BaseModel):
    ingredients: List[Ingredient]
    hydration_percentage: float
    spawn_ratio: float
    notes: Optional[str] = None

class RecipeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    latest_version_id: Optional[int] = None

    model_config = {"from_attributes": True}

class RecipeVersionResponse(BaseModel):
    id: int
    version: int
    ingredients: List[dict]
    hydration_percentage: float
    spawn_ratio: float
    notes: Optional[str]

    model_config = {"from_attributes": True}