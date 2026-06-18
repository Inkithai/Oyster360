from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import worker_access
from app.core.tenant import get_current_organization
from app.database.database import get_db
from app.models.room import Room
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[dict])
def get_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    rooms = db.query(Room).filter(Room.organization_id == organization_id).all()
    return [
        {
            "id": room.id,
            "name": room.name,
            "capacity": room.capacity,
            "temperature_target": room.temperature_target,
            "humidity_target": room.humidity_target,
        }
        for room in rooms
    ]
