from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.harvest import Harvest
from app.models.batch import Batch
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class HarvestCreate(BaseModel):
    quantity_kg: float
    quality_score: float
    selling_price: float

@router.post("/batches/{batch_id}/harvest")
def record_harvest(batch_id: int, harvest_in: HarvestCreate, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    harvest = Harvest(
        batch_id=batch_id,
        quantity_kg=harvest_in.quantity_kg,
        quality_score=harvest_in.quality_score,
        harvest_date=datetime.utcnow(),
        selling_price=harvest_in.selling_price
    )
    db.add(harvest)
    batch.current_stage = "COMPLETED"
    db.commit()
    
    return {
        "message": "Harvest recorded",
        "total_yield_kg": harvest_in.quantity_kg,
        "revenue": harvest_in.quantity_kg * harvest_in.selling_price
    }