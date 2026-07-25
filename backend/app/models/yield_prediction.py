from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from .base import Base

class YieldPrediction(Base):
    __tablename__ = "yield_predictions"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    predicted_yield_kg = Column(Float)
    confidence_score = Column(Float)
    expected_harvest_date = Column(DateTime)
    model_version = Column(String, default="v1-rule-based")
    created_at = Column(DateTime)