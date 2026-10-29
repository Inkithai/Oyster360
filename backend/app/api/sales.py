"""API endpoints for Sri Lankan mushroom harvest sales and buyer management."""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import worker_access
from app.core.tenant import get_current_organization
from app.database.database import get_db
from app.models.sales import BuyerType
from app.models.user import User
from app.services.sales_service import SalesService

router = APIRouter()


class BuyerCreate(BaseModel):
    name: str = Field(min_length=2)
    buyer_type: BuyerType = BuyerType.RETAILER
    phone: str = ""
    location: str = ""
    notes: str = ""


class SaleCreate(BaseModel):
    buyer_id: int
    quantity_kg: float = Field(gt=0)
    price_per_kg_lkr: float = Field(ge=0)
    amount_paid_lkr: Optional[float] = Field(default=None, ge=0)
    batch_id: Optional[int] = None
    harvest_id: Optional[int] = None
    notes: str = ""


class PaymentUpdate(BaseModel):
    payment_amount_lkr: float = Field(gt=0)


@router.get("/buyers")
def list_buyers(
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> List[Dict[str, Any]]:
    return SalesService(db, organization_id).list_buyers()


@router.post("/buyers")
def create_buyer(
    data: BuyerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> Dict[str, Any]:
    buyer = SalesService(db, organization_id).create_buyer(
        name=data.name,
        buyer_type=data.buyer_type,
        phone=data.phone,
        location=data.location,
        notes=data.notes,
    )
    return {
        "id": buyer.id,
        "name": buyer.name,
        "buyer_type": buyer.buyer_type.value,
        "phone": buyer.phone,
        "location": buyer.location,
        "notes": buyer.notes,
    }


@router.get("/buyers/{buyer_id}/orders")
def get_buyer_orders(
    buyer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> List[Dict[str, Any]]:
    return SalesService(db, organization_id).list_sales(buyer_id=buyer_id)


@router.get("/orders")
def list_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> List[Dict[str, Any]]:
    return SalesService(db, organization_id).list_sales()


@router.post("/orders")
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> Dict[str, Any]:
    sale = SalesService(db, organization_id).record_sale(
        buyer_id=data.buyer_id,
        quantity_kg=data.quantity_kg,
        price_per_kg_lkr=data.price_per_kg_lkr,
        amount_paid_lkr=data.amount_paid_lkr,
        batch_id=data.batch_id,
        harvest_id=data.harvest_id,
        notes=data.notes,
        user_id=int(current_user.id),  # type: ignore[arg-type]
    )
    return {
        "id": sale.id,
        "buyer_id": sale.buyer_id,
        "batch_id": sale.batch_id,
        "quantity_kg": sale.quantity_kg,
        "price_per_kg_lkr": sale.price_per_kg_lkr,
        "total_amount_lkr": sale.total_amount_lkr,
        "amount_paid_lkr": sale.amount_paid_lkr,
        "balance_due_lkr": sale.balance_due_lkr,
        "payment_status": sale.payment_status.value,
    }


@router.patch("/orders/{sale_id}/payment")
def update_sale_payment(
    sale_id: int,
    data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> Dict[str, Any]:
    sale = SalesService(db, organization_id).record_payment(
        sale_id=sale_id,
        payment_amount_lkr=data.payment_amount_lkr,
    )
    return {
        "id": sale.id,
        "total_amount_lkr": sale.total_amount_lkr,
        "amount_paid_lkr": sale.amount_paid_lkr,
        "balance_due_lkr": sale.balance_due_lkr,
        "payment_status": sale.payment_status.value,
    }


@router.get("/stock-summary")
def get_stock_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> Dict[str, Any]:
    return SalesService(db, organization_id).get_stock_summary()
