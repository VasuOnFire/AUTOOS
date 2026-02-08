# 🔑 AUTOOS Access Code System

## Overview

AUTOOS uses an **access code system** where users receive a unique code after payment to access the application. When their subscription expires, they need to pay again to receive a new access code.

---

## 🔄 How It Works

### Complete Flow

```
1. User Pays → 2. Receives Access Code → 3. Uses App → 4. Subscription Expires → 5. Pay Again (Repeat)
```

### Detailed Process

#### Step 1: User Makes Payment

```
User selects subscription tier (Student/Employee/Professional)
↓
User pays via UPI (vasu7993457842@axl) or Card (Stripe)
↓
Payment verified
↓
System generates unique access code
```

#### Step 2: User Receives Access Code

```
Access Code Generated: AUTOOS-A7B9-C2D4-E6F8-G1H3
↓
Sent via Email
↓
Displayed on payment success page
↓
Saved in user dashboard
```

#### Step 3: User Enters Access Code

```
User opens AUTOOS app
↓
Enters access code: AUTOOS-A7B9-C2D4-E6F8-G1H3
↓
System verifies code
↓
Access granted for subscription period (30 days)
```

#### Step 4: Subscription Period

```
User has full access to AUTOOS
↓
Can use workflows, agents, all features
↓
System tracks usage and expiration
↓
Sends reminders at 7, 3, 1 day before expiration
```

#### Step 5: Subscription Expires

```
30 days pass
↓
Access code expires
↓
User can no longer access app
↓
Email sent: "Your subscription has expired"
↓
Renewal link provided
```

#### Step 6: User Renews (Pays Again)

```
User clicks renewal link
↓
Makes payment again
↓
Receives NEW access code: AUTOOS-X1Y2-Z3A4-B5C6-D7E8
↓
Old code is revoked
↓
Process repeats from Step 3
```

---

## 🎫 Access Code Format

### Structure

```
AUTOOS-XXXX-XXXX-XXXX-XXXX
```

### Example Codes

```
AUTOOS-A7B9-C2D4-E6F8-G1H3  (Student)
AUTOOS-K4L6-M8N2-P5Q7-R9S1  (Employee)
AUTOOS-T3U5-V7W9-X1Y3-Z5A7  (Professional)
```

### Properties

- **Length**: 16 characters + 5 hyphens
- **Characters**: Uppercase letters (A-Z) and digits (0-9)
- **Unique**: Each code is unique and can only be used by one user
- **Secure**: Generated using cryptographically secure random generator
- **One-time**: Each payment generates a new code

---

## 💳 Payment to Access Code Flow

### After UPI Payment (India)

```python
# 1. User scans QR code and pays ₹799 to vasu7993457842@axl
# 2. Payment webhook received
# 3. System verifies payment
# 4. Generate access code

from src.autoos.auth.access_code import AccessCodeGenerator

code_gen = AccessCodeGenerator()
access_code = code_gen.create_access_code(
    user_id="user_123",
    subscription_tier="student",
    payment_id="pay_upi_abc123",
    duration_days=30
)

# 5. Send email with access code
print(f"Your Access Code: {access_code.code}")
print(f"Valid until: {access_code.expires_at}")
```

### After Card Payment (Stripe)

```python
# 1. User enters card details on Stripe checkout
# 2. Stripe processes payment
# 3. Webhook received from Stripe
# 4. Generate access code

access_code = code_gen.create_access_code(
    user_id="user_456",
    subscription_tier="professional",
    payment_id="pay_stripe_xyz789",
    duration_days=30
)

# 5. Send email with access code
```

---

## 🔐 Access Code Verification

### When User Enters Code

```python
from src.autoos.auth.access_code import AccessCodeGenerator

code_gen = AccessCodeGenerator()

# User enters: AUTOOS-A7B9-C2D4-E6F8-G1H3
verification = code_gen.verify_access_code("AUTOOS-A7B9-C2D4-E6F8-G1H3")

if verification["valid"]:
    print("✅ Access Granted!")
    print(f"Subscription: {verification['subscription_tier']}")
    print(f"Days Remaining: {verification['days_remaining']}")
    # Allow user to access app
else:
    print("❌ Access Denied!")
    print(f"Reason: {verification['reason']}")
    # Show renewal page
```

### Verification Responses

**Valid Code**:
```json
{
  "valid": true,
  "user_id": "user_123",
  "subscription_tier": "professional",
  "expires_at": "2026-03-10T12:00:00Z",
  "days_remaining": 25,
  "status": "active"
}
```

