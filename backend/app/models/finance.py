"""LKR Farm Expense model for Sri Lankan mushroom-farm cost & profit tracking."""
from datetime import datetime
import enum
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ExpenseCategory(str, enum.Enum):
    SUBSTRATE = "SUBSTRATE"
    SPAWN = "SPAWN"
    BAGS = "BAGS"
    PACKAGING = "PACKAGING"
    ELECTRICITY = "ELECTRICITY"
    WATER = "WATER"
    LABOUR = "LABOUR"
    TRANSPORT = "TRANSPORT"
    OTHER = "OTHER"


class FarmExpense(Base):
    __tablename__ = "farm_expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id"), index=True
    )
    batch_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("batches.id"), nullable=True, index=True
    )
    category: Mapped[ExpenseCategory] = mapped_column(
        Enum(ExpenseCategory), default=ExpenseCategory.SUBSTRATE
    )
    description: Mapped[str] = mapped_column(String, default="")
    amount_lkr: Mapped[float] = mapped_column(Float, default=0.0)
    expense_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    recorded_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
