from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import worker_access
from app.core.tenant import get_current_organization
from app.core.tenant_enforcer import TenantEnforcer
from app.database.database import get_db
from app.models.batch import Batch
from app.models.image_inspection import ImageInspection
from app.models.room import Room
from app.models.user import User
from app.services.image_service import ImageService
from app.services.vision_service import VisionService

router = APIRouter()


class InspectionCreate(BaseModel):
    batch_id: int
    room_id: int
    image_url: str


def _tenant_inspection(
    db: Session,
    inspection_id: int,
    organization_id: int,
) -> ImageInspection:
    inspection = db.query(ImageInspection).join(
        Batch,
        Batch.id == ImageInspection.batch_id,
    ).filter(
        ImageInspection.id == inspection_id,
        Batch.organization_id == organization_id,
    ).first()
    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection


@router.post("/upload")
def upload_image(
    data: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    enforcer = TenantEnforcer(db, organization_id)
    batch = enforcer.safe_get(Batch, data.batch_id)
    room = enforcer.safe_get(Room, data.room_id)
    if batch.room_id != room.id:
        raise HTTPException(status_code=400, detail="Room does not match the batch")

    inspection = ImageService(db).create_inspection(
        batch_id=data.batch_id,
        room_id=data.room_id,
        image_url=data.image_url,
        user_id=current_user.id,
    )
    return {"inspection_id": inspection.id, "status": "pending"}


@router.post("/{inspection_id}/analyze")
def analyze_image(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    inspection = _tenant_inspection(db, inspection_id, organization_id)
    result = VisionService(db).analyze_image(inspection.id, inspection.image_url)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/batches/{batch_id}/history")
def get_batch_inspections(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    TenantEnforcer(db, organization_id).safe_get(Batch, batch_id)
    return ImageService(db).get_batch_inspections(batch_id)
