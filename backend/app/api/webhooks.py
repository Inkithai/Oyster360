"""
Stripe Webhook Handlers
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.billing_service import BillingService
import stripe
import os
import json

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    billing_service = BillingService(db)

    # Handle different event types
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Create subscription record
        billing_service.create_subscription(
            organization_id=int(session["metadata"].get("organization_id", 0)),
            stripe_customer_id=session["customer"],
            stripe_subscription_id=session["subscription"],
            plan=session["metadata"].get("plan", "starter"),
            status="trialing"
        )

    elif event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
        # Update subscription status
        if invoice.get("subscription"):
            billing_service.update_subscription_status(
                invoice["subscription"], "active"
            )

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        # Handle failed payment
        if invoice.get("subscription"):
            billing_service.update_subscription_status(
                invoice["subscription"], "past_due"
            )

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        # Handle subscription cancellation
        billing_service.update_subscription_status(
            subscription["id"], "canceled"
        )

    elif event["type"] == "customer.subscription.trial_will_end":
        subscription = event["data"]["object"]
        # Send notification about trial ending
        pass

    return {"status": "success"}