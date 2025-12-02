"""
Oyster360 Production Billing Service
"""
from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from app.models.organization import Organization
from datetime import datetime
from typing import Optional

class BillingService:
    def __init__(self, db: Session):
        self.db = db

    def create_subscription(
        self, 
        organization_id: int, 
        stripe_customer_id: str,
        stripe_subscription_id: str,
        plan: str,
        status: str = "trialing"
    ) -> Subscription:
        subscription = Subscription(
            organization_id=organization_id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            plan=plan,
            status=status,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            created_at=datetime.utcnow()
        )
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def update_subscription_status(self, stripe_subscription_id: str, status: str):
        sub = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        if sub:
            sub.status = status
            self.db.commit()
        return sub

    def get_active_subscription(self, organization_id: int) -> Optional[Subscription]:
        return self.db.query(Subscription).filter(
            Subscription.organization_id == organization_id,
            Subscription.status.in_(["active", "trialing"])
        ).first()