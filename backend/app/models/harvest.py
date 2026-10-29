from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Harvest(Base):
    __tablename__ = "harvests"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    flush_number: Mapped[int] = mapped_column(Integer, default=1)
    quantity_kg = Column(Float)
    unsold_kg: Mapped[float] = mapped_column(Float, default=0.0)
    spoiled_kg: Mapped[float] = mapped_column(Float, default=0.0)
    quality_score = Column(Float)
    harvest_date = Column(DateTime)
    selling_price = Column(Float)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
