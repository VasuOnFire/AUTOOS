# 💳 AUTOOS Payment Setup Guide

Complete guide for setting up payments with UPI (India) and Stripe (International).

---

## 🇮🇳 UPI Payment Setup (India)

### Your UPI Details

**UPI ID**: `vasu7993457842@axl`  
**Merchant Name**: AUTOOS  
**Supported Apps**: PhonePe, Google Pay, Paytm, BHIM, Amazon Pay, WhatsApp Pay

### How It Works

1. **User selects subscription tier**
2. **System generates QR code** with your UPI ID
3. **User scans QR code** with any UPI app
4. **Payment goes directly to** `vasu7993457842@axl`
5. **System verifies payment** and activates subscription

### Test QR Code Generation

```bash
# Run test script
python scripts/test_qr_payment.py

# This will:
# - Generate QR code with your UPI ID
# - Save QR code as test_qr_code.png
# - Show UPI string and deep links
# - Test different subscription amounts
```

### QR Code Example

For a ₹99.99 Professional subscription, the UPI string will be:

```
upi://pay?pa=vasu7993457842@axl&pn=AUTOOS&am=99.99&cu=INR&tn=AUTOOS Professional Subscription&tr=qr_abc123def456
```

### Configuration

The UPI ID is configured in multiple places:

**1. Environment Variable** (`.env`):
```bash
UPI_ID=vasu7993457842@axl
UPI_MERCHANT_NAME=AUTOOS
```

**2. Code Default** (`src/autoos/payment/qr_payment.py`):
```python
class QRPaymentService:
    def __init__(self, merchant_vpa: str = "vasu7993457842@axl", ...):
```

**3. Configuration File** (`src/autoos/payment/config.py`):
```python
class UPIConfig:
    DEFAULT_UPI_ID = "vasu7993457842@axl"
    MERCHANT_NAME = "AUTOOS"
```

### Pricing in INR

| Tier | Monthly | Annual |
|------|---------|--------|
| Free Trial | ₹0 | ₹0 |
| Student | ₹799 | ₹7,999 |
| Employee | ₹2,399 | ₹23,999 |
| Professional | ₹7,999 | ₹79,999 |
| Enterprise | Custom | Custom |

---

## 💳 Stripe Setup (International)

### Get Stripe API Keys

1. **Create Stripe Account**: https://stripe.com
2. **Get API Keys**: Dashboard → Developers → API keys
3. **Get Webhook Secret**: Dashboard → Developers → Webhooks

### Configure Stripe

Add to `.env`:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### Set Up Webhook

1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter URL: `https://your-domain.com/webhooks/stripe`
4. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy webhook secret to `.env`

### Pricing in USD

| Tier | Monthly | Annual |
|------|---------|--------|
| Free Trial | $0 | $0 |
| Student | $9.99 | $99.99 |
| Employee | $29.99 | $299.99 |
| Professional | $99.99 | $999.99 |
| Enterprise | Custom | Custom |

---

## 🎯 Payment Flow

### Free Trial Flow (No Payment)

```
1. User signs up
2. User clicks "Start Free Trial"
3. System activates trial:
   - 30 days duration
   - 10 workflow credits
   - 2 concurrent agents
4. No payment required!
5. User can upgrade anytime
```

### UPI Payment Flow (India)

```
1. User selects subscription tier
2. User clicks "Pay with UPI"
3. System generates QR code with vasu7993457842@axl
4. User scans QR code with PhonePe/GPay/Paytm
5. User completes payment in UPI app
6. Payment goes to vasu7993457842@axl
7. System verifies payment (via webhook or polling)
8. System activates subscription
9. User receives confirmation email
```

### Card Payment Flow (International)

```
1. User selects subscription tier
2. User clicks "Pay with Card"
3. Stripe checkout opens
4. User enters card details
5. Stripe processes payment
6. Stripe sends webhook to your server
7. System activates subscription
8. User receives confirmation email
```

---

## 🔧 Implementation Status

### ✅ Completed

- [x] UPI ID configured (`vasu7993457842@axl`)
- [x] QR code generation service
- [x] Free trial service
- [x] Subscription tier configuration
- [x] Payment models (database)
- [x] Test script for QR generation

### 🔄 To Implement

- [ ] Payment API endpoints
- [ ] Stripe integration
- [ ] Payment verification webhook
- [ ] Frontend payment components
- [ ] Email notifications
- [ ] Invoice generation

**Estimated Time**: 6-8 hours

---

## 📱 Frontend Integration

### QR Code Display Component

