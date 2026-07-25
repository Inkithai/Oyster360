from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.inventory_service import InventoryService
from app.core.dependencies import manager_only, worker_access
from app.models.user import User
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ItemCreate(BaseModel):
    name: str
    category: str
    unit: str
    reorder_level: float

class TransactionCreate(BaseModel):
    item_id: int
    transaction_type: str
    quantity: float
    notes: str = ""

@router.get("/items")
def get_items(db: Session = Depends(get_db), current_user: User = Depends(worker_access)):
    service = InventoryService(db)
    return service.get_all_items()

@router.post("/items")
def create_item(data: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(manager_only)):
    service = InventoryService(db)
    return service.create_item(data.name, data.category, data.unit, data.reorder_level)

@router.post("/transactions")
def record_transaction(
    data: TransactionCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(worker_access)
):
    service = InventoryService(db)
    return service.record_transaction(
        item_id=data.item_id,
        transaction_type=data.transaction_type,
        quantity=data.quantity,
        notes=data.notes,
        user_id=current_user.id
    )

@router.get("/low-stock")
def get_low_stock(db: Session = Depends(get_db), current_user: User = Depends(manager_only)):
    service = InventoryService(db)
    return service.get_low_stock_items()