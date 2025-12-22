from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import manager_only
from app.core.tenant import get_current_organization
from app.database.database import get_db
from app.models.subscription import Subscription
from app.models.user import User
from app.services.stripe_service import StripeService

router = APIRouter()
stripe_service = StripeService()


class CreateCheckoutSession(BaseModel):
    plan: Literal["starter", "pro", "enterprise"]
    success_url: str
    cancel_url: str


class SubscriptionResponse(BaseModel):
    id: int
    plan: str
    status: str
    current_period_end: datetime
    cancel_at_period_end: bool

    model_config = {"from_attributes": True}


def _price_id_for_plan(plan: str) -> str:
    price_id = {
        "starter": settings.STRIPE_PRICE_STARTER,
        "pro": settings.STRIPE_PRICE_PRO,
        "enterprise": settings.STRIPE_PRICE_ENTERPRISE,
    }[plan]
    if not price_id:
        raise HTTPException(
            status_code=503,
            detail=f"Stripe price for the {plan} plan is not configured",
        )
    return price_id


@router.post("/create-checkout-session")
def create_checkout_session(
    data: CreateCheckoutSession,
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == organization_id
    ).first()

    if not subscription or not subscription.stripe_customer_id:
        customer = stripe_service.create_customer(
            email=current_user.email,
            name=current_user.name,
            organization_id=organization_id,
        )
        customer_id = customer.id
        now = datetime.utcnow()
        if subscription is None:
            subscription = Subscription(
                organization_id=organization_id,
                plan=data.plan,
                status="incomplete",
                current_period_start=now,
                current_period_end=now + timedelta(days=14),
                created_at=now,
            )
            db.add(subscription)
        subscription.stripe_customer_id = customer_id
        db.commit()
    else:
        customer_id = subscription.stripe_customer_id

    session = stripe_service.create_checkout_session(
        customer_id=customer_id,
        price_id=_price_id_for_plan(data.plan),
        success_url=data.success_url,
        cancel_url=data.cancel_url,
        organization_id=organization_id,
        plan=data.plan,
    )
    return {"checkout_url": session.url}


@router.get("/subscription", response_model=SubscriptionResponse)
def get_subscription(
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == organization_id
    ).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    return subscription


@router.post("/cancel-subscription")
def cancel_subscription(
    current_user: User = Depends(manager_only),
    organization_id: int = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == organization_id
    ).first()
    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription")

    stripe_service.cancel_subscription(subscription.stripe_subscription_id)
    subscription.cancel_at_period_end = True
    db.commit()
    return {"message": "Subscription will be canceled at the end of the current period"}
