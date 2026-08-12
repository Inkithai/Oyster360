from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import worker_access
from app.core.tenant import get_current_organization
from app.core.tenant_enforcer import TenantEnforcer
from app.database.database import get_db
from app.models.batch import Batch
from app.models.growth_log import GrowthLog
from app.models.user import User

router = APIRouter()


class GrowthLogCreate(BaseModel):
    stage: str
    notes: str
    health_score: float = Field(ge=0, le=100)
    image_url: str | None = None


@router.post("/batches/{batch_id}/growth-logs")
def create_growth_log(
    batch_id: int,
    log: GrowthLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    TenantEnforcer(db, organization_id).safe_get(Batch, batch_id)
    growth_log = GrowthLog(
        batch_id=batch_id,
        organization_id=organization_id,
        stage=log.stage,
        notes=log.notes,
        health_score=log.health_score,
        image_url=log.image_url,
        created_at=datetime.utcnow(),
    )
    db.add(growth_log)
    db.commit()
    return {"message": "Growth log recorded"}


@router.get("/batches/{batch_id}/timeline")
def get_batch_timeline(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    TenantEnforcer(db, organization_id).safe_get(Batch, batch_id)
    logs = db.query(GrowthLog).filter(
        GrowthLog.batch_id == batch_id,
        GrowthLog.organization_id == organization_id,
    ).order_by(GrowthLog.created_at).all()
    return [
        {
            "date": log.created_at.strftime("%Y-%m-%d"),
            "stage": log.stage,
            "health_score": log.health_score,
            "notes": log.notes,
        }
        for log in logs
    ]
