from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from .base import Base
import enum

class ItemCategory(str, enum.Enum):
    SPAWN = "SPAWN"
    SUBSTRATE = "SUBSTRATE"
    GROW_BAG = "GROW_BAG"
    PACKAGING = "PACKAGING"
    CLEANING = "CLEANING"
    OTHER = "OTHER"

class TransactionType(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category: Column[ItemCategory] = Column(Enum(ItemCategory), nullable=False)
    unit = Column(String, default="kg")  # kg, pcs, liters, etc.
    current_stock = Column(Float, default=0)
    reorder_level = Column(Float, default=0)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime)

    transactions = relationship("InventoryTransaction", back_populates="item")


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"))
    transaction_type: Column[TransactionType] = Column(Enum(TransactionType))
    quantity = Column(Float)
    notes = Column(String)
    performed_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)

    item = relationship("InventoryItem", back_populates="transactions")


# Supplier model is defined in purchase.py to avoid duplicate table definition