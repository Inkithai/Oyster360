from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base

class GrowBag(Base):
    __tablename__ = "grow_bags"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    barcode = Column(String, unique=True)
    status = Column(String, default="active")
    weight = Column(Float)

    batch = relationship("Batch", back_populates="grow_bags")