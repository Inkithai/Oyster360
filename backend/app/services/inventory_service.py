from sqlalchemy.orm import Session
from app.models.inventory import InventoryItem, InventoryTransaction, TransactionType
from app.models.purchase import Supplier
from datetime import datetime
from typing import List

class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_items(self) -> List[InventoryItem]:
        return self.db.query(InventoryItem).all()

    def create_item(self, name: str, category: str, unit: str, reorder_level: float) -> InventoryItem:
        item = InventoryItem(
            name=name,
            category=category,
            unit=unit,
            reorder_level=reorder_level,
            current_stock=0,
            created_at=datetime.utcnow()
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def record_transaction(self, item_id: int, transaction_type: str, quantity: float, notes: str, user_id: int):
        item = self.db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
        if not item:
            return None

        if transaction_type == "OUT":
            item.current_stock -= quantity
        else:
            item.current_stock += quantity

        transaction = InventoryTransaction(
            item_id=item_id,
            transaction_type=transaction_type,
            quantity=quantity,
            notes=notes,
            performed_by=user_id,
            created_at=datetime.utcnow()
        )
        self.db.add(transaction)
        self.db.commit()
        return transaction

    def get_low_stock_items(self) -> List[InventoryItem]:
        return self.db.query(InventoryItem).filter(
            InventoryItem.current_stock <= InventoryItem.reorder_level
        ).all()