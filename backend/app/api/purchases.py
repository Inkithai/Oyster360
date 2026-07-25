from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.purchase_service import PurchaseService
from app.core.dependencies import manager_only, worker_access
from app.models.user import User
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class SupplierCreate(BaseModel):
    name: str
    contact_person: str = ""
    phone: str = ""
    email: str = ""

class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    items: List[dict]
    expected_date: datetime

@router.get("/suppliers")
def get_suppliers(db: Session = Depends(get_db), current_user: User = Depends(worker_access)):
    service = PurchaseService(db)
    return service.get_all_suppliers()

@router.post("/suppliers")
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db), current_user: User = Depends(manager_only)):
    service = PurchaseService(db)
    return service.create_supplier(data.name, data.contact_person, data.phone, data.email)

@router.get("/orders")
def get_orders(db: Session = Depends(get_db), current_user: User = Depends(manager_only)):
    service = PurchaseService(db)
    return service.get_all_orders()

@router.post("/orders")
def create_order(
    data: PurchaseOrderCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(manager_only)
):
    service = PurchaseService(db)
    return service.create_purchase_order(
        supplier_id=data.supplier_id,
        items=data.items,
        expected_date=data.expected_date,
        user_id=current_user.id
    )