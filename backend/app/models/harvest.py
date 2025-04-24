from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from .base import Base

class Harvest(Base):
    __tablename__ = "harvests"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    quantity_kg = Column(Float)
    quality_score = Column(Float)
    harvest_date = Column(DateTime)
    selling_price = Column(Float)