"""Sri Lankan LKR Cost & Profit Calculator service for Oyster360."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.batch import Batch
from app.models.finance import ExpenseCategory, FarmExpense
from app.models.harvest import Harvest
from app.models.sales import HarvestSale

EXPECTED_YIELD_KG_PER_BAG = 0.35  # 350g per bag across flushes (Sri Lanka DOA standard)


class FinanceService:
    def __init__(self, db: Session, organization_id: int) -> None:
        self.db = db
        self.organization_id = organization_id

    def record_expense(
        self,
        category: ExpenseCategory,
        amount_lkr: float,
        description: str = "",
        batch_id: Optional[int] = None,
        expense_date: Optional[datetime] = None,
        user_id: Optional[int] = None,
    ) -> FarmExpense:
        if amount_lkr <= 0:
            raise HTTPException(
                status_code=400, detail="Expense amount must be greater than zero"
            )
        if batch_id is not None:
            batch = (
                self.db.query(Batch)
                .filter(
                    Batch.id == batch_id,
                    Batch.organization_id == self.organization_id,
                )
                .first()
            )
            if batch is None:
                raise HTTPException(status_code=404, detail="Batch not found")

        expense = FarmExpense(
            organization_id=self.organization_id,
            batch_id=batch_id,
            category=category,
            description=description,
            amount_lkr=round(float(amount_lkr), 2),
            expense_date=expense_date or datetime.utcnow(),
            recorded_by=user_id,
        )
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def list_expenses(self, batch_id: Optional[int] = None) -> List[Dict[str, Any]]:
        query = self.db.query(FarmExpense).filter(
            FarmExpense.organization_id == self.organization_id
        )
        if batch_id is not None:
            query = query.filter(FarmExpense.batch_id == batch_id)
        rows = query.order_by(FarmExpense.expense_date.desc()).all()
        return [
            {
                "id": row.id,
                "batch_id": row.batch_id,
                "category": row.category.value,
                "description": row.description,
                "amount_lkr": round(float(row.amount_lkr), 2),
                "expense_date": (
                    row.expense_date.isoformat() if row.expense_date else None
                ),
            }
            for row in rows
        ]

    def get_profitability_summary(self) -> Dict[str, Any]:
        batches = (
            self.db.query(Batch)
            .filter(Batch.organization_id == self.organization_id)
            .all()
        )
        expenses = (
            self.db.query(FarmExpense)
            .filter(FarmExpense.organization_id == self.organization_id)
            .all()
        )
        harvests = (
            self.db.query(Harvest)
            .filter(Harvest.organization_id == self.organization_id)
            .all()
        )
        sales = (
            self.db.query(HarvestSale)
            .filter(HarvestSale.organization_id == self.organization_id)
            .all()
        )

        total_expenses_lkr = round(
            sum(float(e.amount_lkr or 0.0) for e in expenses), 2
        )
        expense_by_category: Dict[str, float] = {}
        for exp in expenses:
            cat = exp.category.value
            expense_by_category[cat] = round(
                expense_by_category.get(cat, 0.0) + float(exp.amount_lkr or 0.0), 2
            )

        total_bags = sum(int(b.bags_prepared or 500) for b in batches)
        total_contaminated = sum(int(b.bags_contaminated or 0) for b in batches)
        healthy_bags = max(0, total_bags - total_contaminated)

        total_harvested_kg = round(
            sum(float(h.quantity_kg or 0.0) for h in harvests), 2
        )
        total_spoiled_kg = round(
            sum(float(h.spoiled_kg or 0.0) for h in harvests), 2
        )
        sellable_harvest_kg = round(
            max(0.0, total_harvested_kg - total_spoiled_kg), 2
        )
        expected_yield_kg = round(healthy_bags * EXPECTED_YIELD_KG_PER_BAG, 2)
        yield_efficiency_pct = (
            round((total_harvested_kg / expected_yield_kg) * 100.0, 1)
            if expected_yield_kg > 0
            else 0.0
        )

        harvest_revenue_lkr = round(
            sum(
                max(0.0, float(h.quantity_kg or 0.0) - float(h.spoiled_kg or 0.0))
                * float(h.selling_price or 0.0)
                for h in harvests
            ),
            2,
        )
        sales_revenue_lkr = round(
            sum(float(s.total_amount_lkr or 0.0) for s in sales), 2
        )
        collected_revenue_lkr = round(
            sum(float(s.amount_paid_lkr or 0.0) for s in sales), 2
        )
        outstanding_receivables_lkr = round(
            sum(float(s.balance_due_lkr or 0.0) for s in sales), 2
        )

        effective_revenue_lkr = (
            sales_revenue_lkr if sales_revenue_lkr > 0 else harvest_revenue_lkr
        )
        direct_categories = {"SUBSTRATE", "SPAWN", "BAGS", "PACKAGING"}
        direct_costs_lkr = round(
            sum(
                amt
                for cat, amt in expense_by_category.items()
                if cat in direct_categories
            ),
            2,
        )
        gross_profit_lkr = round(effective_revenue_lkr - direct_costs_lkr, 2)
        estimated_net_profit_lkr = round(
            effective_revenue_lkr - total_expenses_lkr, 2
        )

        cost_per_bag_lkr = (
            round(total_expenses_lkr / total_bags, 2) if total_bags > 0 else 0.0
        )
        cost_per_kg_lkr = (
            round(total_expenses_lkr / total_harvested_kg, 2)
            if total_harvested_kg > 0
            else 0.0
        )
        profit_per_kg_lkr = (
            round(estimated_net_profit_lkr / total_harvested_kg, 2)
            if total_harvested_kg > 0
            else 0.0
        )
        profit_margin_pct = (
            round((estimated_net_profit_lkr / effective_revenue_lkr) * 100.0, 1)
            if effective_revenue_lkr > 0
            else 0.0
        )

        unassigned_expenses = sum(
            float(e.amount_lkr or 0.0) for e in expenses if e.batch_id is None
        )
        shared_per_batch = (
            unassigned_expenses / len(batches) if batches else 0.0
        )

        batch_profitability: List[Dict[str, Any]] = []
        for batch in batches:
            b_prepared = int(batch.bags_prepared or 500)
            b_contam = int(batch.bags_contaminated or 0)
            b_healthy = max(0, b_prepared - b_contam)
            b_expected_kg = round(b_healthy * EXPECTED_YIELD_KG_PER_BAG, 2)

            b_harvests = [h for h in harvests if h.batch_id == batch.id]
            b_actual_kg = round(
                sum(float(h.quantity_kg or 0.0) for h in b_harvests), 2
            )
            b_harvest_rev = round(
                sum(
                    max(0.0, float(h.quantity_kg or 0.0) - float(h.spoiled_kg or 0.0))
                    * float(h.selling_price or 0.0)
                    for h in b_harvests
                ),
                2,
            )
            b_sales = [s for s in sales if s.batch_id == batch.id]
            b_sales_rev = round(
                sum(float(s.total_amount_lkr or 0.0) for s in b_sales), 2
            )
            b_rev = b_sales_rev if b_sales_rev > 0 else b_harvest_rev

            b_direct_exp = sum(
                float(e.amount_lkr or 0.0)
                for e in expenses
                if e.batch_id == batch.id
            )
            b_total_cost = round(b_direct_exp + shared_per_batch, 2)
            b_profit = round(b_rev - b_total_cost, 2)

            batch_profitability.append({
                "batch_id": batch.id,
                "batch_number": str(batch.batch_number),
                "stage": Batch.current_stage.type.python_type(batch.current_stage).value
                if batch.current_stage
                else "PREPARATION",
                "bags_prepared": b_prepared,
                "bags_contaminated": b_contam,
                "expected_yield_kg": b_expected_kg,
                "actual_yield_kg": b_actual_kg,
                "flushes_recorded": len(b_harvests),
                "total_cost_lkr": b_total_cost,
                "cost_per_bag_lkr": (
                    round(b_total_cost / b_prepared, 2) if b_prepared > 0 else 0.0
                ),
                "revenue_lkr": b_rev,
                "net_profit_lkr": b_profit,
                "profit_per_kg_lkr": (
                    round(b_profit / b_actual_kg, 2) if b_actual_kg > 0 else 0.0
                ),
            })

        return {
            "currency": "LKR",
            "total_expenses_lkr": total_expenses_lkr,
            "expense_by_category": expense_by_category,
            "total_bags_prepared": total_bags,
            "total_bags_contaminated": total_contaminated,
            "total_harvested_kg": total_harvested_kg,
            "sellable_harvest_kg": sellable_harvest_kg,
            "expected_yield_kg": expected_yield_kg,
            "yield_efficiency_pct": yield_efficiency_pct,
            "cost_per_bag_lkr": cost_per_bag_lkr,
            "cost_per_kg_lkr": cost_per_kg_lkr,
            "harvest_revenue_lkr": harvest_revenue_lkr,
            "sales_revenue_lkr": sales_revenue_lkr,
            "effective_revenue_lkr": effective_revenue_lkr,
            "collected_revenue_lkr": collected_revenue_lkr,
            "outstanding_receivables_lkr": outstanding_receivables_lkr,
            "gross_profit_lkr": gross_profit_lkr,
            "estimated_net_profit_lkr": estimated_net_profit_lkr,
            "profit_per_kg_lkr": profit_per_kg_lkr,
            "profit_margin_pct": profit_margin_pct,
            "batch_profitability": batch_profitability,
        }
