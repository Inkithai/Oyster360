from sqlalchemy import Column, Integer, String, JSON, Float, ForeignKey, DateTime
from .base import Base

class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    type = Column(String)  # contamination, yield, stage_prediction
    input_data = Column(JSON)
    recommendation = Column(String)
    confidence_score = Column(Float)
    created_at = Column(DateTime)