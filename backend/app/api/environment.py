from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.environment_log import EnvironmentLog
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class EnvironmentCreate(BaseModel):
    temperature: float
    humidity: float
    co2: float

@router.post("/rooms/{room_id}/environment")
def record_environment(room_id: int, env: EnvironmentCreate, db: Session = Depends(get_db)):
    log = EnvironmentLog(
        room_id=room_id,
        temperature=env.temperature,
        humidity=env.humidity,
        co2=env.co2,
        recorded_at=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    return {"message": "Environment recorded"}

@router.get("/rooms/{room_id}/environment/history")
def get_environment_history(room_id: int, db: Session = Depends(get_db)):
    logs = db.query(EnvironmentLog).filter(EnvironmentLog.room_id == room_id).order_by(EnvironmentLog.recorded_at.desc()).limit(50).all()
    return [
        {
            "recorded_at": log.recorded_at,
            "temperature": log.temperature,
            "humidity": log.humidity,
            "co2": log.co2
        } for log in logs
    ]