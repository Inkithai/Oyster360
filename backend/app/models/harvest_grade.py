from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from .base import Base
import enum

class GradeLevel(str, enum.Enum):
    A = "A"      # Premium
    B = "B"      # Standard
    C = "C"      # Processing / Lower grade

class HarvestGrade(Base):
    __tablename__ = "harvest_grades"

    id = Column(Integer, primary_key=True, index=True)
    harvest_id = Column(Integer, ForeignKey("harvests.id"))
    batch_id = Column(Integer, ForeignKey("batches.id"))
    grade = Column(Enum(GradeLevel))
    quantity_kg = Column(Float)
    price_per_kg = Column(Float)
    notes = Column(String)
    graded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)

    harvest = relationship("Harvest")