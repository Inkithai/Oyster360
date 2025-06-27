from datetime import datetime
import secrets
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.purchase import (
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseOrderStatus,
    Supplier,
)


class PurchaseService:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def get_all_suppliers(self) -> List[Supplier]:
        return self.db.query(Supplier).filter(
            Supplier.organization_id == self.organization_id
        ).all()

    def create_supplier(
        self,
        name: str,
        contact: str,
        phone: str,
        email: str,
    ) -> Supplier:
        supplier = Supplier(
            organization_id=self.organization_id,
            name=name,
            contact_person=contact,
            phone=phone,
            email=email,
            created_at=datetime.utcnow(),
        )
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def create_purchase_order(
        self,
        supplier_id: int,
        items: list[dict],
        expected_date,
        user_id: int,
    ) -> PurchaseOrder:
        supplier = self.db.query(Supplier).filter(
            Supplier.id == supplier_id,
            Supplier.organization_id == self.organization_id,
        ).first()
        if supplier is None:
            raise HTTPException(status_code=404, detail="Supplier not found")

        order = PurchaseOrder(
            supplier_id=supplier_id,
            organization_id=self.organization_id,
            order_number=(
                f"PO-{datetime.utcnow():%Y%m%d%H%M%S}-"
                f"{secrets.token_hex(3).upper()}"
            ),
            status=PurchaseOrderStatus.PENDING,
            expected_date=expected_date,
            created_by=user_id,
            created_at=datetime.utcnow(),
        )
        self.db.add(order)
        self.db.flush()

        total = 0.0
        for item in items:
            self.db.add(
                PurchaseOrderItem(
                    purchase_order_id=order.id,
                    item_name=item["name"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                )
            )
            total += item["quantity"] * item["unit_price"]

        order.total_amount = total
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_all_orders(self) -> List[PurchaseOrder]:
        return self.db.query(PurchaseOrder).filter(
            PurchaseOrder.organization_id == self.organization_id
        ).order_by(PurchaseOrder.created_at.desc()).all()
