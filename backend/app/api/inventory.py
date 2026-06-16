from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import manager_only, worker_access
from app.core.tenant import get_current_organization
from app.database.database import get_db
from app.models.inventory import ItemCategory, TransactionType
from app.models.user import User
from app.services.inventory_service import InventoryService

router = APIRouter()


class ItemCreate(BaseModel):
    name: str
    category: ItemCategory
    unit: str
    reorder_level: float = Field(ge=0)


class TransactionCreate(BaseModel):
    item_id: int
    transaction_type: TransactionType
    quantity: float = Field(gt=0)
    notes: str = ""


@router.get("/items")
def get_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    return InventoryService(db, organization_id).get_all_items()


@router.post("/items")
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return InventoryService(db, organization_id).create_item(
        data.name,
        data.category.value,
        data.unit,
        data.reorder_level,
    )


@router.post("/transactions")
def record_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
):
    return InventoryService(db, organization_id).record_transaction(
        item_id=data.item_id,
        transaction_type=data.transaction_type,
        quantity=data.quantity,
        notes=data.notes,
        user_id=current_user.id,
    )


@router.get("/low-stock")
def get_low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
):
    return InventoryService(db, organization_id).get_low_stock_items()