**Expired Code**:
```json
{
  "valid": false,
  "reason": "Access code has expired",
  "status": "expired",
  "expired_at": "2026-02-08T12:00:00Z",
  "subscription_tier": "professional"
}
```

**Invalid Code**:
```json
{
  "valid": false,
  "reason": "Invalid access code",
  "status": "invalid"
}
```

---

## 📧 Email Notifications

### 1. Payment Success Email

```
Subject: Your AUTOOS Access Code

Hi [User Name],

Thank you for subscribing to AUTOOS Professional!

Your Access Code: AUTOOS-A7B9-C2D4-E6F8-G1H3

Subscription Details:
- Tier: Professional
- Duration: 30 days
- Expires: March 10, 2026
- Amount Paid: ₹7,999

How to Use:
1. Open AUTOOS app
2. Enter your access code
3. Start using all features!

Keep this code safe. You'll need it to access AUTOOS.

Questions? Reply to this email.

Best regards,
AUTOOS Team
```

### 2. Expiration Reminder (7 days)

```
Subject: Your AUTOOS Subscription Expires in 7 Days

Hi [User Name],

Your AUTOOS subscription expires in 7 days.

Current Access Code: AUTOOS-A7B9-C2D4-E6F8-G1H3
Expires: March 10, 2026

Renew now to continue using AUTOOS without interruption:
[Renew Subscription Button]

After expiration, you'll need to pay again to receive a new access code.

Best regards,
AUTOOS Team
```

### 3. Subscription Expired Email

```
Subject: Your AUTOOS Subscription Has Expired

Hi [User Name],

Your AUTOOS subscription has expired.

Previous Access Code: AUTOOS-A7B9-C2D4-E6F8-G1H3
Expired: March 10, 2026

To continue using AUTOOS, please renew your subscription:
[Renew Now Button]

After payment, you'll receive a new access code.

Pricing:
- Student: ₹799/month
- Employee: ₹2,399/month
- Professional: ₹7,999/month

Best regards,
AUTOOS Team
```

### 4. Renewal Success Email

```
Subject: Your AUTOOS Subscription Has Been Renewed

Hi [User Name],

Your subscription has been renewed successfully!

New Access Code: AUTOOS-X1Y2-Z3A4-B5C6-D7E8

Subscription Details:
- Tier: Professional
- Duration: 30 days
- Expires: April 10, 2026
- Amount Paid: ₹7,999

Your previous access code has been revoked.
Please use the new code to access AUTOOS.

Best regards,
AUTOOS Team
```

---

## 🖥️ Frontend Implementation

### Access Code Entry Screen

```tsx
// frontend/web/src/components/auth/AccessCodeEntry.tsx

import { useState } from 'react';

export function AccessCodeEntry() {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/verify-access-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });

      const data = await response.json();

      if (data.valid) {
        // Store access token
        localStorage.setItem('access_token', data.token);
        // Redirect to dashboard
        window.location.href = '/dashboard';
      } else {
        setError(data.reason);
      }
    } catch (err) {
      setError('Failed to verify access code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="access-code-entry">
      <h2>Enter Your Access Code</h2>
      <p>Enter the code you received after payment</p>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder="AUTOOS-XXXX-XXXX-XXXX-XXXX"
          maxLength={29}
          pattern="AUTOOS-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}"
          required
        />
        
        <button type="submit" disabled={loading}>
          {loading ? 'Verifying...' : 'Access AUTOOS'}
        </button>
        
        {error && <div className="error">{error}</div>}
      </form>
      
      <div className="help-links">
        <a href="/payments/subscribe">Don't have a code? Subscribe now</a>
        <a href="/support">Lost your code? Contact support</a>
      </div>
    </div>
  );
}
```

### Subscription Status Display

```tsx
// frontend/web/src/components/SubscriptionStatus.tsx

export function SubscriptionStatus({ user }) {
  const daysRemaining = calculateDaysRemaining(user.expires_at);
  const isExpiringSoon = daysRemaining <= 7;

  return (
    <div className={`subscription-status ${isExpiringSoon ? 'warning' : ''}`}>
      <h3>Your Subscription</h3>
      
      <div className="code-display">
        <label>Access Code:</label>
        <code>{user.access_code}</code>
        <button onClick={() => copyToClipboard(user.access_code)}>
          Copy
        </button>
      </div>
      
      <div className="expiration">
        <label>Expires:</label>
        <span>{formatDate(user.expires_at)}</span>
        <span className="days-remaining">
          {daysRemaining} days remaining
        </span>
      </div>
      
      {isExpiringSoon && (
        <div className="renewal-prompt">
          <p>⚠️ Your subscription expires soon!</p>
          <button onClick={() => window.location.href = '/payments/renew'}>
            Renew Now
          </button>
        </div>
      )}
      
      <div className="tier-info">
        <label>Tier:</label>
        <span>{user.subscription_tier}</span>
      </div>
    </div>
  );
}
```

