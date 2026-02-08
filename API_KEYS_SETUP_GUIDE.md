# API Keys Setup Guide for AUTOOS Omega

This guide will walk you through getting all the required API keys for deploying AUTOOS Omega.

---

## 1. 🔑 STRIPE_SECRET_KEY (Required for Payments)

Stripe is used for payment processing in AUTOOS Omega.

### Steps to Get Stripe Secret Key:

1. **Go to Stripe Dashboard**
   - Visit: https://dashboard.stripe.com/register
   - Sign up for a free account (no credit card required for testing)

2. **Complete Account Setup**
   - Fill in your business details
   - Verify your email address

3. **Get Your API Keys**
   - After login, go to: https://dashboard.stripe.com/test/apikeys
   - You'll see two keys:
     - **Publishable key** (starts with `pk_test_...`)
     - **Secret key** (starts with `sk_test_...`) ← **This is what you need!**
   - Click "Reveal test key" to see the secret key
   - Copy the **Secret key** (sk_test_...)

4. **Important Notes**
   - Start with **Test Mode** keys (they have `test` in them)
   - Test mode is FREE and perfect for development
   - You can process test payments without real money
   - Switch to **Live Mode** later when you're ready to accept real payments

**Example Format:**
```
sk_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
(Your actual key will be much longer - about 100+ characters)
```

---

## 2. 🔐 STRIPE_WEBHOOK_SECRET (Required for Payment Events)

Webhook secret is used to verify that payment events are actually from Stripe.

### Steps to Get Stripe Webhook Secret:

**IMPORTANT:** You need to set this up AFTER deploying to Render (because you need your backend URL).

#### Initial Deployment (Use Placeholder):
For your first deployment, use this placeholder:
```
whsec_placeholder_will_update_after_deployment
```

#### After Deployment (Get Real Webhook Secret):

1. **Deploy to Render First**
   - Complete your Render deployment
   - Get your backend URL (e.g., `https://autoos-backend.onrender.com`)

2. **Go to Stripe Webhooks**
   - Visit: https://dashboard.stripe.com/test/webhooks
   - Click "Add endpoint"

3. **Configure Webhook**
   - **Endpoint URL:** `https://your-backend-url.onrender.com/api/payment/webhook`
   - Example: `https://autoos-backend.onrender.com/api/payment/webhook`
   
4. **Select Events to Listen**
   - Click "Select events"
   - Choose these events:
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.paid`
     - `invoice.payment_failed`

5. **Get Webhook Secret**
   - Click "Add endpoint"
   - You'll see your webhook listed
   - Click on the webhook
   - Click "Reveal" under "Signing secret"
   - Copy the secret (starts with `whsec_...`)

6. **Update Render Environment Variable**
   - Go to your Render dashboard
   - Select your backend service
   - Go to "Environment" tab
   - Update `STRIPE_WEBHOOK_SECRET` with the real value
   - Save changes (service will auto-redeploy)

**Example Format:**
```
whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
(Your actual webhook secret will be about 60+ characters)
```

---

## 3. 🤖 OPENAI_API_KEY (Optional - For AI Features)

OpenAI API is used for the AI agent capabilities in AUTOOS Omega.

### Steps to Get OpenAI API Key:

1. **Go to OpenAI Platform**
   - Visit: https://platform.openai.com/signup
   - Sign up for an account

2. **Add Payment Method** (Required)
   - Go to: https://platform.openai.com/account/billing/overview
   - Click "Add payment method"
   - Add a credit/debit card
   - OpenAI charges pay-as-you-go (very affordable for testing)
   - New accounts get $5 free credits!

3. **Create API Key**
   - Go to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Give it a name (e.g., "AUTOOS Omega")
   - Copy the key immediately (you won't see it again!)
   - Key starts with `sk-...`

4. **Set Usage Limits** (Recommended)
   - Go to: https://platform.openai.com/account/limits
   - Set a monthly budget limit (e.g., $10/month)
   - This prevents unexpected charges

**Example Format:**
```
sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
(Your actual OpenAI key will be about 50+ characters)
```

### If You Don't Want to Use OpenAI (Optional):

You can deploy without OpenAI initially:
- Leave `OPENAI_API_KEY` empty or use: `sk-placeholder-no-ai-features`
- The app will work, but AI agent features will be disabled
- You can add it later when ready

---

## 📋 Quick Summary

### Required Keys:
1. **STRIPE_SECRET_KEY** - Get from https://dashboard.stripe.com/test/apikeys
2. **STRIPE_WEBHOOK_SECRET** - Use placeholder first, then get from https://dashboard.stripe.com/test/webhooks after deployment

### Optional Keys:
3. **OPENAI_API_KEY** - Get from https://platform.openai.com/api-keys (or skip for now)

---

## 🚀 Deployment Workflow

### Step 1: Initial Deployment
Use these values in Render:
```
STRIPE_SECRET_KEY=<paste your actual Stripe test key here>
STRIPE_WEBHOOK_SECRET=whsec_placeholder_update_after_deploy
OPENAI_API_KEY=<leave empty or add later>
```

### Step 2: After Deployment
1. Get your backend URL from Render
2. Set up Stripe webhook with that URL
3. Get the real webhook secret
4. Update `STRIPE_WEBHOOK_SECRET` in Render
5. (Optional) Add real OpenAI key when ready

---

## 💰 Cost Breakdown

### Stripe:
- **Free** for testing (test mode)
- Live mode: 2.9% + $0.30 per transaction
- No monthly fees

### OpenAI:
- **$5 free credits** for new accounts
- Pay-as-you-go after that
- Typical usage: $0.01 - $0.10 per AI request
- Set budget limits to control costs

### Render:
- **Free tier** available for all services
- PostgreSQL: Free for 90 days
- Redis: Free for 30 days

---

## 🔒 Security Best Practices

1. **Never commit API keys to Git**
   - Already handled in `.gitignore`
   - Only set keys in Render environment variables

2. **Use Test Keys First**
   - Always start with Stripe test keys
   - Switch to live keys only when ready for production

3. **Rotate Keys Regularly**
   - Change keys every 90 days
   - Immediately rotate if compromised

4. **Set Usage Limits**
   - Set OpenAI monthly budget
   - Monitor Stripe dashboard for unusual activity

---

## ❓ Troubleshooting

### "Invalid API Key" Error:
- Make sure you copied the entire key (they're long!)
- Check for extra spaces at the beginning or end
- Verify you're using the correct key type (secret key, not publishable key)

### Webhook Not Working:
- Verify your backend URL is correct
- Make sure URL ends with `/api/payment/webhook`
- Check that webhook secret starts with `whsec_`
- Look at Stripe webhook logs for errors

### OpenAI Rate Limit:
- Check your usage at https://platform.openai.com/account/usage
- Verify payment method is active
- Check if you've exceeded your budget limit

---

## 📞 Support Links

- **Stripe Support:** https://support.stripe.com
- **OpenAI Support:** https://help.openai.com
- **Render Support:** https://render.com/docs

---

## ✅ Ready to Deploy?

Once you have your keys:
1. Go to https://dashboard.render.com
2. Create a new Blueprint
3. Connect your GitHub repo: `VasuOnFire/AUTOOS`
4. Enter your API keys when prompted
5. Click "Apply" to deploy!

Your AUTOOS Omega will be live in 5-10 minutes! 🎉
