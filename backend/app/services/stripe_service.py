"""
Oyster360 Stripe Billing Service
Production-ready Stripe integration
"""
import stripe
import os
from typing import Dict, Any, Optional
from datetime import datetime

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")

class StripeService:
    def __init__(self):
        self.stripe = stripe

    def create_customer(self, email: str, name: str, organization_id: int) -> Dict[str, Any]:
        """Create a Stripe customer"""
        customer = self.stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                "organization_id": str(organization_id)
            }
        )
        return customer

    def create_checkout_session(
        self, 
        customer_id: str, 
        price_id: str, 
        success_url: str, 
        cancel_url: str,
        organization_id: int,
        plan: str,
        trial_days: int = 14
    ) -> Dict[str, Any]:
        """Create a checkout session for subscription"""
        session = self.stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(organization_id),
            metadata={
                'organization_id': str(organization_id),
                'plan': plan,
            },
            subscription_data={
                'trial_period_days': trial_days,
                'metadata': {
                    'organization_id': str(organization_id),
                    'plan': plan,
                },
            }
        )
        return session

    def create_customer_portal_session(self, customer_id: str, return_url: str) -> Dict[str, Any]:
        """Create customer portal for subscription management"""
        session = self.stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url
        )
        return session

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription details"""
        return self.stripe.Subscription.retrieve(subscription_id)

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        return self.stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )

    def create_price(self, product_id: str, unit_amount: int, currency: str = "usd", interval: str = "month") -> Dict[str, Any]:
        """Create a price for a product"""
        price = self.stripe.Price.create(
            product=product_id,
            unit_amount=unit_amount,
            currency=currency,
            recurring={"interval": interval}
        )
        return price

    def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhooks"""
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError:
            raise Exception("Invalid payload")
        except self.stripe.error.SignatureVerificationError:
            raise Exception("Invalid signature")