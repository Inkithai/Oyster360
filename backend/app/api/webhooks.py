"""Verified, idempotent Stripe webhook handlers."""

from datetime import datetime, timezone
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import stripe

from app.database.database import get_db
from app.models.organization import Organization
from app.services.billing_service import BillingService

router = APIRouter()


def _stripe_api_key() -> str | None:
    """Resolve the Stripe key lazily instead of mutating global state at import."""
    return os.getenv("STRIPE_SECRET_KEY")


def _timestamp(value) -> datetime | None:
    """Convert a Unix timestamp to a naive UTC datetime (DB columns are naive)."""
    if not value:
        return None
    return datetime.fromtimestamp(value, tz=timezone.utc).replace(tzinfo=None)


def _organization_id(metadata: dict, db: Session) -> int:
    try:
        organization_id = int(metadata.get("organization_id"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Stripe event is missing organization metadata",
        )

    exists = db.query(Organization.id).filter(
        Organization.id == organization_id
    ).first()
    if not exists:
        raise HTTPException(status_code=400, detail="Unknown organization")
    return organization_id


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhooks are not configured")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    stripe.api_key = _stripe_api_key()

    try:
        event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid payload") from exc
    except stripe.SignatureVerificationError as exc:
        raise HTTPException(status_code=400, detail="Invalid signature") from exc

    billing = BillingService(db)
    event_type = event["type"]
    obj = event["data"]["object"]

    if event_type == "checkout.session.completed":
        organization_id = _organization_id(obj.get("metadata", {}), db)
        if not obj.get("customer") or not obj.get("subscription"):
            raise HTTPException(status_code=400, detail="Incomplete checkout session")
        billing.create_subscription(
            organization_id=organization_id,
            stripe_customer_id=obj["customer"],
            stripe_subscription_id=obj["subscription"],
            plan=obj.get("metadata", {}).get("plan", "starter"),
            status="trialing",
        )

    elif event_type in {
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    }:
        metadata = obj.get("metadata", {})
        organization_id = _organization_id(metadata, db)
        billing.sync_subscription(
            organization_id=organization_id,
            stripe_customer_id=obj["customer"],
            stripe_subscription_id=obj["id"],
            plan=metadata.get("plan", "starter"),
            status=obj.get("status", "canceled"),
            current_period_start=_timestamp(obj.get("current_period_start")),
            current_period_end=_timestamp(obj.get("current_period_end")),
            cancel_at_period_end=bool(obj.get("cancel_at_period_end", False)),
        )

    elif event_type == "invoice.paid" and obj.get("subscription"):
        billing.update_subscription_status(obj["subscription"], "active")

    elif event_type == "invoice.payment_failed" and obj.get("subscription"):
        billing.update_subscription_status(obj["subscription"], "past_due")

    return {"status": "success"}
