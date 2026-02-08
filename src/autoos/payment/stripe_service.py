"""
AUTOOS Stripe Payment Service

Handles Stripe integration for card payments and subscription management.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
import stripe
import os
from pydantic import BaseModel

from src.autoos.payment.config import StripeConfig, SubscriptionTiers
from src.autoos.core.models import (
    SubscriptionTier,
    SubscriptionStatus,
    PaymentStatus,
    PaymentType
)


class StripeCustomerRequest(BaseModel):
    """Request to create Stripe customer"""
    user_id: str
    email: str
    name: str
    metadata: Optional[Dict] = None


class StripePaymentIntentRequest(BaseModel):
    """Request to create payment intent"""
    user_id: str
    amount: float
    currency: str = "USD"
    description: str
    customer_id: Optional[str] = None
    payment_method: Optional[str] = None


class StripeSubscriptionRequest(BaseModel):
    """Request to create subscription"""
    user_id: str
    customer_id: str
    tier: SubscriptionTier
    billing_cycle: str = "monthly"  # monthly or annual
    payment_method: Optional[str] = None


class StripeService:
    """Service for Stripe payment processing"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Stripe service
        
        Args:
            api_key: Stripe secret API key (defaults to environment variable)
        """
        self.api_key = api_key or StripeConfig.SECRET_KEY
        if not self.api_key:
            raise ValueError("Stripe API key is required")
        
        stripe.api_key = self.api_key
        self.webhook_secret = StripeConfig.WEBHOOK_SECRET
    
    async def create_customer(self, request: StripeCustomerRequest) -> Dict:
        """
        Create a Stripe customer
        
        Args:
            request: Customer creation request
            
        Returns:
            Stripe customer object
        """
        try:
            metadata = request.metadata or {}
            metadata["user_id"] = request.user_id
            
            customer = stripe.Customer.create(
                email=request.email,
                name=request.name,
                metadata=metadata
            )
            
            return {
                "customer_id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "created": customer.created,
                "metadata": customer.metadata
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create Stripe customer: {str(e)}")
    
    async def create_payment_intent(self, request: StripePaymentIntentRequest) -> Dict:
        """
        Create a payment intent for one-time payment
        
        Args:
            request: Payment intent request
            
        Returns:
            Payment intent details
        """
        try:
            # Convert amount to cents (Stripe uses smallest currency unit)
            amount_cents = int(request.amount * 100)
            
            payment_intent_params = {
                "amount": amount_cents,
                "currency": request.currency.lower(),
                "description": request.description,
                "metadata": {
                    "user_id": request.user_id
                }
            }
            
            if request.customer_id:
                payment_intent_params["customer"] = request.customer_id
            
            if request.payment_method:
                payment_intent_params["payment_method"] = request.payment_method
                payment_intent_params["confirm"] = True
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
            
            return {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": request.amount,
                "currency": request.currency,
                "status": payment_intent.status,
                "created": payment_intent.created
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create payment intent: {str(e)}")
    
    async def create_subscription(self, request: StripeSubscriptionRequest) -> Dict:
        """
        Create a Stripe subscription
        
        Args:
            request: Subscription creation request
            
        Returns:
            Subscription details
        """
        try:
            # Get tier configuration
            tier_config = SubscriptionTiers.get_tier_by_id(request.tier.value)
            if not tier_config:
                raise ValueError(f"Invalid subscription tier: {request.tier}")
            
            # Determine price based on billing cycle
            if request.billing_cycle == "annual":
                price_amount = tier_config.price_annual_usd
            else:
                price_amount = tier_config.price_monthly_usd
            
            # Create or retrieve price in Stripe
            price = await self._get_or_create_price(
                tier=request.tier,
                amount=price_amount,
                currency="USD",
                interval=request.billing_cycle
            )
            
            # Create subscription
            subscription_params = {
                "customer": request.customer_id,
                "items": [{"price": price["id"]}],
                "metadata": {
                    "user_id": request.user_id,
                    "tier": request.tier.value
                }
            }
            
            if request.payment_method:
                subscription_params["default_payment_method"] = request.payment_method
            
            subscription = stripe.Subscription.create(**subscription_params)
            
            return {
                "subscription_id": subscription.id,
                "customer_id": subscription.customer,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "tier": request.tier.value,
                "billing_cycle": request.billing_cycle,
                "amount": price_amount,
                "currency": "USD"
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    async def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> Dict:
        """
        Cancel a Stripe subscription
        
        Args:
            subscription_id: Stripe subscription ID
            immediate: If True, cancel immediately; if False, cancel at period end
            
        Returns:
            Cancelled subscription details
        """
        try:
            if immediate:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "cancelled_at": datetime.fromtimestamp(subscription.canceled_at) if subscription.canceled_at else None,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    async def update_payment_method(self, customer_id: str, payment_method_id: str) -> Dict:
        """
        Update customer's default payment method
        
        Args:
            customer_id: Stripe customer ID
            payment_method_id: New payment method ID
            
        Returns:
            Updated customer details
        """
        try:
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            # Set as default payment method
            customer = stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
            
            return {
                "customer_id": customer.id,
                "default_payment_method": payment_method_id,
                "updated": True
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to update payment method: {str(e)}")
    
    async def get_customer(self, customer_id: str) -> Dict:
        """
        Get Stripe customer details
        
        Args:
            customer_id: Stripe customer ID
            
        Returns:
            Customer details
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)
            
            return {
                "customer_id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "default_payment_method": customer.invoice_settings.default_payment_method,
                "metadata": customer.metadata
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to retrieve customer: {str(e)}")
    
    async def get_subscription(self, subscription_id: str) -> Dict:
        """
        Get Stripe subscription details
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Subscription details
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "subscription_id": subscription.id,
                "customer_id": subscription.customer,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "metadata": subscription.metadata
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to retrieve subscription: {str(e)}")
    
    async def list_payment_methods(self, customer_id: str) -> List[Dict]:
        """
        List customer's payment methods
        
        Args:
            customer_id: Stripe customer ID
            
        Returns:
            List of payment methods
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            
            return [
                {
                    "payment_method_id": pm.id,
                    "type": pm.type,
                    "card": {
                        "brand": pm.card.brand,
                        "last4": pm.card.last4,
                        "exp_month": pm.card.exp_month,
                        "exp_year": pm.card.exp_year
                    } if pm.card else None
                }
                for pm in payment_methods.data
            ]
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to list payment methods: {str(e)}")
    
    async def verify_webhook_signature(self, payload: bytes, signature: str) -> Dict:
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            
        Returns:
            Verified event object
        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                self.webhook_secret
            )
            return event
        except ValueError as e:
            raise Exception(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f"Invalid signature: {str(e)}")
    
    async def _get_or_create_price(
        self,
        tier: SubscriptionTier,
        amount: float,
        currency: str,
        interval: str
    ) -> Dict:
        """
        Get or create a Stripe price for a subscription tier
        
        Args:
            tier: Subscription tier
            amount: Price amount
            currency: Currency code
            interval: Billing interval (monthly or annual)
            
        Returns:
            Price object
        """
        try:
            # Create a unique price ID
            price_id = f"{tier.value}_{interval}_{currency.lower()}"
            
            # Try to retrieve existing price
            try:
                price = stripe.Price.retrieve(price_id)
                return {"id": price.id, "amount": price.unit_amount / 100}
            except stripe.error.InvalidRequestError:
                # Price doesn't exist, create it
                pass
            
            # Get or create product
            product = await self._get_or_create_product(tier)
            
            # Create price
            price = stripe.Price.create(
                product=product["id"],
                unit_amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                recurring={"interval": "month" if interval == "monthly" else "year"},
                lookup_key=price_id
            )
            
            return {"id": price.id, "amount": amount}
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create price: {str(e)}")
    
    async def _get_or_create_product(self, tier: SubscriptionTier) -> Dict:
        """
        Get or create a Stripe product for a subscription tier
        
        Args:
            tier: Subscription tier
            
        Returns:
            Product object
        """
        try:
            tier_config = SubscriptionTiers.get_tier_by_id(tier.value)
            product_id = f"autoos_{tier.value}"
            
            # Try to retrieve existing product
            try:
                product = stripe.Product.retrieve(product_id)
                return {"id": product.id, "name": product.name}
            except stripe.error.InvalidRequestError:
                # Product doesn't exist, create it
                pass
            
            # Create product
            product = stripe.Product.create(
                id=product_id,
                name=tier_config.display_name,
                description=f"AUTOOS {tier_config.display_name} subscription",
                metadata={"tier": tier.value}
            )
            
            return {"id": product.id, "name": product.name}
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create product: {str(e)}")