---

## 🔄 Renewal Process

### Automatic Renewal (Optional)

```python
# Check for expiring subscriptions daily
from src.autoos.auth.access_code import SubscriptionRenewalService

renewal_service = SubscriptionRenewalService()

# Get users expiring in 1 day
expiring_users = get_users_expiring_in_days(1)

for user in expiring_users:
    # Send final reminder
    send_expiration_reminder(user.email, days_remaining=1)
    
# Get expired users
expired_users = get_expired_users()

for user in expired_users:
    # Handle expiration
    renewal_service.handle_expired_subscription(user.user_id)
    
    # Send expiration email with renewal link
    send_expiration_email(user.email)
```

### Manual Renewal

```python
# User clicks "Renew" button
# User makes payment
# After payment verification:

renewal_result = renewal_service.renew_subscription(
    user_id=user.user_id,
    subscription_tier=user.subscription_tier,
    payment_id=new_payment_id
)

# Send email with new access code
send_renewal_email(
    user.email,
    new_code=renewal_result['access_code'],
    expires_at=renewal_result['expires_at']
)
```

---

## 📊 Database Schema

### Access Codes Table

```sql
CREATE TABLE access_codes (
    code_id VARCHAR(36) PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    user_id VARCHAR(36) NOT NULL,
    subscription_tier VARCHAR(50) NOT NULL,
    payment_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    revoked_at TIMESTAMP,
    revocation_reason TEXT,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id),
    
    INDEX idx_code (code),
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_expires (expires_at)
);
```

---

## 🧪 Testing

### Test Access Code Generation

```bash
# Run test script
python src/autoos/auth/access_code.py

# Output:
# ✅ Payment Successful!
# Access Code: AUTOOS-A7B9-C2D4-E6F8-G1H3
# Tier: professional
# Expires: 2026-03-10 12:00:00
# Duration: 30 days
```

### Test Complete Flow

```python
from src.autoos.auth.access_code import AccessCodeGenerator, SubscriptionRenewalService

# 1. User pays
code_gen = AccessCodeGenerator()
access_code = code_gen.create_access_code(
    user_id="test_user",
    subscription_tier="professional",
    payment_id="pay_test_123",
    duration_days=30
)
print(f"Access Code: {access_code.code}")

# 2. User enters code
verification = code_gen.verify_access_code(access_code.code)
assert verification["valid"] == True

# 3. Subscription expires (simulate)
# ... 30 days pass ...

# 4. User renews
renewal_service = SubscriptionRenewalService()
renewal = renewal_service.renew_subscription(
    user_id="test_user",
    subscription_tier="professional",
    payment_id="pay_test_456"
)
print(f"New Access Code: {renewal['access_code']}")
```

---

## 💡 Benefits of Access Code System

### For Users
✅ Simple - Just one code to remember  
✅ Secure - Unique code per user  
✅ Clear - Know exactly when subscription expires  
✅ Flexible - Easy to share with team (Enterprise)  

### For You (Business Owner)
✅ Payment Tracking - Each code linked to payment  
✅ Access Control - Revoke codes anytime  
✅ Revenue Predictable - Monthly recurring payments  
✅ Simple Implementation - No complex auth flows  

---

## 🔐 Security Features

1. **Unique Codes**: Each code is cryptographically unique
2. **One User Per Code**: Code can only be used by one user
3. **Expiration**: Codes automatically expire after subscription period
4. **Revocation**: Codes can be manually revoked if needed
5. **Usage Tracking**: Track when and how often code is used
6. **Payment Verification**: Code only generated after verified payment

---

## 📞 Support

### Common Issues

**Q: I lost my access code**  
A: Check your email or login to dashboard to view your code

**Q: My code doesn't work**  
A: Check if it's expired. If yes, renew subscription for new code

**Q: Can I share my code?**  
A: No, each code is for one user only (except Enterprise tier)

**Q: How do I renew?**  
A: Click renewal link in email or visit /payments/renew

---

**Your access code system is ready!** 🎉

Users will receive codes after payment to `vasu7993457842@axl` and can use them to access AUTOOS for their subscription period.

*Last Updated: February 8, 2026*
