from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.image_service import ImageService
from app.services.vision_service import VisionService
from app.core.dependencies import worker_access
from app.models.user import User
from pydantic import BaseModel
from typing import List

router = APIRouter()

class InspectionCreate(BaseModel):
    batch_id: int
    room_id: int
    image_url: str

@router.post("/upload")
def upload_image(
    data: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access)
):
    service = ImageService(db)
    inspection = service.create_inspection(
        batch_id=data.batch_id,
        room_id=data.room_id,
        image_url=data.image_url,
        user_id=current_user.id
    )
    return {"inspection_id": inspection.id, "status": "pending"}

@router.post("/{inspection_id}/analyze")
def analyze_image(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access)
):
    vision = VisionService(db)
    result = vision.analyze_image(inspection_id, "")
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/batches/{batch_id}/history")
def get_batch_inspections(batch_id: int, db: Session = Depends(get_db)):
    service = ImageService(db)
    return service.get_batch_inspections(batch_id)

@router.get("/batches/{batch_id}/history")
def get_batch_inspections(batch_id: int, db: Session = Depends(get_db)):
    service = ImageService(db)
    return service.get_batch_inspections(batch_id)