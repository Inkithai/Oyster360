from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.growth_log import GrowthLog
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class GrowthLogCreate(BaseModel):
    stage: str
    notes: str
    health_score: float
    image_url: str | None = None

@router.post("/batches/{batch_id}/growth-logs")
def create_growth_log(batch_id: int, log: GrowthLogCreate, db: Session = Depends(get_db)):
    growth_log = GrowthLog(
        batch_id=batch_id,
        stage=log.stage,
        notes=log.notes,
        health_score=log.health_score,
        image_url=log.image_url,
        created_at=datetime.utcnow()
    )
    db.add(growth_log)
    db.commit()
    return {"message": "Growth log recorded"}

@router.get("/batches/{batch_id}/timeline")
def get_batch_timeline(batch_id: int, db: Session = Depends(get_db)):
    logs = db.query(GrowthLog).filter(GrowthLog.batch_id == batch_id).order_by(GrowthLog.created_at).all()
    return [
        {
            "date": log.created_at.strftime("%Y-%m-%d"),
            "stage": log.stage,
            "health_score": log.health_score,
            "notes": log.notes
        } for log in logs
    ]