```tsx
// frontend/web/src/components/payment/QRCodePayment.tsx
import { useState, useEffect } from 'react';

export function QRCodePayment({ amount, tier }) {
  const [qrCode, setQrCode] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState('pending');
  
  useEffect(() => {
    // Generate QR code
    fetch('/api/payments/qr-code', {
      method: 'POST',
      body: JSON.stringify({ amount, tier })
    })
    .then(res => res.json())
    .then(data => {
      setQrCode(data.qr_code);
      // Poll for payment status
      checkPaymentStatus(data.payment_id);
    });
  }, [amount, tier]);
  
  return (
    <div className="qr-payment">
      <h3>Scan to Pay ₹{amount}</h3>
      <img src={qrCode} alt="UPI QR Code" />
      <p>Scan with any UPI app</p>
      <div className="upi-apps">
        <img src="/icons/phonepe.png" alt="PhonePe" />
        <img src="/icons/googlepay.png" alt="Google Pay" />
        <img src="/icons/paytm.png" alt="Paytm" />
      </div>
      <p>Payment to: vasu7993457842@axl</p>
      {paymentStatus === 'completed' && (
        <div className="success">✅ Payment Successful!</div>
      )}
    </div>
  );
}
```

---

## 🧪 Testing

### Test QR Code Generation

```bash
# Generate test QR code
python scripts/test_qr_payment.py

# Output:
# - test_qr_code.png (scan with UPI app)
# - UPI string
# - Deep links for PhonePe, GPay, Paytm
```

### Test Payment Flow

```bash
# 1. Start backend
docker-compose up -d

# 2. Generate QR code
curl -X POST http://localhost:8000/payments/qr-code \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "amount": 99.99,
    "description": "Test Payment"
  }'

# 3. Scan QR code with UPI app
# 4. Complete payment to vasu7993457842@axl
# 5. Verify payment status
curl http://localhost:8000/payments/qr-code/{payment_id}/status
```

---

## 💰 Revenue Tracking

### Payment Destinations

**UPI Payments (India)**: → `vasu7993457842@axl`  
**Card Payments (International)**: → Stripe account → Your bank

### Expected Revenue

Based on pricing:

| Tier | Monthly | 100 Users/Month | 1000 Users/Month |
|------|---------|-----------------|------------------|
| Student | ₹799 | ₹79,900 | ₹7,99,000 |
| Employee | ₹2,399 | ₹2,39,900 | ₹23,99,000 |
| Professional | ₹7,999 | ₹7,99,900 | ₹79,99,000 |

### Payment Verification

You'll receive payments directly to `vasu7993457842@axl`. To verify:

1. **Check UPI app** for incoming payments
2. **Match transaction ID** with payment_id in database
3. **Activate subscription** for user
4. **Send confirmation email**

---

## 🔐 Security

### UPI Security

- ✅ QR codes expire after 15 minutes
- ✅ Unique transaction ID for each payment
- ✅ Payment verification before activation
- ✅ No sensitive data stored

### Stripe Security

- ✅ PCI DSS compliant (Stripe handles cards)
- ✅ 3D Secure authentication
- ✅ Webhook signature verification
- ✅ Encrypted communication

---

## 📧 Email Notifications

### Payment Emails

**Trial Activated**:
```
Subject: Welcome to AUTOOS - Your 30-Day Free Trial is Active!
Body: Your free trial includes 10 workflows, 2 agents, and 10 credits.
```

**Payment Successful**:
```
Subject: Payment Successful - AUTOOS Subscription
Body: Your payment of ₹99.99 to vasu7993457842@axl was successful.
      Your Professional subscription is now active!
```

**Trial Expiring**:
```
Subject: Your AUTOOS Free Trial Expires in 3 Days
Body: Upgrade now to continue using AUTOOS without interruption.
```

---

## 🆘 Troubleshooting

### QR Code Not Generating

```bash
# Check if qrcode library is installed
pip install qrcode[pil]

# Test generation
python scripts/test_qr_payment.py
```

### Payment Not Verified

1. Check UPI app for payment confirmation
2. Verify transaction ID matches payment_id
3. Check webhook logs for errors
4. Manually verify and activate if needed

### Stripe Webhook Not Working

1. Verify webhook URL is correct
2. Check webhook secret in `.env`
3. Test webhook with Stripe CLI:
```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```

---

## 📞 Support

### For Payment Issues

- **UPI Issues**: Check `vasu7993457842@axl` transaction history
- **Stripe Issues**: Check Stripe dashboard
- **Technical Issues**: Check application logs

### Contact

- **Email**: support@autoos.ai
- **UPI ID**: vasu7993457842@axl
- **Documentation**: See all `*.md` files

---

## ✅ Quick Checklist

- [ ] UPI ID configured (`vasu7993457842@axl`)
- [ ] Test QR code generation works
- [ ] Stripe account created
- [ ] Stripe API keys added to `.env`
- [ ] Webhook endpoint configured
- [ ] Payment API endpoints implemented
- [ ] Frontend payment components created
- [ ] Email notifications set up
- [ ] Test payment flow end-to-end
- [ ] Monitor first real payment

---

**Your UPI ID `vasu7993457842@axl` is now configured and ready to receive payments!** 🎉

*Last Updated: February 8, 2026*
