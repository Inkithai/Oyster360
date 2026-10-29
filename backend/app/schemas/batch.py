from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, computed_field


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
    expected_harvest_date: Optional[datetime] = None
    bags_prepared: int = Field(default=500, ge=1)
    bags_inoculated: Optional[int] = Field(default=None, ge=0)
    bags_contaminated: int = Field(default=0, ge=0)
    bags_harvested: int = Field(default=0, ge=0)
    notes: Optional[str] = None


class BatchStageUpdate(BaseModel):
    stage: BatchStage


class BatchBagUpdate(BaseModel):
    bags_prepared: Optional[int] = Field(default=None, ge=1)
    bags_inoculated: Optional[int] = Field(default=None, ge=0)
    bags_contaminated: Optional[int] = Field(default=None, ge=0)
    bags_harvested: Optional[int] = Field(default=None, ge=0)
    expected_harvest_date: Optional[datetime] = None
    notes: Optional[str] = None


class BatchResponse(BaseModel):
    id: int
    batch_number: str
    current_stage: BatchStage
    status: str
    start_date: Optional[datetime] = None
    expected_harvest_date: Optional[datetime] = None
    bags_prepared: int = 500
    bags_inoculated: int = 500
    bags_contaminated: int = 0
    bags_harvested: int = 0
    notes: Optional[str] = None

    model_config = {"from_attributes": True}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def active_healthy_bags(self) -> int:
        inoculated = self.bags_inoculated or self.bags_prepared or 0
        contaminated = self.bags_contaminated or 0
        return max(0, inoculated - contaminated)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def contamination_rate_pct(self) -> float:
        base = self.bags_inoculated or self.bags_prepared or 0
        if base <= 0:
            return 0.0
        return round(((self.bags_contaminated or 0) / base) * 100.0, 1)


def default_expected_harvest(start_date: datetime, cycle_days: int = 28) -> datetime:
    return start_date + timedelta(days=cycle_days)
