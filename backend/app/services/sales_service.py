"""Harvest Sales, Buyers, Payment Status & Sellable Stock service for Oyster360."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.batch import Batch
from app.models.harvest import Harvest
from app.models.sales import Buyer, BuyerType, HarvestSale, PaymentStatus


def _resolve_payment_status(total_lkr: float, paid_lkr: float) -> PaymentStatus:
    if paid_lkr <= 0:
        return PaymentStatus.UNPAID
    if paid_lkr + 0.01 >= total_lkr:
        return PaymentStatus.PAID
    return PaymentStatus.PARTIAL


class SalesService:
    def __init__(self, db: Session, organization_id: int) -> None:
        self.db = db
        self.organization_id = organization_id

    def create_buyer(
        self,
        name: str,
        buyer_type: BuyerType = BuyerType.RETAILER,
        phone: str = "",
        location: str = "",
        notes: str = "",
    ) -> Buyer:
        buyer = Buyer(
            organization_id=self.organization_id,
            name=name.strip(),
            buyer_type=buyer_type,
            phone=phone.strip(),
            location=location.strip(),
            notes=notes.strip(),
        )
        self.db.add(buyer)
        self.db.commit()
        self.db.refresh(buyer)
        return buyer

    def list_buyers(self) -> List[Dict[str, Any]]:
        buyers = (
            self.db.query(Buyer)
            .filter(Buyer.organization_id == self.organization_id)
            .order_by(Buyer.name.asc())
            .all()
        )
        sales = (
            self.db.query(HarvestSale)
            .filter(HarvestSale.organization_id == self.organization_id)
            .all()
        )
        result: List[Dict[str, Any]] = []
        for buyer in buyers:
            b_sales = [s for s in sales if s.buyer_id == buyer.id]
            result.append({
                "id": buyer.id,
                "name": buyer.name,
                "buyer_type": buyer.buyer_type.value,
                "phone": buyer.phone,
                "location": buyer.location,
                "notes": buyer.notes,
                "order_count": len(b_sales),
                "total_purchased_kg": round(
                    sum(float(s.quantity_kg or 0.0) for s in b_sales), 2
                ),
                "total_sales_lkr": round(
                    sum(float(s.total_amount_lkr or 0.0) for s in b_sales), 2
                ),
                "outstanding_balance_lkr": round(
                    sum(float(s.balance_due_lkr or 0.0) for s in b_sales), 2
                ),
            })
        return result

    def record_sale(
        self,
        buyer_id: int,
        quantity_kg: float,
        price_per_kg_lkr: float,
        amount_paid_lkr: Optional[float] = None,
        batch_id: Optional[int] = None,
        harvest_id: Optional[int] = None,
        notes: str = "",
        user_id: Optional[int] = None,
    ) -> HarvestSale:
        buyer = (
            self.db.query(Buyer)
            .filter(
                Buyer.id == buyer_id,
                Buyer.organization_id == self.organization_id,
            )
            .first()
        )
        if buyer is None:
            raise HTTPException(status_code=404, detail="Buyer not found")

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

        total_lkr = round(float(quantity_kg) * float(price_per_kg_lkr), 2)
        paid_lkr = (
            total_lkr
            if amount_paid_lkr is None
            else round(float(amount_paid_lkr), 2)
        )
        if paid_lkr < 0 or paid_lkr > total_lkr:
            raise HTTPException(
                status_code=400,
                detail="Amount paid must be between 0 and the total sale amount",
            )
        balance_lkr = round(max(0.0, total_lkr - paid_lkr), 2)
        status = _resolve_payment_status(total_lkr, paid_lkr)

        sale = HarvestSale(
            organization_id=self.organization_id,
            buyer_id=buyer_id,
            batch_id=batch_id,
            harvest_id=harvest_id,
            quantity_kg=round(float(quantity_kg), 2),
            price_per_kg_lkr=round(float(price_per_kg_lkr), 2),
            total_amount_lkr=total_lkr,
            amount_paid_lkr=paid_lkr,
            balance_due_lkr=balance_lkr,
            payment_status=status,
            sale_date=datetime.utcnow(),
            notes=notes,
            recorded_by=user_id,
        )
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def record_payment(self, sale_id: int, payment_amount_lkr: float) -> HarvestSale:
        sale = (
            self.db.query(HarvestSale)
            .filter(
                HarvestSale.id == sale_id,
                HarvestSale.organization_id == self.organization_id,
            )
            .first()
        )
        if sale is None:
            raise HTTPException(status_code=404, detail="Sale order not found")
        if payment_amount_lkr <= 0:
            raise HTTPException(
                status_code=400, detail="Payment amount must be greater than zero"
            )
        new_paid = round(float(sale.amount_paid_lkr) + float(payment_amount_lkr), 2)
        if new_paid > float(sale.total_amount_lkr) + 0.01:
            raise HTTPException(
                status_code=400,
                detail="Payment exceeds outstanding balance due",
            )
        sale.amount_paid_lkr = min(float(sale.total_amount_lkr), new_paid)
        sale.balance_due_lkr = round(
            max(0.0, float(sale.total_amount_lkr) - sale.amount_paid_lkr), 2
        )
        sale.payment_status = _resolve_payment_status(
            float(sale.total_amount_lkr), sale.amount_paid_lkr
        )
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def list_sales(self, buyer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        query = (
            self.db.query(HarvestSale, Buyer.name, Buyer.buyer_type)
            .join(Buyer, HarvestSale.buyer_id == Buyer.id)
            .filter(HarvestSale.organization_id == self.organization_id)
        )
        if buyer_id is not None:
            buyer = (
                self.db.query(Buyer)
                .filter(
                    Buyer.id == buyer_id,
                    Buyer.organization_id == self.organization_id,
                )
                .first()
            )
            if buyer is None:
                raise HTTPException(status_code=404, detail="Buyer not found")
            query = query.filter(HarvestSale.buyer_id == buyer_id)

        rows = query.order_by(HarvestSale.sale_date.desc()).all()
        return [
            {
                "id": sale.id,
                "buyer_id": sale.buyer_id,
                "buyer_name": buyer_name,
                "buyer_type": buyer_type.value,
                "batch_id": sale.batch_id,
                "harvest_id": sale.harvest_id,
                "quantity_kg": sale.quantity_kg,
                "price_per_kg_lkr": sale.price_per_kg_lkr,
                "total_amount_lkr": sale.total_amount_lkr,
                "amount_paid_lkr": sale.amount_paid_lkr,
                "balance_due_lkr": sale.balance_due_lkr,
                "payment_status": sale.payment_status.value,
                "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
                "notes": sale.notes,
            }
            for sale, buyer_name, buyer_type in rows
        ]

    def get_stock_summary(self) -> Dict[str, Any]:
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

        total_harvested_kg = round(
            sum(float(h.quantity_kg or 0.0) for h in harvests), 2
        )
        total_spoiled_kg = round(
            sum(float(h.spoiled_kg or 0.0) for h in harvests), 2
        )
        total_unsold_logged_kg = round(
            sum(float(h.unsold_kg or 0.0) for h in harvests), 2
        )
        total_sold_kg = round(
            sum(float(s.quantity_kg or 0.0) for s in sales), 2
        )
        available_for_sale_kg = round(
            max(0.0, total_harvested_kg - total_spoiled_kg - total_sold_kg), 2
        )
        total_sales_lkr = round(
            sum(float(s.total_amount_lkr or 0.0) for s in sales), 2
        )
        outstanding_balance_lkr = round(
            sum(float(s.balance_due_lkr or 0.0) for s in sales), 2
        )

        return {
            "total_harvested_kg": total_harvested_kg,
            "total_spoiled_kg": total_spoiled_kg,
            "total_unsold_logged_kg": total_unsold_logged_kg,
            "total_sold_kg": total_sold_kg,
            "available_for_sale_kg": available_for_sale_kg,
            "total_sales_lkr": total_sales_lkr,
            "outstanding_balance_lkr": outstanding_balance_lkr,
        }
