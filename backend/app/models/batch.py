from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base

class BatchStage(str, enum.Enum):
    PREPARATION = "PREPARATION"
    INOCULATION = "INOCULATION"
    COLONIZATION = "COLONIZATION"
    FRUITING = "FRUITING"
    HARVEST = "HARVEST"
    COMPLETED = "COMPLETED"

class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String, unique=True, nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    strain_id = Column(Integer, ForeignKey("strains.id"))
    recipe_version_id = Column(Integer, ForeignKey("recipe_versions.id"))
    current_stage = Column(Enum(BatchStage), default=BatchStage.PREPARATION)
    start_date = Column(DateTime)
    status = Column(String, default="active")
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    grow_bags = relationship("GrowBag", back_populates="batch")