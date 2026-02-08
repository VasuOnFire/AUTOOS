"""
Payment Configuration for AUTOOS

Centralized configuration for payment processing including UPI, Stripe, and subscription tiers.
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import os


# ============================================================================
# UPI Payment Configuration
# ============================================================================

class UPIConfig:
    """UPI Payment Configuration"""
    
    # Default UPI ID for receiving payments
    DEFAULT_UPI_ID = "vasu7993457842@axl"
    
    # Merchant details
    MERCHANT_NAME = "AUTOOS"
    MERCHANT_ID = os.getenv("UPI_MERCHANT_ID", "AUTOOS")
    
    # Payment timeout (in minutes)
    PAYMENT_TIMEOUT_MINUTES = 15
    
    # Supported UPI apps
    SUPPORTED_UPI_APPS = [
        "PhonePe",
        "Google Pay",
        "Paytm",
        "BHIM",
        "Amazon Pay",
        "WhatsApp Pay"
    ]
    
    # Deep link templates
    PHONEPE_DEEPLINK = "phonepe://pay?{params}"
    GOOGLEPAY_DEEPLINK = "tez://upi/pay?{params}"
    PAYTM_DEEPLINK = "paytmmp://pay?{params}"
    BHIM_DEEPLINK = "bhim://pay?{params}"


# ============================================================================
# Stripe Configuration
# ============================================================================

class StripeConfig:
    """Stripe Payment Configuration"""
    
    # API Keys (from environment)
    SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Currency
    DEFAULT_CURRENCY = "USD"
    
    # Payment methods
    SUPPORTED_PAYMENT_METHODS = ["card", "upi"]
    
    # Webhook events to listen for
    WEBHOOK_EVENTS = [
        "payment_intent.succeeded",
        "payment_intent.failed",
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
        "invoice.payment_succeeded",
        "invoice.payment_failed"
    ]


# ============================================================================
# Subscription Tiers Configuration
# ============================================================================

@dataclass
class SubscriptionTierConfig:
    """Configuration for a subscription tier"""
    
    tier_id: str
    name: str
    display_name: str
    price_monthly_usd: float
    price_annual_usd: float
    price_monthly_inr: float
    price_annual_inr: float
    workflows_limit: int  # -1 for unlimited
    agents_limit: int
    features: List[str]
    is_trial: bool = False
    trial_days: int = 0
    trial_credits: int = 0
    recommended: bool = False


class SubscriptionTiers:
    """All subscription tier configurations"""
    
    FREE_TRIAL = SubscriptionTierConfig(
        tier_id="free_trial",
        name="Free Trial",
        display_name="30-Day Free Trial",
        price_monthly_usd=0.00,
        price_annual_usd=0.00,
        price_monthly_inr=0.00,
        price_annual_inr=0.00,
        workflows_limit=10,
        agents_limit=2,
        features=[
            "10 workflows per month",
            "2 concurrent agents",
            "10 workflow credits",
            "All core features",
            "Email support",
            "No credit card required"
        ],
        is_trial=True,
        trial_days=30,
        trial_credits=10
    )
    
    STUDENT = SubscriptionTierConfig(
        tier_id="student",
        name="Student",
        display_name="Student Plan",
        price_monthly_usd=9.99,
        price_annual_usd=99.99,  # ~$8.33/month
        price_monthly_inr=799.00,
        price_annual_inr=7999.00,
        workflows_limit=100,
        agents_limit=5,
        features=[
            "100 workflows per month",
            "5 concurrent agents",
            "All core features",
            "Email support",
            "Perfect for learning and projects"
        ]
    )
    
    EMPLOYEE = SubscriptionTierConfig(
        tier_id="employee",
        name="Employee",
        display_name="Employee Plan",
        price_monthly_usd=29.99,
        price_annual_usd=299.99,  # ~$25/month
        price_monthly_inr=2399.00,
        price_annual_inr=23999.00,
        workflows_limit=500,
        agents_limit=20,
        features=[
            "500 workflows per month",
            "20 concurrent agents",
            "All core features",
            "Team collaboration",
            "Priority email support",
            "Perfect for small teams"
        ],
        recommended=True
    )
    
    PROFESSIONAL = SubscriptionTierConfig(
        tier_id="professional",
        name="Professional",
        display_name="Professional Plan",
        price_monthly_usd=99.99,
        price_annual_usd=999.99,  # ~$83.33/month
        price_monthly_inr=7999.00,
        price_annual_inr=79999.00,
        workflows_limit=-1,  # Unlimited
        agents_limit=100,
        features=[
            "Unlimited workflows",
            "100 concurrent agents",
            "All core features",
            "Advanced analytics",
            "Custom integrations",
            "24/7 support",
            "Perfect for agencies and large teams"
        ]
    )
    
    ENTERPRISE = SubscriptionTierConfig(
        tier_id="enterprise",
        name="Enterprise",
        display_name="Enterprise Plan",
        price_monthly_usd=0.00,  # Custom pricing
        price_annual_usd=0.00,
        price_monthly_inr=0.00,
        price_annual_inr=0.00,
        workflows_limit=-1,  # Unlimited
        agents_limit=-1,  # Unlimited
        features=[
            "Unlimited everything",
            "Dedicated support team",
            "On-premise deployment option",
            "Custom SLA",
            "Training and onboarding",
            "Custom integrations",
            "Perfect for large enterprises"
        ]
    )
    
    @classmethod
    def get_all_tiers(cls) -> List[SubscriptionTierConfig]:
        """Get all subscription tiers"""
        return [
            cls.FREE_TRIAL,
            cls.STUDENT,
            cls.EMPLOYEE,
            cls.PROFESSIONAL,
            cls.ENTERPRISE
        ]
    
    @classmethod
    def get_tier_by_id(cls, tier_id: str) -> SubscriptionTierConfig:
        """Get tier configuration by ID"""
        tiers = {
            "free_trial": cls.FREE_TRIAL,
            "student": cls.STUDENT,
            "employee": cls.EMPLOYEE,
            "professional": cls.PROFESSIONAL,
            "enterprise": cls.ENTERPRISE
        }
        return tiers.get(tier_id)
    
    @classmethod
    def get_paid_tiers(cls) -> List[SubscriptionTierConfig]:
        """Get only paid tiers (excluding free trial)"""
        return [
            cls.STUDENT,
            cls.EMPLOYEE,
            cls.PROFESSIONAL,
            cls.ENTERPRISE
        ]


# ============================================================================
# Payment Methods Configuration
# ============================================================================

class PaymentMethodConfig:
    """Payment method configuration"""
    
    # Available payment methods by region
    PAYMENT_METHODS_BY_REGION = {
        "IN": ["upi", "card", "netbanking"],  # India
        "US": ["card"],  # United States
        "GB": ["card"],  # United Kingdom
        "DEFAULT": ["card"]
    }
    
    # UPI payment details
    UPI_DETAILS = {
        "merchant_vpa": UPIConfig.DEFAULT_UPI_ID,
        "merchant_name": UPIConfig.MERCHANT_NAME,
        "supported_apps": UPIConfig.SUPPORTED_UPI_APPS
    }
    
    # Card payment details
    CARD_DETAILS = {
        "supported_cards": ["Visa", "Mastercard", "American Express"],
        "3d_secure": True,
        "save_card": True
    }


# ============================================================================
# Currency Configuration
# ============================================================================

class CurrencyConfig:
    """Currency configuration"""
    
    # Supported currencies
    SUPPORTED_CURRENCIES = ["USD", "INR", "EUR", "GBP"]
    
    # Default currency by region
    DEFAULT_CURRENCY_BY_REGION = {
        "IN": "INR",
        "US": "USD",
        "GB": "GBP",
        "EU": "EUR",
        "DEFAULT": "USD"
    }
    
    # Currency symbols
    CURRENCY_SYMBOLS = {
        "USD": "$",
        "INR": "₹",
        "EUR": "€",
        "GBP": "£"
    }
    
    # Exchange rates (approximate, should be updated from API)
    EXCHANGE_RATES = {
        "USD_TO_INR": 80.0,
        "USD_TO_EUR": 0.92,
        "USD_TO_GBP": 0.79
    }


# ============================================================================
# Email Configuration
# ============================================================================

class EmailConfig:
    """Email configuration for payment notifications"""
    
    # Email templates
    TEMPLATES = {
        "trial_activated": "trial_activated.html",
        "trial_expiring_7days": "trial_expiring_7days.html",
        "trial_expiring_3days": "trial_expiring_3days.html",
        "trial_expiring_1day": "trial_expiring_1day.html",
        "trial_expired": "trial_expired.html",
        "payment_successful": "payment_successful.html",
        "payment_failed": "payment_failed.html",
        "subscription_created": "subscription_created.html",
        "subscription_updated": "subscription_updated.html",
        "subscription_cancelled": "subscription_cancelled.html",
        "invoice": "invoice.html"
    }
    
    # Email subjects
    SUBJECTS = {
        "trial_activated": "Welcome to AUTOOS - Your 30-Day Free Trial is Active!",
        "trial_expiring_7days": "Your AUTOOS Free Trial Expires in 7 Days",
        "trial_expiring_3days": "Your AUTOOS Free Trial Expires in 3 Days",
        "trial_expiring_1day": "Last Day of Your AUTOOS Free Trial!",
        "trial_expired": "Your AUTOOS Free Trial Has Ended",
        "payment_successful": "Payment Successful - AUTOOS Subscription",
        "payment_failed": "Payment Failed - AUTOOS Subscription",
        "subscription_created": "Welcome to AUTOOS {tier}!",
        "subscription_updated": "Your AUTOOS Subscription Has Been Updated",
        "subscription_cancelled": "Your AUTOOS Subscription Has Been Cancelled",
        "invoice": "Your AUTOOS Invoice for {month}"
    }


# ============================================================================
# Feature Flags
# ============================================================================

class FeatureFlags:
    """Feature flags for payment system"""
    
    ENABLE_FREE_TRIAL = os.getenv("ENABLE_FREE_TRIAL", "true").lower() == "true"
    ENABLE_UPI_PAYMENTS = os.getenv("ENABLE_UPI_PAYMENTS", "true").lower() == "true"
    ENABLE_CARD_PAYMENTS = os.getenv("ENABLE_CARD_PAYMENTS", "true").lower() == "true"
    ENABLE_ANNUAL_BILLING = os.getenv("ENABLE_ANNUAL_BILLING", "true").lower() == "true"
    ENABLE_PRORATION = os.getenv("ENABLE_PRORATION", "true").lower() == "true"
    ENABLE_TRIAL_REMINDERS = os.getenv("ENABLE_TRIAL_REMINDERS", "true").lower() == "true"


# ============================================================================
# Export Configuration
# ============================================================================

__all__ = [
    "UPIConfig",
    "StripeConfig",
    "SubscriptionTiers",
    "SubscriptionTierConfig",
    "PaymentMethodConfig",
    "CurrencyConfig",
    "EmailConfig",
    "FeatureFlags"
]
