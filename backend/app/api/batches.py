from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import manager_only, worker_access
from app.core.tenant import get_current_organization
from app.database.database import get_db
from app.models.batch import Batch
from app.models.user import User
from app.schemas.batch import BatchCreate, BatchResponse, BatchStageUpdate
from app.services.batch_service import create_batch as create_tenant_batch
from app.services.batch_service import update_batch_stage

router = APIRouter()


@router.get("/", response_model=List[BatchResponse])
def get_batches(
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    return db.query(Batch).filter(Batch.organization_id == organization_id).all()


@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    batch = db.query(Batch).filter(
        Batch.id == batch_id,
        Batch.organization_id == organization_id,
    ).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.post("/", response_model=BatchResponse)
def create_batch(
    batch_in: BatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return create_tenant_batch(db, batch_in.model_dump(), organization_id)


@router.patch("/{batch_id}/stage", response_model=BatchResponse)
def update_stage(
    batch_id: int,
    update: BatchStageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    try:
        return update_batch_stage(db, batch_id, update.stage.value, organization_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
