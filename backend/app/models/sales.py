"""Buyer and Harvest Sale models for Sri Lankan mushroom-farm sales tracking."""
from datetime import datetime
import enum
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class BuyerType(str, enum.Enum):
    RETAILER = "RETAILER"
    RESTAURANT = "RESTAURANT"
    WHOLESALER = "WHOLESALER"
    DIRECT_CUSTOMER = "DIRECT_CUSTOMER"
    HOTEL = "HOTEL"
    INTERMEDIARY = "INTERMEDIARY"


class PaymentStatus(str, enum.Enum):
    PAID = "PAID"
    PARTIAL = "PARTIAL"
    UNPAID = "UNPAID"


class Buyer(Base):
    __tablename__ = "buyers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id"), index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    buyer_type: Mapped[BuyerType] = mapped_column(
        Enum(BuyerType), default=BuyerType.RETAILER
    )
    phone: Mapped[str] = mapped_column(String, default="")
    location: Mapped[str] = mapped_column(String, default="")
    notes: Mapped[str] = mapped_column(String, default="")

    sales: Mapped[list["HarvestSale"]] = relationship(
        "HarvestSale", back_populates="buyer"
    )


class HarvestSale(Base):
    __tablename__ = "harvest_sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id"), index=True
    )
    buyer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("buyers.id"), index=True
    )
    batch_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("batches.id"), nullable=True
    )
    harvest_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("harvests.id"), nullable=True
    )
    quantity_kg: Mapped[float] = mapped_column(Float, default=0.0)
    price_per_kg_lkr: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount_lkr: Mapped[float] = mapped_column(Float, default=0.0)
    amount_paid_lkr: Mapped[float] = mapped_column(Float, default=0.0)
    balance_due_lkr: Mapped[float] = mapped_column(Float, default=0.0)
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.PAID
    )
    sale_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    notes: Mapped[str] = mapped_column(String, default="")
    recorded_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    buyer: Mapped["Buyer"] = relationship("Buyer", back_populates="sales")
