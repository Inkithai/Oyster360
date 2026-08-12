from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import worker_access
from app.core.tenant import get_current_organization
from app.core.tenant_enforcer import TenantEnforcer
from app.database.database import get_db
from app.models.batch import Batch, BatchStage
from app.models.harvest import Harvest
from app.models.user import User

router = APIRouter()


class HarvestCreate(BaseModel):
    quantity_kg: float = Field(gt=0)
    quality_score: float = Field(ge=0, le=100)
    selling_price: float = Field(ge=0)


@router.post("/batches/{batch_id}/harvest")
def record_harvest(
    batch_id: int,
    harvest_in: HarvestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    batch = TenantEnforcer(db, organization_id).safe_get(Batch, batch_id)
    harvest = Harvest(
        batch_id=batch_id,
        organization_id=organization_id,
        quantity_kg=harvest_in.quantity_kg,
        quality_score=harvest_in.quality_score,
        harvest_date=datetime.utcnow(),
        selling_price=harvest_in.selling_price,
    )
    db.add(harvest)
    batch.current_stage = BatchStage.COMPLETED
    db.commit()

    return {
        "message": "Harvest recorded",
        "total_yield_kg": harvest_in.quantity_kg,
        "revenue": harvest_in.quantity_kg * harvest_in.selling_price,
    }
