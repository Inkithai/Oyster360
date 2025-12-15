from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class GrowthLog(Base):
    __tablename__ = "growth_logs"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    stage = Column(String)
    notes = Column(String)
    image_url = Column(String)
    health_score = Column(Float)
    created_at = Column(DateTime)