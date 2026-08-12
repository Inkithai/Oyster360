from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.room import Room
from app.core.dependencies import worker_access
from app.models.user import User
from typing import List

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_rooms(db: Session = Depends(get_db), current_user: User = Depends(worker_access)):
    rooms = db.query(Room).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "capacity": r.capacity,
            "temperature_target": r.temperature_target,
            "humidity_target": r.humidity_target
        } for r in rooms
    ]