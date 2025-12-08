from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import manager_only, worker_access
from app.core.tenant import get_current_organization
from app.core.tenant_enforcer import TenantEnforcer
from app.database.database import get_db
from app.models.batch import Batch
from app.models.harvest import Harvest
from app.models.harvest_grade import GradeLevel
from app.models.user import User
from app.services.harvest_grade_service import HarvestGradeService

router = APIRouter()


class GradeCreate(BaseModel):
    harvest_id: int
    batch_id: int
    grade: GradeLevel
    quantity_kg: float = Field(gt=0)
    price_per_kg: float = Field(ge=0)
    notes: str = ""


@router.post("/")
def record_harvest_grade(
    data: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    enforcer = TenantEnforcer(db, organization_id)
    enforcer.safe_get(Batch, data.batch_id)
    harvest = enforcer.safe_get(Harvest, data.harvest_id)
    if harvest.batch_id != data.batch_id:
        raise HTTPException(status_code=400, detail="Harvest does not match the batch")

    return HarvestGradeService(db).record_grade(
        harvest_id=data.harvest_id,
        batch_id=data.batch_id,
        grade=data.grade.value,
        quantity_kg=data.quantity_kg,
        price_per_kg=data.price_per_kg,
        notes=data.notes,
        user_id=current_user.id,
    )


@router.get("/batches/{batch_id}")
def get_grades_by_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    TenantEnforcer(db, organization_id).safe_get(Batch, batch_id)
    return HarvestGradeService(db).get_grades_by_batch(batch_id)
