from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
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
    quality_score: float = Field(default=90.0, ge=0, le=100)
    selling_price: float = Field(default=0.0, ge=0)
    flush_number: int = Field(default=1, ge=1, le=10)
    unsold_kg: float = Field(default=0.0, ge=0)
    spoiled_kg: float = Field(default=0.0, ge=0)
    notes: Optional[str] = None
    complete_batch: bool = True


def _serialize_harvest(harvest: Harvest, batch_number: Optional[str] = None) -> Dict[str, Any]:
    qty = float(harvest.quantity_kg or 0.0)
    spoiled = float(harvest.spoiled_kg or 0.0)
    unsold = float(harvest.unsold_kg or 0.0)
    sellable_kg = round(max(0.0, qty - spoiled), 2)
    price = float(harvest.selling_price or 0.0)
    return {
        "id": harvest.id,
        "batch_id": harvest.batch_id,
        "batch_number": batch_number or f"BATCH-{harvest.batch_id}",
        "flush_number": harvest.flush_number or 1,
        "quantity_kg": qty,
        "sellable_kg": sellable_kg,
        "unsold_kg": unsold,
        "spoiled_kg": spoiled,
        "quality_score": float(harvest.quality_score or 0.0),
        "selling_price": price,
        "revenue": round(sellable_kg * price, 2),
        "harvest_date": (
            harvest.harvest_date.isoformat() if harvest.harvest_date else None
        ),
        "notes": harvest.notes,
    }


@router.get("/harvests")
def list_harvests(
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> List[Dict[str, Any]]:
    rows = (
        db.query(Harvest, Batch.batch_number)
        .outerjoin(Batch, Harvest.batch_id == Batch.id)
        .filter(Harvest.organization_id == organization_id)
        .order_by(Harvest.harvest_date.desc())
        .all()
    )
    return [_serialize_harvest(harvest, batch_num) for harvest, batch_num in rows]


@router.get("/batches/{batch_id}/harvests")
def list_batch_harvests(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> List[Dict[str, Any]]:
    batch = TenantEnforcer(db, organization_id).safe_get(Batch, batch_id)
    harvests = (
        db.query(Harvest)
        .filter(
            Harvest.batch_id == batch_id,
            Harvest.organization_id == organization_id,
        )
        .order_by(Harvest.flush_number.asc(), Harvest.harvest_date.asc())
        .all()
    )
    return [_serialize_harvest(h, str(batch.batch_number)) for h in harvests]


@router.post("/batches/{batch_id}/harvest")
def record_harvest(
    batch_id: int,
    harvest_in: HarvestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    batch = TenantEnforcer(db, organization_id).safe_get(Batch, batch_id)
    if harvest_in.unsold_kg + harvest_in.spoiled_kg > harvest_in.quantity_kg:
        raise HTTPException(
            status_code=400,
            detail="Unsold and spoiled weight cannot exceed total harvested weight",
        )

    harvest = Harvest(
        batch_id=batch_id,
        organization_id=organization_id,
        flush_number=harvest_in.flush_number,
        quantity_kg=harvest_in.quantity_kg,
        unsold_kg=harvest_in.unsold_kg,
        spoiled_kg=harvest_in.spoiled_kg,
        quality_score=harvest_in.quality_score,
        harvest_date=datetime.utcnow(),
        selling_price=harvest_in.selling_price,
        notes=harvest_in.notes,
    )
    db.add(harvest)
    if harvest_in.complete_batch:
        batch.current_stage = BatchStage.COMPLETED
    else:
        batch.current_stage = BatchStage.HARVEST
    db.commit()
    db.refresh(harvest)

    sellable_kg = round(max(0.0, harvest_in.quantity_kg - harvest_in.spoiled_kg), 2)
    return {
        "id": harvest.id,
        "message": "Harvest recorded",
        "flush_number": harvest.flush_number,
        "total_yield_kg": harvest_in.quantity_kg,
        "sellable_kg": sellable_kg,
        "unsold_kg": harvest_in.unsold_kg,
        "spoiled_kg": harvest_in.spoiled_kg,
        "revenue": round(sellable_kg * harvest_in.selling_price, 2),
    }
