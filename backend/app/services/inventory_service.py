from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem, InventoryTransaction, TransactionType


class InventoryService:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _items(self):
        return self.db.query(InventoryItem).filter(
            InventoryItem.organization_id == self.organization_id
        )

    def get_all_items(self) -> List[InventoryItem]:
        return self._items().all()

    def create_item(
        self,
        name: str,
        category: str,
        unit: str,
        reorder_level: float,
    ) -> InventoryItem:
        item = InventoryItem(
            name=name,
            category=category,
            unit=unit,
            reorder_level=reorder_level,
            current_stock=0,
            organization_id=self.organization_id,
            created_at=datetime.utcnow(),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def record_transaction(
        self,
        item_id: int,
        transaction_type: TransactionType,
        quantity: float,
        notes: str,
        user_id: int,
    ) -> InventoryTransaction:
        item = self._items().filter(InventoryItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero")
        if transaction_type == TransactionType.OUT and item.current_stock < quantity:
            raise HTTPException(status_code=400, detail="Insufficient inventory stock")

        if transaction_type == TransactionType.OUT:
            item.current_stock -= quantity
        elif transaction_type == TransactionType.IN:
            item.current_stock += quantity
        else:
            item.current_stock = quantity

        transaction = InventoryTransaction(
            item_id=item_id,
            transaction_type=transaction_type,
            quantity=quantity,
            notes=notes,
            performed_by=user_id,
            created_at=datetime.utcnow(),
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_low_stock_items(self) -> List[InventoryItem]:
        return self._items().filter(
            InventoryItem.current_stock <= InventoryItem.reorder_level
        ).all()
