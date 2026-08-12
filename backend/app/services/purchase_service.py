from sqlalchemy.orm import Session
from app.models.purchase import Supplier, PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus
from datetime import datetime
from typing import List

class PurchaseService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_suppliers(self) -> List[Supplier]:
        return self.db.query(Supplier).all()

    def create_supplier(self, name: str, contact: str, phone: str, email: str) -> Supplier:
        supplier = Supplier(
            name=name,
            contact_person=contact,
            phone=phone,
            email=email,
            created_at=datetime.utcnow()
        )
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def create_purchase_order(self, supplier_id: int, items: list, expected_date, user_id: int) -> PurchaseOrder:
        order = PurchaseOrder(
            supplier_id=supplier_id,
            order_number=f"PO-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            status=PurchaseOrderStatus.PENDING,
            expected_date=expected_date,
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        self.db.add(order)
        self.db.flush()

        total = 0
        for item in items:
            po_item = PurchaseOrderItem(
                purchase_order_id=order.id,
                item_name=item["name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"]
            )
            total += item["quantity"] * item["unit_price"]
            self.db.add(po_item)

        order.total_amount = total
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_all_orders(self) -> List[PurchaseOrder]:
        return self.db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).all()