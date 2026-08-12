from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import manager_only, worker_access
from app.core.tenant import get_current_organization
from app.database.database import get_db
from app.models.user import User
from app.services.purchase_service import PurchaseService

router = APIRouter()


class SupplierCreate(BaseModel):
    name: str
    contact_person: str = ""
    phone: str = ""
    email: str = ""


class PurchaseItemCreate(BaseModel):
    name: str
    quantity: float = Field(gt=0)
    unit_price: float = Field(ge=0)


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    items: List[PurchaseItemCreate] = Field(min_length=1)
    expected_date: datetime


@router.get("/suppliers")
def get_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    return PurchaseService(db, organization_id).get_all_suppliers()


@router.post("/suppliers")
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return PurchaseService(db, organization_id).create_supplier(
        data.name,
        data.contact_person,
        data.phone,
        data.email,
    )


@router.get("/orders")
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return PurchaseService(db, organization_id).get_all_orders()


@router.post("/orders")
def create_order(
    data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return PurchaseService(db, organization_id).create_purchase_order(
        supplier_id=data.supplier_id,
        items=[item.model_dump() for item in data.items],
        expected_date=data.expected_date,
        user_id=current_user.id,
    )
