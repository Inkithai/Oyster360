from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class ImageInspection(Base):
    __tablename__ = "image_inspections"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    image_url = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime)
    ai_status = Column(String, default="pending")  # pending, completed, failed
    overall_health_score = Column(Float)
    contamination_probability = Column(Float)
    detected_stage = Column(String)
    notes = Column(String)

    findings = relationship("InspectionFinding", back_populates="inspection")


class InspectionFinding(Base):
    __tablename__ = "inspection_findings"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("image_inspections.id"))
    category = Column(String)           # contamination, growth_stage, moisture, etc.
    severity = Column(String)           # low, medium, high
    confidence = Column(Float)
    recommendation = Column(String)

    inspection = relationship("ImageInspection", back_populates="findings")