"""
AUTOOS Payment API Router

FastAPI router for payment and subscription endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Header
from typing import Optional, Dict, List
from datetime import datetime
import logging

from src.autoos.payment.stripe_service import (
    StripeService,
    SubscriptionManager,
    StripeCustomerRequest,
    StripePaymentIntentRequest,
    StripeSubscriptionRequest
)
from src.autoos.payment.qr_payment import (
    QRPaymentService,
    FreeTrialService,
    QRPaymentRequest,
    QRPaymentResponse
)
from src.autoos.payment.webhook_handler import StripeWebhookHandler
from src.autoos.payment.config import SubscriptionTiers, FeatureFlags
from src.autoos.core.models import SubscriptionTier

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/payments", tags=["payments"])

# Initialize services
stripe_service = StripeService()
subscription_manager = SubscriptionManager(stripe_service)
qr_payment_service = QRPaymentService()
free_trial_service = FreeTrialService()
webhook_handler = StripeWebhookHandler(stripe_service)


# ============================================================================
# Pricing and Tiers
# ============================================================================

@router.get("/pricing")
async def get_pricing_tiers():
    """
    Get all available pricing tiers
    
    Returns:
        List of pricing tiers with details
    """
    try:
        tiers = SubscriptionTiers.get_all_tiers()
        
        return {
            "tiers": [
                {
                    "tier_id": tier.tier_id,
                    "name": tier.name,
                    "display_name": tier.display_name,
                    "price_monthly_usd": tier.price_monthly_usd,
                    "price_annual_usd": tier.price_annual_usd,
                    "price_monthly_inr": tier.price_monthly_inr,
                    "price_annual_inr": tier.price_annual_inr,
                    "workflows_limit": tier.workflows_limit,
                    "agents_limit": tier.agents_limit,
                    "features": tier.features,
                    "is_trial": tier.is_trial,
                    "trial_days": tier.trial_days,
                    "trial_credits": tier.trial_credits,
                    "recommended": tier.recommended
                }
                for tier in tiers
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching pricing tiers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Free Trial
# ============================================================================

@router.post("/start-trial")
async def start_free_trial(user_id: str):
    """
    Start a free trial for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Trial details
    """
    if not FeatureFlags.ENABLE_FREE_TRIAL:
        raise HTTPException(status_code=403, detail="Free trial is not enabled")
    
    try:
        trial_data = await free_trial_service.start_free_trial(user_id)
        
        return {
            "success": True,
            "message": "Free trial activated successfully",
            "trial": trial_data
        }
    except Exception as e:
        logger.error(f"Error starting free trial: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trial-status")
async def get_trial_status(user_id: str):
    """
    Get trial status for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Trial status details
    """
    try:
        trial_status = await free_trial_service.check_trial_status(user_id)
        
        return {
            "success": True,
            "trial": trial_status
        }
    except Exception as e:
        logger.error(f"Error fetching trial status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Stripe Payment Intents
# ============================================================================

@router.post("/create-intent")
async def create_payment_intent(request: StripePaymentIntentRequest):
    """
    Create a Stripe payment intent for one-time payment
    
    Args:
        request: Payment intent request
        
    Returns:
        Payment intent details with client secret
    """
    if not FeatureFlags.ENABLE_CARD_PAYMENTS:
        raise HTTPException(status_code=403, detail="Card payments are not enabled")
    
    try:
        payment_intent = await stripe_service.create_payment_intent(request)
        
        return {
            "success": True,
            "payment_intent": payment_intent
        }
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# QR Code Payments
# ============================================================================

@router.post("/qr-code", response_model=QRPaymentResponse)
async def generate_qr_payment(request: QRPaymentRequest):
    """
    Generate QR code for UPI payment
    
    Args:
        request: QR payment request
        
    Returns:
        QR code and payment details
    """
    if not FeatureFlags.ENABLE_UPI_PAYMENTS:
        raise HTTPException(status_code=403, detail="UPI payments are not enabled")
    
    try:
        qr_payment = await qr_payment_service.create_qr_payment(request)
        return qr_payment
    except Exception as e:
        logger.error(f"Error generating QR payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/qr-code/{payment_id}/status")
async def check_qr_payment_status(payment_id: str):
    """
    Check QR code payment status
    
    Args:
        payment_id: Payment identifier
        
    Returns:
        Payment status
    """
    try:
        status = await qr_payment_service.check_payment_status(payment_id)
        
        return {
            "payment_id": payment_id,
            "status": status.value
        }
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Subscriptions
# ============================================================================

@router.post("/subscribe")
async def create_subscription(request: StripeSubscriptionRequest):
    """
    Create a new subscription
    
    Args:
        request: Subscription creation request
        
    Returns:
        Subscription details
    """
    if not FeatureFlags.ENABLE_CARD_PAYMENTS:
        raise HTTPException(status_code=403, detail="Subscriptions are not enabled")
    
    try:
        subscription = await stripe_service.create_subscription(request)
        
        return {
            "success": True,
            "subscription": subscription
        }
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscription")
async def get_subscription(subscription_id: str):
    """
    Get subscription details
    
    Args:
        subscription_id: Stripe subscription ID
        
    Returns:
        Subscription details
    """
    try:
        subscription = await stripe_service.get_subscription(subscription_id)
        
        return {
            "success": True,
            "subscription": subscription
        }
    except Exception as e:
        logger.error(f"Error fetching subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel-subscription")
async def cancel_subscription(subscription_id: str, immediate: bool = False):
    """
    Cancel a subscription
    
    Args:
        subscription_id: Stripe subscription ID
        immediate: Cancel immediately or at period end
        
    Returns:
        Cancellation confirmation
    """
    try:
        result = await stripe_service.cancel_subscription(subscription_id, immediate)
        
        return {
            "success": True,
            "message": "Subscription cancelled successfully",
            "subscription": result
        }
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upgrade")
async def upgrade_subscription(
    subscription_id: str,
    new_tier: SubscriptionTier,
    billing_cycle: str = "monthly"
):
    """
    Upgrade subscription to a higher tier
    
    Args:
        subscription_id: Current subscription ID
        new_tier: New subscription tier
        billing_cycle: Billing cycle (monthly or annual)
        
    Returns:
        Updated subscription details
    """
    try:
        subscription = await subscription_manager.upgrade_subscription(
            subscription_id,
            new_tier,
            billing_cycle
        )
        
        return {
            "success": True,
            "message": "Subscription upgraded successfully",
            "subscription": subscription
        }
    except Exception as e:
        logger.error(f"Error upgrading subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/downgrade")
async def downgrade_subscription(
    subscription_id: str,
    new_tier: SubscriptionTier,
    billing_cycle: str = "monthly"
):
    """
    Downgrade subscription to a lower tier
    
    Args:
        subscription_id: Current subscription ID
        new_tier: New subscription tier
        billing_cycle: Billing cycle (monthly or annual)
        
    Returns:
        Updated subscription details
    """
    try:
        subscription = await subscription_manager.downgrade_subscription(
            subscription_id,
            new_tier,
            billing_cycle
        )
        
        return {
            "success": True,
            "message": "Subscription downgrade scheduled",
            "subscription": subscription
        }
    except Exception as e:
        logger.error(f"Error downgrading subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proration-preview")
async def preview_proration(
    subscription_id: str,
    new_tier: SubscriptionTier,
    billing_cycle: str = "monthly"
):
    """
    Preview proration amount for subscription change
    
    Args:
        subscription_id: Current subscription ID
        new_tier: New subscription tier
        billing_cycle: Billing cycle (monthly or annual)
        
    Returns:
        Proration details
    """
    try:
        proration = await subscription_manager.calculate_proration(
            subscription_id,
            new_tier,
            billing_cycle
        )
        
        return {
            "success": True,
            "proration": proration
        }
    except Exception as e:
        logger.error(f"Error calculating proration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Usage and Limits
# ============================================================================

@router.get("/usage")
async def get_usage_stats(user_id: str):
    """
    Get current usage statistics for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Usage statistics
    """
    try:
        # Import session memory
        from src.autoos.memory.session_memory import SessionMemory
        import os
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "postgresql://autoos:autoos@localhost:5432/autoos")
        session_memory = SessionMemory(database_url)
        
        # Get user's subscription
        subscription = session_memory.get_user_subscription(user_id)
        
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")
        
        # Calculate remaining resources
        workflows_remaining = subscription["workflows_limit"] - subscription["workflows_used"]
        if subscription["workflows_limit"] == -1:
            workflows_remaining = -1  # Unlimited
        
        return {
            "success": True,
            "usage": {
                "workflows_limit": subscription["workflows_limit"],
                "workflows_used": subscription["workflows_used"],
                "workflows_remaining": workflows_remaining,
                "agents_limit": subscription["agents_limit"],
                "can_create_workflow": (
                    subscription["workflows_limit"] == -1
                    or subscription["workflows_used"] < subscription["workflows_limit"]
                ),
                "subscription_tier": subscription["tier"],
                "billing_cycle": subscription["billing_cycle"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching usage stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Payment Methods
# ============================================================================

@router.post("/update-payment-method")
async def update_payment_method(customer_id: str, payment_method_id: str):
    """
    Update customer's default payment method
    
    Args:
        customer_id: Stripe customer ID
        payment_method_id: New payment method ID
        
    Returns:
        Update confirmation
    """
    try:
        result = await stripe_service.update_payment_method(customer_id, payment_method_id)
        
        return {
            "success": True,
            "message": "Payment method updated successfully",
            "customer": result
        }
    except Exception as e:
        logger.error(f"Error updating payment method: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payment-methods")
async def list_payment_methods(customer_id: str):
    """
    List customer's payment methods
    
    Args:
        customer_id: Stripe customer ID
        
    Returns:
        List of payment methods
    """
    try:
        payment_methods = await stripe_service.list_payment_methods(customer_id)
        
        return {
            "success": True,
            "payment_methods": payment_methods
        }
    except Exception as e:
        logger.error(f"Error listing payment methods: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Billing History
# ============================================================================

@router.get("/history")
async def get_payment_history(user_id: str, limit: int = 10, offset: int = 0):
    """
    Get payment history for a user
    
    Args:
        user_id: User identifier
        limit: Number of records to return
        offset: Offset for pagination
        
    Returns:
        Payment history
    """
    try:
        # Import session memory
        from src.autoos.memory.session_memory import SessionMemory
        import os
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "postgresql://autoos:autoos@localhost:5432/autoos")
        session_memory = SessionMemory(database_url)
        
        # Query payment history
        payments = session_memory.get_payment_history(user_id, limit, offset)
        
        return {
            "success": True,
            "payments": payments,
            "total": len(payments),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching payment history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices")
async def get_invoices(user_id: str, limit: int = 10, offset: int = 0):
    """
    Get invoices for a user
    
    Args:
        user_id: User identifier
        limit: Number of invoices to return
        offset: Offset for pagination
        
    Returns:
        List of invoices
    """
    try:
        # Import session memory
        from src.autoos.memory.session_memory import SessionMemory
        import os
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "postgresql://autoos:autoos@localhost:5432/autoos")
        session_memory = SessionMemory(database_url)
        
        # Query invoices
        invoices = session_memory.get_user_invoices(user_id, limit, offset)
        
        return {
            "success": True,
            "invoices": invoices,
            "total": len(invoices),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}/download")
async def download_invoice(invoice_id: str):
    """
    Download invoice PDF
    
    Args:
        invoice_id: Invoice identifier
        
    Returns:
        Invoice PDF or download URL
    """
    try:
        # Import session memory
        from src.autoos.memory.session_memory import SessionMemory
        import os
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "postgresql://autoos:autoos@localhost:5432/autoos")
        session_memory = SessionMemory(database_url)
        
        # Get invoice from database
        # For now, return a placeholder response
        # In production, this would generate or retrieve the PDF
        
        return {
            "success": True,
            "invoice_id": invoice_id,
            "download_url": f"/api/invoices/{invoice_id}.pdf",
            "message": "Invoice PDF generation will be implemented with a PDF library"
        }
    except Exception as e:
        logger.error(f"Error downloading invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Webhooks
# ============================================================================

@router.post("/webhooks/stripe")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """
    Handle Stripe webhook events
    
    Args:
        request: FastAPI request object
        stripe_signature: Stripe signature header
        
    Returns:
        Processing confirmation
    """
    try:
        # Get raw body
        payload = await request.body()
        
        # Verify webhook signature
        event = await stripe_service.verify_webhook_signature(payload, stripe_signature)
        
        # Handle event
        result = await webhook_handler.handle_webhook(event)
        
        return result
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Customer Management
# ============================================================================

@router.post("/create-customer")
async def create_customer(request: StripeCustomerRequest):
    """
    Create a Stripe customer
    
    Args:
        request: Customer creation request
        
    Returns:
        Customer details
    """
    try:
        customer = await stripe_service.create_customer(request)
        
        return {
            "success": True,
            "customer": customer
        }
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer")
async def get_customer(customer_id: str):
    """
    Get Stripe customer details
    
    Args:
        customer_id: Stripe customer ID
        
    Returns:
        Customer details
    """
    try:
        customer = await stripe_service.get_customer(customer_id)
        
        return {
            "success": True,
            "customer": customer
        }
    except Exception as e:
        logger.error(f"Error fetching customer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
