from sqlalchemy.orm import Session
from app.models.image_inspection import ImageInspection
from datetime import datetime
from typing import List

class ImageService:
    def __init__(self, db: Session):
        self.db = db

    def create_inspection(self, batch_id: int, room_id: int, image_url: str, user_id: int) -> ImageInspection:
        inspection = ImageInspection(
            batch_id=batch_id,
            room_id=room_id,
            image_url=image_url,
            uploaded_by=user_id,
            uploaded_at=datetime.utcnow(),
            ai_status="pending"
        )
        self.db.add(inspection)
        self.db.commit()
        self.db.refresh(inspection)
        return inspection

    def get_inspection(self, inspection_id: int) -> ImageInspection | None:
        return self.db.query(ImageInspection).filter(ImageInspection.id == inspection_id).first()

    def get_batch_inspections(self, batch_id: int) -> List[ImageInspection]:
        return self.db.query(ImageInspection).filter(ImageInspection.batch_id == batch_id).order_by(ImageInspection.uploaded_at.desc()).all()