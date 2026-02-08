"""
AUTOOS Payment Module

Unified payment service supporting both Stripe (card payments) and QR code (UPI) payments.
"""

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
    QRPaymentResponse,
    PaymentStatus,
    UPIProvider
)
from src.autoos.payment.webhook_handler import StripeWebhookHandler
from src.autoos.payment.config import (
    StripeConfig,
    UPIConfig,
    SubscriptionTiers,
    SubscriptionTierConfig,
    PaymentMethodConfig,
    CurrencyConfig,
    EmailConfig,
    FeatureFlags
)

__all__ = [
    # Stripe services
    "StripeService",
    "SubscriptionManager",
    "StripeCustomerRequest",
    "StripePaymentIntentRequest",
    "StripeSubscriptionRequest",
    "StripeWebhookHandler",
    
    # QR payment services
    "QRPaymentService",
    "FreeTrialService",
    "QRPaymentRequest",
    "QRPaymentResponse",
    "PaymentStatus",
    "UPIProvider",
    
    # Configuration
    "StripeConfig",
    "UPIConfig",
    "SubscriptionTiers",
    "SubscriptionTierConfig",
    "PaymentMethodConfig",
    "CurrencyConfig",
    "EmailConfig",
    "FeatureFlags"
]
