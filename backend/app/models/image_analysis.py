from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from .base import Base

class ImageAnalysis(Base):
    __tablename__ = "image_analyses"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    image_url = Column(String)
    stage = Column(String)
    health_score = Column(Float)
    contamination_risk = Column(String)
    issues = Column(JSON)
    recommendations = Column(JSON)
    created_at = Column(DateTime)