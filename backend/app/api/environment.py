from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import worker_access
from app.core.tenant import get_current_organization
from app.core.tenant_enforcer import TenantEnforcer
from app.database.database import get_db
from app.models.environment_log import EnvironmentLog
from app.models.room import Room
from app.models.user import User

router = APIRouter()


class EnvironmentCreate(BaseModel):
    temperature: float
    humidity: float = Field(ge=0, le=100)
    co2: float = Field(ge=0)


@router.post("/rooms/{room_id}/environment")
def record_environment(
    room_id: int,
    env: EnvironmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    TenantEnforcer(db, organization_id).safe_get(Room, room_id)
    log = EnvironmentLog(
        room_id=room_id,
        organization_id=organization_id,
        temperature=env.temperature,
        humidity=env.humidity,
        co2=env.co2,
        recorded_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    return {"message": "Environment recorded"}


@router.get("/rooms/{room_id}/environment/history")
def get_environment_history(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    TenantEnforcer(db, organization_id).safe_get(Room, room_id)
    logs = db.query(EnvironmentLog).filter(
        EnvironmentLog.room_id == room_id,
        EnvironmentLog.organization_id == organization_id,
    ).order_by(EnvironmentLog.recorded_at.desc()).limit(50).all()
    return [
        {
            "recorded_at": log.recorded_at,
            "temperature": log.temperature,
            "humidity": log.humidity,
            "co2": log.co2,
        }
        for log in logs
    ]
