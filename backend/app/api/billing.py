from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.services.stripe_service import StripeService
from app.core.dependencies import get_current_user, manager_only
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()
stripe_service = StripeService()

class CreateCheckoutSession(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str

class SubscriptionResponse(BaseModel):
    id: int
    plan: str
    status: str
    current_period_end: datetime

@router.post("/create-checkout-session")
def create_checkout_session(
    data: CreateCheckoutSession,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get or create Stripe customer
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == current_user.current_organization_id
    ).first()
    
    if not subscription or not subscription.stripe_customer_id:
        # Create new customer
        customer = stripe_service.create_customer(
            email=current_user.email,
            name=current_user.name,
            organization_id=current_user.current_organization_id or 1
        )
        customer_id = customer.id
    else:
        customer_id = subscription.stripe_customer_id
    
    # Create checkout session
    session = stripe_service.create_checkout_session(
        customer_id=customer_id,
        price_id=data.price_id,
        success_url=data.success_url,
        cancel_url=data.cancel_url
    )
    
    return {"checkout_url": session.url}

@router.get("/subscription", response_model=SubscriptionResponse)
def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == current_user.current_organization_id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    return subscription

@router.post("/cancel-subscription")
def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == current_user.current_organization_id
    ).first()
    
    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription")
    
    # Cancel in Stripe
    stripe_service.cancel_subscription(subscription.stripe_subscription_id)
    
    # Update local record
    subscription.cancel_at_period_end = True
    db.commit()
    
    return {"message": "Subscription will be canceled at the end of the current period"}