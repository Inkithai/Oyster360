from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.harvest_grade_service import HarvestGradeService
from app.core.dependencies import worker_access, manager_only
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class GradeCreate(BaseModel):
    harvest_id: int
    batch_id: int
    grade: str
    quantity_kg: float
    price_per_kg: float
    notes: str = ""

@router.post("/")
def record_harvest_grade(
    data: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only)
):
    service = HarvestGradeService(db)
    return service.record_grade(
        harvest_id=data.harvest_id,
        batch_id=data.batch_id,
        grade=data.grade,
        quantity_kg=data.quantity_kg,
        price_per_kg=data.price_per_kg,
        notes=data.notes,
        user_id=current_user.id
    )

@router.get("/batches/{batch_id}")
def get_grades_by_batch(batch_id: int, db: Session = Depends(get_db)):
    service = HarvestGradeService(db)
    return service.get_grades_by_batch(batch_id)