from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class BatchStage(str, Enum):
    PREPARATION = "PREPARATION"
    INOCULATION = "INOCULATION"
    COLONIZATION = "COLONIZATION"
    FRUITING = "FRUITING"
    HARVEST = "HARVEST"
    COMPLETED = "COMPLETED"

class BatchCreate(BaseModel):
    batch_number: str
    farm_id: int
    room_id: int
    strain_id: int
    recipe_version_id: int
    start_date: datetime

class BatchResponse(BaseModel):
    id: int
    batch_number: str
    current_stage: BatchStage
    status: str
    class Config:
        from_attributes = True