class SubscriptionManager:
    """Manager for subscription operations"""
    
    def __init__(self, stripe_service: StripeService):
        """
        Initialize subscription manager
        
        Args:
            stripe_service: Stripe service instance
        """
        self.stripe_service = stripe_service
    
    async def upgrade_subscription(
        self,
        subscription_id: str,
        new_tier: SubscriptionTier,
        billing_cycle: str = "monthly"
    ) -> Dict:
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
            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Get new tier configuration
            tier_config = SubscriptionTiers.get_tier_by_id(new_tier.value)
            if not tier_config:
                raise ValueError(f"Invalid subscription tier: {new_tier}")
            
            # Determine new price
            if billing_cycle == "annual":
                price_amount = tier_config.price_annual_usd
            else:
                price_amount = tier_config.price_monthly_usd
            
            # Get or create new price
            price = await self.stripe_service._get_or_create_price(
                tier=new_tier,
                amount=price_amount,
                currency="USD",
                interval=billing_cycle
            )
            
            # Update subscription with proration
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": price["id"]
                }],
                proration_behavior="create_prorations",
                metadata={
                    **subscription.metadata,
                    "tier": new_tier.value
                }
            )
            
            return {
                "subscription_id": updated_subscription.id,
                "tier": new_tier.value,
                "status": updated_subscription.status,
                "current_period_end": datetime.fromtimestamp(updated_subscription.current_period_end),
                "amount": price_amount,
                "billing_cycle": billing_cycle
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to upgrade subscription: {str(e)}")
    
    async def downgrade_subscription(
        self,
        subscription_id: str,
        new_tier: SubscriptionTier,
        billing_cycle: str = "monthly"
    ) -> Dict:
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
            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Get new tier configuration
            tier_config = SubscriptionTiers.get_tier_by_id(new_tier.value)
            if not tier_config:
                raise ValueError(f"Invalid subscription tier: {new_tier}")
            
            # Determine new price
            if billing_cycle == "annual":
                price_amount = tier_config.price_annual_usd
            else:
                price_amount = tier_config.price_monthly_usd
            
            # Get or create new price
            price = await self.stripe_service._get_or_create_price(
                tier=new_tier,
                amount=price_amount,
                currency="USD",
                interval=billing_cycle
            )
            
            # Update subscription at period end (no immediate proration for downgrades)
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": price["id"]
                }],
                proration_behavior="none",
                billing_cycle_anchor="unchanged",
                metadata={
                    **subscription.metadata,
                    "tier": new_tier.value
                }
            )
            
            return {
                "subscription_id": updated_subscription.id,
                "tier": new_tier.value,
                "status": updated_subscription.status,
                "current_period_end": datetime.fromtimestamp(updated_subscription.current_period_end),
                "amount": price_amount,
                "billing_cycle": billing_cycle,
                "note": "Downgrade will take effect at the end of current billing period"
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to downgrade subscription: {str(e)}")
    
    async def check_subscription_limits(self, user_id: str, tier: SubscriptionTier) -> Dict:
        """
        Check subscription limits for a user
        
        Args:
            user_id: User identifier
            tier: Subscription tier
            
        Returns:
            Limit status
        """
        # Get tier configuration
        tier_config = SubscriptionTiers.get_tier_by_id(tier.value)
        if not tier_config:
            raise ValueError(f"Invalid subscription tier: {tier}")
        
        # Query database for current usage
        # (Database query would go here)
        
        # For now, return mock data
        workflows_used = 0
        agents_used = 0
        
        return {
            "workflows_limit": tier_config.workflows_limit,
            "workflows_used": workflows_used,
            "workflows_remaining": tier_config.workflows_limit - workflows_used if tier_config.workflows_limit > 0 else -1,
            "agents_limit": tier_config.agents_limit,
            "agents_used": agents_used,
            "agents_remaining": tier_config.agents_limit - agents_used if tier_config.agents_limit > 0 else -1,
            "can_create_workflow": tier_config.workflows_limit == -1 or workflows_used < tier_config.workflows_limit,
            "can_create_agent": tier_config.agents_limit == -1 or agents_used < tier_config.agents_limit
        }
    
    async def calculate_proration(
        self,
        subscription_id: str,
        new_tier: SubscriptionTier,
        billing_cycle: str = "monthly"
    ) -> Dict:
        """
        Calculate proration amount for subscription change
        
        Args:
            subscription_id: Current subscription ID
            new_tier: New subscription tier
            billing_cycle: Billing cycle (monthly or annual)
            
        Returns:
            Proration details
        """
        try:
            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Get new tier configuration
            tier_config = SubscriptionTiers.get_tier_by_id(new_tier.value)
            if not tier_config:
                raise ValueError(f"Invalid subscription tier: {new_tier}")
            
            # Determine new price
            if billing_cycle == "annual":
                new_price = tier_config.price_annual_usd
            else:
                new_price = tier_config.price_monthly_usd
            
            # Get or create new price
            price = await self.stripe_service._get_or_create_price(
                tier=new_tier,
                amount=new_price,
                currency="USD",
                interval=billing_cycle
            )
            
            # Preview upcoming invoice with proration
            upcoming_invoice = stripe.Invoice.upcoming(
                customer=subscription.customer,
                subscription=subscription_id,
                subscription_items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": price["id"]
                }],
                subscription_proration_behavior="create_prorations"
            )
            
            # Calculate proration amount
            proration_amount = sum(
                line.amount for line in upcoming_invoice.lines.data
                if line.proration
            ) / 100  # Convert from cents
            
            return {
                "current_tier": subscription.metadata.get("tier"),
                "new_tier": new_tier.value,
                "proration_amount": proration_amount,
                "next_invoice_amount": upcoming_invoice.total / 100,
                "next_invoice_date": datetime.fromtimestamp(upcoming_invoice.period_end)
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to calculate proration: {str(e)}")
