from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.batch import Batch
from app.schemas.batch import BatchCreate, BatchResponse
from app.services.batch_service import update_batch_stage
from app.core.dependencies import worker_access, manager_only
from app.models.user import User
from typing import List

router = APIRouter()

@router.get("/", response_model=List[BatchResponse])
def get_batches(db: Session = Depends(get_db), current_user: User = Depends(worker_access)):
    # Filter by current user's organization
    if current_user.current_organization_id:
        return db.query(Batch).filter(
            Batch.organization_id == current_user.current_organization_id
        ).all()
    return db.query(Batch).all()

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: int, db: Session = Depends(get_db), current_user: User = Depends(worker_access)):
    organization_id = current_user.current_organization_id or 1
    batch = db.query(Batch).filter(
        Batch.id == batch_id,
        Batch.organization_id == organization_id
    ).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

@router.post("/", response_model=BatchResponse)
def create_batch(
    batch_in: BatchCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only)
):
    if not batch_in.batch_number or len(batch_in.batch_number) < 3:
        from app.core.exceptions import BadRequestException
        raise BadRequestException("Batch number must be at least 3 characters")
    
    batch = Batch(**batch_in.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch

@router.patch("/{batch_id}/stage")
def update_stage(
    batch_id: int, 
    stage: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access)
):
    try:
        organization_id = current_user.current_organization_id or 1
        batch = update_batch_stage(db, batch_id, stage, organization_id)
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        return {"message": f"Stage updated to {stage}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))