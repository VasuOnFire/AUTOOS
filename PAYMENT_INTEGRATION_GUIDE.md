# AUTOOS Payment Integration Guide

## Overview

AUTOOS supports two payment methods:
1. **Stripe** - For card payments and international subscriptions
2. **QR Code/UPI** - For Indian market (PhonePe, Google Pay, Paytm, etc.)

## Table of Contents

- [Setup](#setup)
- [Pricing Tiers](#pricing-tiers)
- [Free Trial](#free-trial)
- [Stripe Integration](#stripe-integration)
- [QR Code/UPI Payments](#qr-codeupi-payments)
- [Subscription Management](#subscription-management)
- [Webhooks](#webhooks)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)

## Setup

### Environment Variables

Add the following to your `.env` file:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# UPI Configuration
UPI_MERCHANT_ID=AUTOOS
UPI_DEFAULT_VPA=vasu7993457842@axl

# Feature Flags
ENABLE_FREE_TRIAL=true
ENABLE_UPI_PAYMENTS=true
ENABLE_CARD_PAYMENTS=true
ENABLE_ANNUAL_BILLING=true
ENABLE_PRORATION=true
ENABLE_TRIAL_REMINDERS=true
```

### Install Dependencies

```bash
pip install stripe==8.0.0 qrcode[pil]==7.4.2
```

## Pricing Tiers

### Free Trial
- **Duration**: 30 days
- **Workflows**: 10 per month
- **Agents**: 2 concurrent
- **Credits**: 10 workflow credits
- **Cost**: $0 (No credit card required)

### Student Plan
- **Price**: $9.99/month or $99.99/year
- **Price (INR)**: ₹799/month or ₹7,999/year
- **Workflows**: 100 per month
- **Agents**: 5 concurrent
- **Features**: All core features, email support

### Employee Plan (Recommended)
- **Price**: $29.99/month or $299.99/year
- **Price (INR)**: ₹2,399/month or ₹23,999/year
- **Workflows**: 500 per month
- **Agents**: 20 concurrent
- **Features**: Team collaboration, priority support

### Professional Plan
- **Price**: $99.99/month or $999.99/year
- **Price (INR)**: ₹7,999/month or ₹79,999/year
- **Workflows**: Unlimited
- **Agents**: 100 concurrent
- **Features**: Advanced analytics, custom integrations, 24/7 support

### Enterprise Plan
- **Price**: Custom pricing
- **Workflows**: Unlimited
- **Agents**: Unlimited
- **Features**: Dedicated support, on-premise deployment, custom SLA

## Free Trial

### Starting a Free Trial

```python
from src.autoos.payment import FreeTrialService

trial_service = FreeTrialService()

# Start trial
trial_data = await trial_service.start_free_trial(user_id="user123")

# Returns:
# {
#     "user_id": "user123",
#     "trial_start_date": datetime,
#     "trial_end_date": datetime,
#     "credits_remaining": 10,
#     "workflows_used": 0,
#     "workflow_limit": 10,
#     "agent_limit": 2,
#     "is_active": True
# }
```

### Checking Trial Status

```python
# Check status
status = await trial_service.check_trial_status(user_id="user123")

# Returns:
# {
#     "is_active": True,
#     "days_remaining": 25,
#     "credits_remaining": 7,
#     "workflows_used": 3,
#     "workflow_limit": 10
# }
```

### Deducting Credits

```python
# Deduct credit when workflow is executed
success = await trial_service.deduct_credit(user_id="user123", amount=1)
```

### Trial Expiration

The system automatically:
- Sends reminder emails at 7, 3, and 1 day before expiration
- Expires trial after 30 days
- Sends trial expired notification
- Prompts user to upgrade to paid plan

## Stripe Integration

### Creating a Customer

```python
from src.autoos.payment import StripeService, StripeCustomerRequest

stripe_service = StripeService()

request = StripeCustomerRequest(
    user_id="user123",
    email="user@example.com",
    name="John Doe",
    metadata={"organization": "Acme Corp"}
)

customer = await stripe_service.create_customer(request)

# Returns:
# {
#     "customer_id": "cus_xxx",
#     "email": "user@example.com",
#     "name": "John Doe",
#     "created": 1234567890,
#     "metadata": {...}
# }
```

### Creating a Payment Intent (One-time Payment)

```python
from src.autoos.payment import StripePaymentIntentRequest

request = StripePaymentIntentRequest(
    user_id="user123",
    amount=99.99,
    currency="USD",
    description="AUTOOS Professional Plan - Monthly",
    customer_id="cus_xxx"
)

payment_intent = await stripe_service.create_payment_intent(request)

# Returns:
# {
#     "payment_intent_id": "pi_xxx",
#     "client_secret": "pi_xxx_secret_yyy",
#     "amount": 99.99,
#     "currency": "USD",
#     "status": "requires_payment_method"
# }
```

### Creating a Subscription

```python
from src.autoos.payment import StripeSubscriptionRequest
from src.autoos.core.models import SubscriptionTier

request = StripeSubscriptionRequest(
    user_id="user123",
    customer_id="cus_xxx",
    tier=SubscriptionTier.PROFESSIONAL,
    billing_cycle="monthly",  # or "annual"
    payment_method="pm_xxx"
)

subscription = await stripe_service.create_subscription(request)

# Returns:
# {
#     "subscription_id": "sub_xxx",
#     "customer_id": "cus_xxx",
#     "status": "active",
#     "current_period_start": datetime,
#     "current_period_end": datetime,
#     "tier": "professional",
#     "billing_cycle": "monthly",
#     "amount": 99.99,
#     "currency": "USD"
# }
```

### Cancelling a Subscription

```python
# Cancel at period end (recommended)
result = await stripe_service.cancel_subscription(
    subscription_id="sub_xxx",
    immediate=False
)

# Cancel immediately
result = await stripe_service.cancel_subscription(
    subscription_id="sub_xxx",
    immediate=True
)
```

## QR Code/UPI Payments

### Generating QR Code

```python
from src.autoos.payment import QRPaymentService, QRPaymentRequest, UPIProvider

qr_service = QRPaymentService()

request = QRPaymentRequest(
    user_id="user123",
    amount=799.00,
    currency="INR",
    description="AUTOOS Student Plan - Monthly",
    subscription_tier="student",
    upi_provider=UPIProvider.ANY  # Works with all UPI apps
)

qr_payment = await qr_service.create_qr_payment(request)

# Returns:
# {
#     "payment_id": "qr_xxx",
#     "qr_code": "data:image/png;base64,...",  # Base64 QR code image
#     "upi_string": "upi://pay?pa=vasu7993457842@axl&...",
#     "amount": 799.00,
#     "currency": "INR",
#     "status": "pending",
#     "expires_at": datetime,
#     "merchant_name": "AUTOOS",
#     "merchant_vpa": "vasu7993457842@axl"
# }
```

### Displaying QR Code

```html
<!-- In your frontend -->
<img src="{{ qr_payment.qr_code }}" alt="Scan to pay" />
<p>Scan with PhonePe, Google Pay, Paytm, or any UPI app</p>
<p>Amount: ₹{{ qr_payment.amount }}</p>
<p>Expires in: 15 minutes</p>
```

### Checking Payment Status

```python
# Poll every 3 seconds to check payment status
status = await qr_service.check_payment_status(payment_id="qr_xxx")

# Status can be: pending, processing, completed, failed, expired
```

### Deep Links for UPI Apps

```python
# Generate deep links for specific apps
phonepe_link = qr_service.generate_phonepe_deeplink(qr_payment.upi_string)
googlepay_link = qr_service.generate_googlepay_deeplink(qr_payment.upi_string)
paytm_link = qr_service.generate_paytm_deeplink(qr_payment.upi_string)

# Use these links for "Open in App" buttons
```

## Subscription Management

### Upgrading Subscription

```python
from src.autoos.payment import SubscriptionManager

manager = SubscriptionManager(stripe_service)

# Upgrade with proration
result = await manager.upgrade_subscription(
    subscription_id="sub_xxx",
    new_tier=SubscriptionTier.PROFESSIONAL,
    billing_cycle="monthly"
)

# User is charged prorated amount immediately
```

### Downgrading Subscription

```python
# Downgrade at period end (no immediate charge)
result = await manager.downgrade_subscription(
    subscription_id="sub_xxx",
    new_tier=SubscriptionTier.STUDENT,
    billing_cycle="monthly"
)

# Downgrade takes effect at end of current billing period
```

### Calculating Proration

```python
# Preview proration before upgrade
proration = await manager.calculate_proration(
    subscription_id="sub_xxx",
    new_tier=SubscriptionTier.PROFESSIONAL,
    billing_cycle="monthly"
)

# Returns:
# {
#     "current_tier": "student",
#     "new_tier": "professional",
#     "proration_amount": 75.00,
#     "next_invoice_amount": 99.99,
#     "next_invoice_date": datetime
# }
```

### Checking Usage Limits

```python
limits = await manager.check_subscription_limits(
    user_id="user123",
    tier=SubscriptionTier.STUDENT
)

# Returns:
# {
#     "workflows_limit": 100,
#     "workflows_used": 45,
#     "workflows_remaining": 55,
#     "agents_limit": 5,
#     "agents_used": 2,
#     "agents_remaining": 3,
#     "can_create_workflow": True,
#     "can_create_agent": True
# }
```

## Webhooks

### Setting Up Stripe Webhooks

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://your-domain.com/payments/webhooks/stripe`
3. Select events to listen for:
   - `payment_intent.succeeded`
   - `payment_intent.failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy webhook signing secret to `.env`

### Webhook Handler

The webhook handler automatically processes events:

```python
from src.autoos.payment import StripeWebhookHandler

handler = StripeWebhookHandler(stripe_service)

# Verify and handle webhook
event = await stripe_service.verify_webhook_signature(payload, signature)
result = await handler.handle_webhook(event)
```

### Supported Events

- **payment_intent.succeeded**: Payment completed successfully
- **payment_intent.failed**: Payment failed
- **customer.subscription.created**: New subscription created
- **customer.subscription.updated**: Subscription modified
- **customer.subscription.deleted**: Subscription cancelled
- **invoice.payment_succeeded**: Recurring payment succeeded
- **invoice.payment_failed**: Recurring payment failed

## API Endpoints

### Pricing

```
GET /payments/pricing
```

Returns all pricing tiers with details.

### Free Trial

```
POST /payments/start-trial
Body: { "user_id": "user123" }
```

```
GET /payments/trial-status?user_id=user123
```

### Stripe Payments

```
POST /payments/create-customer
Body: { "user_id": "user123", "email": "...", "name": "..." }
```

```
POST /payments/create-intent
Body: { "user_id": "user123", "amount": 99.99, "currency": "USD", ... }
```

```
POST /payments/subscribe
Body: { "user_id": "user123", "customer_id": "cus_xxx", "tier": "professional", ... }
```

### QR Code Payments

```
POST /payments/qr-code
Body: { "user_id": "user123", "amount": 799.00, "currency": "INR", ... }
```

```
GET /payments/qr-code/{payment_id}/status
```

### Subscription Management

```
GET /payments/subscription?subscription_id=sub_xxx
```

```
POST /payments/cancel-subscription
Body: { "subscription_id": "sub_xxx", "immediate": false }
```

```
POST /payments/upgrade
Body: { "subscription_id": "sub_xxx", "new_tier": "professional", ... }
```

```
POST /payments/downgrade
Body: { "subscription_id": "sub_xxx", "new_tier": "student", ... }
```

```
GET /payments/proration-preview?subscription_id=sub_xxx&new_tier=professional
```

### Usage and Limits

```
GET /payments/usage?user_id=user123
```

### Payment Methods

```
POST /payments/update-payment-method
Body: { "customer_id": "cus_xxx", "payment_method_id": "pm_xxx" }
```

```
GET /payments/payment-methods?customer_id=cus_xxx
```

### Billing History

```
GET /payments/history?user_id=user123&limit=10
```

```
GET /payments/invoices?user_id=user123&limit=10
```

```
GET /payments/invoices/{invoice_id}/download
```

### Webhooks

```
POST /payments/webhooks/stripe
Headers: { "stripe-signature": "..." }
Body: <raw webhook payload>
```

## Testing

### Running Tests

```bash
# Run all payment tests
pytest src/autoos/payment/test_payment_service.py -v

# Run specific test class
pytest src/autoos/payment/test_payment_service.py::TestStripeService -v

# Run with coverage
pytest src/autoos/payment/test_payment_service.py --cov=src/autoos/payment
```

### Test Stripe Cards

Use these test cards in Stripe test mode:

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Insufficient funds**: `4000 0000 0000 9995`
- **3D Secure**: `4000 0025 0000 3155`

### Testing QR Payments

In test mode, QR payments will generate valid QR codes but won't actually charge. You can:

1. Generate QR code
2. Manually mark payment as completed in database
3. Test payment status polling

### Testing Webhooks

Use Stripe CLI to test webhooks locally:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/payments/webhooks/stripe

# Trigger test events
stripe trigger payment_intent.succeeded
stripe trigger customer.subscription.created
```

## Best Practices

### Security

1. **Never expose secret keys** in frontend code
2. **Always verify webhook signatures** before processing
3. **Use HTTPS** for all payment endpoints
4. **Store customer IDs** securely in your database
5. **Encrypt sensitive data** at rest

### User Experience

1. **Show clear pricing** with all features listed
2. **Highlight free trial** prominently (no credit card required)
3. **Display usage limits** and remaining credits
4. **Send reminder emails** before trial expiration
5. **Make upgrade process** simple and clear
6. **Support both payment methods** (card and UPI) for Indian users

### Error Handling

1. **Handle Stripe errors** gracefully with user-friendly messages
2. **Retry failed payments** with exponential backoff
3. **Log all payment events** for debugging
4. **Monitor webhook failures** and retry if needed
5. **Alert on critical failures** (e.g., subscription cancellations)

### Performance

1. **Cache pricing tiers** to reduce API calls
2. **Use webhooks** instead of polling for payment status
3. **Implement rate limiting** on payment endpoints
4. **Queue webhook processing** for high volume
5. **Monitor payment latency** and optimize slow endpoints

## Troubleshooting

### Common Issues

**Issue**: Stripe API key not working
- **Solution**: Check that you're using the correct key for your environment (test vs. live)

**Issue**: Webhook signature verification fails
- **Solution**: Ensure you're using the raw request body, not parsed JSON

**Issue**: QR code not displaying
- **Solution**: Check that the base64 string is properly formatted with data URI prefix

**Issue**: Payment status stuck on pending
- **Solution**: Implement proper polling with timeout and expiration handling

**Issue**: Proration calculation incorrect
- **Solution**: Ensure subscription is active and has valid billing cycle

### Support

For payment-related issues:
1. Check logs for error messages
2. Verify environment variables are set correctly
3. Test with Stripe test mode first
4. Contact Stripe support for API issues
5. Check webhook event logs in Stripe Dashboard

## Additional Resources

- [Stripe API Documentation](https://stripe.com/docs/api)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [UPI Payment Specification](https://www.npci.org.in/what-we-do/upi/product-overview)
- [PhonePe Integration](https://developer.phonepe.com/)
- [AUTOOS Documentation](./README.md)
