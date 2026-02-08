"""
AUTOOS Stripe Webhook Handler

Handles Stripe webhook events for payment and subscription updates.
"""

from datetime import datetime
from typing import Dict, Optional
import logging

from src.autoos.payment.stripe_service import StripeService
from src.autoos.core.models import (
    PaymentStatus,
    SubscriptionStatus,
    SubscriptionTier
)

logger = logging.getLogger(__name__)


class StripeWebhookHandler:
    """Handler for Stripe webhook events"""
    
    def __init__(self, stripe_service: StripeService):
        """
        Initialize webhook handler
        
        Args:
            stripe_service: Stripe service instance
        """
        self.stripe_service = stripe_service
        
        # Map event types to handler methods
        self.event_handlers = {
            "payment_intent.succeeded": self.handle_payment_intent_succeeded,
            "payment_intent.failed": self.handle_payment_intent_failed,
            "customer.subscription.created": self.handle_subscription_created,
            "customer.subscription.updated": self.handle_subscription_updated,
            "customer.subscription.deleted": self.handle_subscription_deleted,
            "invoice.payment_succeeded": self.handle_invoice_payment_succeeded,
            "invoice.payment_failed": self.handle_invoice_payment_failed,
            "customer.created": self.handle_customer_created,
            "customer.updated": self.handle_customer_updated,
            "payment_method.attached": self.handle_payment_method_attached,
            "payment_method.detached": self.handle_payment_method_detached
        }
    
    async def handle_webhook(self, event: Dict) -> Dict:
        """
        Handle incoming webhook event
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        event_type = event.get("type")
        event_id = event.get("id")
        
        logger.info(f"Processing webhook event: {event_type} (ID: {event_id})")
        
        # Get handler for event type
        handler = self.event_handlers.get(event_type)
        
        if not handler:
            logger.warning(f"No handler for event type: {event_type}")
            return {
                "status": "ignored",
                "event_type": event_type,
                "message": f"No handler configured for {event_type}"
            }
        
        try:
            # Call handler
            result = await handler(event)
            
            logger.info(f"Successfully processed event {event_id}: {event_type}")
            
            return {
                "status": "success",
                "event_type": event_type,
                "event_id": event_id,
                "result": result
            }
        except Exception as e:
            logger.error(f"Error processing event {event_id}: {str(e)}")
            
            return {
                "status": "error",
                "event_type": event_type,
                "event_id": event_id,
                "error": str(e)
            }
    
    async def handle_payment_intent_succeeded(self, event: Dict) -> Dict:
        """
        Handle successful payment intent
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        payment_intent = event["data"]["object"]
        
        payment_id = payment_intent["id"]
        amount = payment_intent["amount"] / 100  # Convert from cents
        currency = payment_intent["currency"].upper()
        customer_id = payment_intent.get("customer")
        user_id = payment_intent["metadata"].get("user_id")
        
        logger.info(f"Payment succeeded: {payment_id} - ${amount} {currency}")
        
        # Update payment status in database
        # (Database update would go here)
        
        # Send payment confirmation email
        # (Email service would go here)
        
        return {
            "payment_id": payment_id,
            "amount": amount,
            "currency": currency,
            "user_id": user_id,
            "status": "completed"
        }
    
    async def handle_payment_intent_failed(self, event: Dict) -> Dict:
        """
        Handle failed payment intent
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        payment_intent = event["data"]["object"]
        
        payment_id = payment_intent["id"]
        amount = payment_intent["amount"] / 100
        currency = payment_intent["currency"].upper()
        user_id = payment_intent["metadata"].get("user_id")
        error_message = payment_intent.get("last_payment_error", {}).get("message", "Unknown error")
        
        logger.warning(f"Payment failed: {payment_id} - {error_message}")
        
        # Update payment status in database
        # (Database update would go here)
        
        # Send payment failure notification
        # (Email service would go here)
        
        return {
            "payment_id": payment_id,
            "amount": amount,
            "currency": currency,
            "user_id": user_id,
            "status": "failed",
            "error": error_message
        }
    
    async def handle_subscription_created(self, event: Dict) -> Dict:
        """
        Handle subscription creation
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        subscription = event["data"]["object"]
        
        subscription_id = subscription["id"]
        customer_id = subscription["customer"]
        status = subscription["status"]
        user_id = subscription["metadata"].get("user_id")
        tier = subscription["metadata"].get("tier")
        
        current_period_start = datetime.fromtimestamp(subscription["current_period_start"])
        current_period_end = datetime.fromtimestamp(subscription["current_period_end"])
        
        logger.info(f"Subscription created: {subscription_id} - Tier: {tier}")
        
        # Create subscription record in database
        # (Database insert would go here)
        
        # Send welcome email
        # (Email service would go here)
        
        return {
            "subscription_id": subscription_id,
            "user_id": user_id,
            "tier": tier,
            "status": status,
            "current_period_start": current_period_start.isoformat(),
            "current_period_end": current_period_end.isoformat()
        }
    
    async def handle_subscription_updated(self, event: Dict) -> Dict:
        """
        Handle subscription update
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        subscription = event["data"]["object"]
        previous_attributes = event["data"].get("previous_attributes", {})
        
        subscription_id = subscription["id"]
        customer_id = subscription["customer"]
        status = subscription["status"]
        user_id = subscription["metadata"].get("user_id")
        tier = subscription["metadata"].get("tier")
        
        logger.info(f"Subscription updated: {subscription_id} - Status: {status}")
        
        # Update subscription in database
        # (Database update would go here)
        
        # Check if status changed
        if "status" in previous_attributes:
            old_status = previous_attributes["status"]
            logger.info(f"Subscription status changed: {old_status} -> {status}")
            
            # Send status change notification
            # (Email service would go here)
        
        # Check if tier changed
        if "metadata" in previous_attributes and "tier" in previous_attributes.get("metadata", {}):
            old_tier = previous_attributes["metadata"]["tier"]
            logger.info(f"Subscription tier changed: {old_tier} -> {tier}")
            
            # Send tier change notification
            # (Email service would go here)
        
        return {
            "subscription_id": subscription_id,
            "user_id": user_id,
            "tier": tier,
            "status": status,
            "changes": list(previous_attributes.keys())
        }
    
    async def handle_subscription_deleted(self, event: Dict) -> Dict:
        """
        Handle subscription deletion/cancellation
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        subscription = event["data"]["object"]
        
        subscription_id = subscription["id"]
        customer_id = subscription["customer"]
        user_id = subscription["metadata"].get("user_id")
        tier = subscription["metadata"].get("tier")
        
        canceled_at = datetime.fromtimestamp(subscription["canceled_at"]) if subscription.get("canceled_at") else None
        
        logger.info(f"Subscription deleted: {subscription_id}")
        
        # Update subscription status in database
        # (Database update would go here)
        
        # Send cancellation confirmation email
        # (Email service would go here)
        
        return {
            "subscription_id": subscription_id,
            "user_id": user_id,
            "tier": tier,
            "status": "cancelled",
            "canceled_at": canceled_at.isoformat() if canceled_at else None
        }
    
    async def handle_invoice_payment_succeeded(self, event: Dict) -> Dict:
        """
        Handle successful invoice payment
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        
        invoice_id = invoice["id"]
        subscription_id = invoice.get("subscription")
        customer_id = invoice["customer"]
        amount_paid = invoice["amount_paid"] / 100
        currency = invoice["currency"].upper()
        
        logger.info(f"Invoice paid: {invoice_id} - ${amount_paid} {currency}")
        
        # Record payment in database
        # (Database insert would go here)
        
        # Send invoice receipt email
        # (Email service would go here)
        
        return {
            "invoice_id": invoice_id,
            "subscription_id": subscription_id,
            "amount": amount_paid,
            "currency": currency,
            "status": "paid"
        }
    
    async def handle_invoice_payment_failed(self, event: Dict) -> Dict:
        """
        Handle failed invoice payment
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        
        invoice_id = invoice["id"]
        subscription_id = invoice.get("subscription")
        customer_id = invoice["customer"]
        amount_due = invoice["amount_due"] / 100
        currency = invoice["currency"].upper()
        
        logger.warning(f"Invoice payment failed: {invoice_id} - ${amount_due} {currency}")
        
        # Update subscription status to past_due
        # (Database update would go here)
        
        # Send payment failure notification
        # (Email service would go here)
        
        return {
            "invoice_id": invoice_id,
            "subscription_id": subscription_id,
            "amount": amount_due,
            "currency": currency,
            "status": "payment_failed"
        }
    
    async def handle_customer_created(self, event: Dict) -> Dict:
        """
        Handle customer creation
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        customer = event["data"]["object"]
        
        customer_id = customer["id"]
        email = customer["email"]
        user_id = customer["metadata"].get("user_id")
        
        logger.info(f"Customer created: {customer_id} - {email}")
        
        # Update user record with Stripe customer ID
        # (Database update would go here)
        
        return {
            "customer_id": customer_id,
            "email": email,
            "user_id": user_id
        }
    
    async def handle_customer_updated(self, event: Dict) -> Dict:
        """
        Handle customer update
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        customer = event["data"]["object"]
        previous_attributes = event["data"].get("previous_attributes", {})
        
        customer_id = customer["id"]
        email = customer["email"]
        user_id = customer["metadata"].get("user_id")
        
        logger.info(f"Customer updated: {customer_id}")
        
        # Update customer information in database
        # (Database update would go here)
        
        return {
            "customer_id": customer_id,
            "email": email,
            "user_id": user_id,
            "changes": list(previous_attributes.keys())
        }
    
    async def handle_payment_method_attached(self, event: Dict) -> Dict:
        """
        Handle payment method attachment
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        payment_method = event["data"]["object"]
        
        payment_method_id = payment_method["id"]
        customer_id = payment_method.get("customer")
        payment_type = payment_method["type"]
        
        logger.info(f"Payment method attached: {payment_method_id} - Type: {payment_type}")
        
        # Record payment method in database
        # (Database insert would go here)
        
        return {
            "payment_method_id": payment_method_id,
            "customer_id": customer_id,
            "type": payment_type
        }
    
    async def handle_payment_method_detached(self, event: Dict) -> Dict:
        """
        Handle payment method detachment
        
        Args:
            event: Stripe event object
            
        Returns:
            Processing result
        """
        payment_method = event["data"]["object"]
        
        payment_method_id = payment_method["id"]
        payment_type = payment_method["type"]
        
        logger.info(f"Payment method detached: {payment_method_id}")
        
        # Remove payment method from database
        # (Database delete would go here)
        
        return {
            "payment_method_id": payment_method_id,
            "type": payment_type,
            "status": "detached"
        }
