"""API endpoints for Sri Lankan LKR farm expenses and profitability tracking."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import worker_access
from app.core.tenant import get_current_organization
from app.database.database import get_db
from app.models.finance import ExpenseCategory
from app.models.user import User
from app.services.finance_service import FinanceService

router = APIRouter()


class ExpenseCreate(BaseModel):
    category: ExpenseCategory
    amount_lkr: float = Field(gt=0)
    description: str = ""
    batch_id: Optional[int] = None
    expense_date: Optional[datetime] = None


@router.post("/expenses")
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> Dict[str, Any]:
    expense = FinanceService(db, organization_id).record_expense(
        category=data.category,
        amount_lkr=data.amount_lkr,
        description=data.description,
        batch_id=data.batch_id,
        expense_date=data.expense_date,
        user_id=int(current_user.id),  # type: ignore[arg-type]
    )
    return {
        "id": expense.id,
        "batch_id": expense.batch_id,
        "category": expense.category.value,
        "description": expense.description,
        "amount_lkr": expense.amount_lkr,
        "expense_date": expense.expense_date.isoformat(),
    }


@router.get("/expenses")
def list_expenses(
    batch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> List[Dict[str, Any]]:
    return FinanceService(db, organization_id).list_expenses(batch_id=batch_id)


@router.get("/profitability")
def get_profitability(
    db: Session = Depends(get_db),
    current_user: User = Depends(worker_access),
    organization_id: int = Depends(get_current_organization),
) -> Dict[str, Any]:
    return FinanceService(db, organization_id).get_profitability_summary()
