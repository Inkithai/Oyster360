"""Database synchronization for Stripe subscriptions."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.subscription import Subscription


class BillingService:
    def __init__(self, db: Session):
        self.db = db

    def create_subscription(
        self,
        organization_id: int,
        stripe_customer_id: str,
        stripe_subscription_id: str,
        plan: str,
        status: str = "trialing",
    ) -> Subscription:
        """Create or update a subscription idempotently.

        Stripe retries webhook events, so inserting a new row on every delivery
        would violate unique constraints and turn a successful retry into a 500.
        """
        subscription = self.db.query(Subscription).filter(
            (Subscription.stripe_subscription_id == stripe_subscription_id)
            | (Subscription.organization_id == organization_id)
        ).first()
        now = datetime.utcnow()

        if subscription is None:
            subscription = Subscription(
                organization_id=organization_id,
                created_at=now,
            )
            self.db.add(subscription)

        subscription.stripe_customer_id = stripe_customer_id
        subscription.stripe_subscription_id = stripe_subscription_id
        subscription.plan = plan
        subscription.status = status
        subscription.current_period_start = now
        subscription.current_period_end = now + timedelta(days=30)
        subscription.updated_at = now
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def sync_subscription(
        self,
        organization_id: int,
        stripe_customer_id: str,
        stripe_subscription_id: str,
        plan: str,
        status: str,
        current_period_start: datetime | None = None,
        current_period_end: datetime | None = None,
        cancel_at_period_end: bool = False,
    ) -> Subscription:
        subscription = self.create_subscription(
            organization_id=organization_id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            plan=plan,
            status=status,
        )
        if current_period_start is not None:
            subscription.current_period_start = current_period_start
        if current_period_end is not None:
            subscription.current_period_end = current_period_end
        subscription.cancel_at_period_end = cancel_at_period_end
        subscription.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def update_subscription_status(
        self,
        stripe_subscription_id: str,
        status: str,
    ) -> Optional[Subscription]:
        subscription = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        if subscription:
            subscription.status = status
            subscription.updated_at = datetime.utcnow()
            self.db.commit()
        return subscription

    def get_active_subscription(self, organization_id: int) -> Optional[Subscription]:
        return self.db.query(Subscription).filter(
            Subscription.organization_id == organization_id,
            Subscription.status.in_(["active", "trialing"]),
        ).first()
