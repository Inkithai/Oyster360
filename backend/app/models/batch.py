from datetime import datetime
import enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    current_stage: Column[BatchStage] = Column(
        Enum(BatchStage), default=BatchStage.PREPARATION
    )
    start_date = Column(DateTime)
    expected_harvest_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    bags_prepared: Mapped[int] = mapped_column(Integer, default=500)
    bags_inoculated: Mapped[int] = mapped_column(Integer, default=500)
    bags_contaminated: Mapped[int] = mapped_column(Integer, default=0)
    bags_harvested: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status = Column(String, default="active")
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    grow_bags = relationship("GrowBag", back_populates="batch")
