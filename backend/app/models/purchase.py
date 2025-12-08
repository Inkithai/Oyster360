from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from .base import Base
import enum

class PurchaseOrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    ORDERED = "ORDERED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"

class Supplier(Base):
    __tablename__ = "suppliers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    contact_person = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    created_at = Column(DateTime)

    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    order_number = Column(String, unique=True)
    status = Column(Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.PENDING)
    total_amount = Column(Float, default=0)
    expected_date = Column(DateTime)
    received_date = Column(DateTime)
    notes = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)

    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"))
    item_name = Column(String, nullable=False)
    quantity = Column(Float)
    unit_price = Column(Float)
    received_quantity = Column(Float, default=0)

    purchase_order = relationship("PurchaseOrder", back_populates="items")