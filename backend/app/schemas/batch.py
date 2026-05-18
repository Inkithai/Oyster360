from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BatchStage(str, Enum):
    PREPARATION = "PREPARATION"
    INOCULATION = "INOCULATION"
    COLONIZATION = "COLONIZATION"
    FRUITING = "FRUITING"
    HARVEST = "HARVEST"
    COMPLETED = "COMPLETED"


class BatchCreate(BaseModel):
    batch_number: str = Field(min_length=3)
    farm_id: Optional[int] = None
    room_id: int
    strain_id: int
    recipe_version_id: int
    start_date: datetime = Field(default_factory=datetime.utcnow)


class BatchStageUpdate(BaseModel):
    stage: BatchStage


class BatchResponse(BaseModel):
    id: int
    batch_number: str
    current_stage: BatchStage
    status: str

    model_config = {"from_attributes": True}
