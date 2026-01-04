from sqlalchemy.orm import Session
from app.models.harvest_grade import HarvestGrade, GradeLevel
from datetime import datetime
from typing import List

class HarvestGradeService:
    def __init__(self, db: Session):
        self.db = db

    def record_grade(self, harvest_id: int, batch_id: int, grade: str, quantity_kg: float, price_per_kg: float, notes: str, user_id: int) -> HarvestGrade:
        grade_record = HarvestGrade(
            harvest_id=harvest_id,
            batch_id=batch_id,
            grade=grade,
            quantity_kg=quantity_kg,
            price_per_kg=price_per_kg,
            notes=notes,
            graded_by=user_id,
            created_at=datetime.utcnow()
        )
        self.db.add(grade_record)
        self.db.commit()
        self.db.refresh(grade_record)
        return grade_record

    def get_grades_by_batch(self, batch_id: int) -> List[HarvestGrade]:
        return self.db.query(HarvestGrade).filter(HarvestGrade.batch_id == batch_id).all()