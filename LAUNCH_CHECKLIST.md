# 🚀 AUTOOS Launch Checklist

Complete checklist for implementing Phase 9 (Authentication & Payment) and deploying AUTOOS to production.

## 📋 Table of Contents

1. [Phase 9 Implementation Status](#phase-9-implementation-status)
2. [Quick Deployment (Free Option)](#quick-deployment-free-option)
3. [Production Deployment](#production-deployment)
4. [Post-Deployment Checklist](#post-deployment-checklist)

---

## Phase 9 Implementation Status

### ✅ Completed

- [x] Database models (User, Subscription, Payment, OAuth)
- [x] Database schema (init-db.sql updated)
- [x] Core data models in models.py
- [x] Authentication service foundation
- [x] QR payment service foundation

### 🔄 In Progress / To Complete

Follow the tasks in `.kiro/specs/autoos-omega/tasks.md` Phase 9 (Tasks 30-42):

#### Task 30: Database Models ✅ DONE
- User, Subscription, Payment, OAuth models created
- SQLAlchemy ORM models defined
- Database migration scripts in init-db.sql

#### Task 31: Authentication API Endpoints
```bash
# Create authentication router
touch src/autoos/auth/router.py
```

Implement:
- POST /auth/signup
- POST /auth/signin
- POST /auth/signout
- POST /auth/refresh
- GET /auth/me
- POST /auth/verify-email
- POST /auth/forgot-password
- POST /auth/reset-password
- POST /auth/mfa/setup
- POST /auth/mfa/verify
- GET /auth/oauth/{provider}/authorize
- GET /auth/oauth/{provider}/callback

#### Task 32: Payment Service
```bash
# Expand payment service
# File already exists: src/autoos/payment/qr_payment.py
```

Add:
- Stripe SDK integration
- Subscription management
- Free trial logic
- QR code payment verification

#### Task 33: Payment API Endpoints
```bash
# Create payment router
touch src/autoos/payment/router.py
```

Implement:
- GET /payments/pricing
- POST /payments/subscribe
- POST /payments/qr-code
- GET /payments/qr-code/{payment_id}/status
- POST /payments/start-trial
- GET /payments/trial-status
- GET /payments/subscription
- POST /payments/cancel-subscription

#### Task 34-35: Frontend Components
```bash
cd frontend/web/src/components

# Create auth components
touch SignIn.tsx SignUp.tsx MFASetup.tsx UserProfile.tsx PasswordReset.tsx

# Create payment components
touch PricingPlans.tsx CheckoutForm.tsx SubscriptionManager.tsx
touch BillingHistory.tsx PaymentMethod.tsx QRCodePayment.tsx FreeTrialBanner.tsx
```

#### Task 36: State Management
```bash
cd frontend/web/src/store

# Create stores
touch authStore.ts paymentStore.ts
```

#### Task 37: Email Service
```bash
# Create email service
touch src/autoos/auth/email_service.py
mkdir -p src/autoos/auth/templates
```

#### Task 38: Middleware & Guards
```bash
# Create middleware
touch src/autoos/auth/middleware.py
touch src/autoos/auth/guards.py
```

#### Task 39: Integration
Update existing files:
- src/autoos/intent/api.py (add auth middleware)
- src/autoos/orchestration/orchestrator.py (track user_id)

#### Task 40-41: Testing & Documentation
```bash
# Create tests
mkdir -p tests/auth tests/payment
touch tests/auth/test_authentication.py
touch tests/payment/test_payment_service.py
```

#### Task 42: Final Verification
Run complete test suite and verify all features work.

---

## Quick Deployment (Free Option)

### Option 1: Railway + Vercel (100% Free)

**Time: 30 minutes | Cost: $0/month**

#### Step 1: Deploy Backend to Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Initialize project
railway init

# 4. Add PostgreSQL
railway add postgresql

# 5. Add Redis
railway add redis

# 6. Set environment variables
railway variables set OPENAI_API_KEY=your_key_here
railway variables set ANTHROPIC_API_KEY=your_key_here
railway variables set JWT_SECRET=your_secret_here
railway variables set STRIPE_SECRET_KEY=your_stripe_key

# 7. Deploy
railway up
```

Your backend will be live at: `https://your-app.railway.app`

#### Step 2: Deploy Frontend to Vercel

```bash
cd frontend/web

# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Set environment variable
echo "NEXT_PUBLIC_API_URL=https://your-app.railway.app" > .env.production

# 4. Deploy
vercel --prod
```

Your frontend will be live at: `https://your-app.vercel.app`

#### Step 3: Get Free HTTPS (Automatic)

Both Railway and Vercel provide automatic HTTPS with free SSL certificates. No configuration needed!

#### Step 4: Connect Custom Domain (Optional - $12/year)

**Railway (Backend):**
```bash
railway domain
# Follow prompts to add custom domain
```

**Vercel (Frontend):**
```bash
vercel domains add yourdomain.com
# Follow DNS instructions
```

---

## Production Deployment

### Option 2: AWS/GCP/Azure (Scalable)

See `PUBLISHING_GUIDE.md` for detailed instructions on:
- AWS deployment with ECS/EKS
- GCP deployment with Cloud Run/GKE
- Azure deployment with Container Instances/AKS

### Option 3: Private Cloud (Maximum Security)

See `PRIVATE_CLOUD_SECURITY.md` for:
- Kubernetes deployment
- 13-layer security implementation
- Military-grade protection

---

## Post-Deployment Checklist

### 1. Verify Core Functionality

```bash
# Test API health
curl https://your-app.railway.app/health

# Test authentication
curl -X POST https://your-app.railway.app/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!@#","username":"testuser"}'

# Test free trial activation
curl -X POST https://your-app.railway.app/payments/start-trial \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. Configure Payment Providers

**Stripe Setup:**
```bash
# 1. Create Stripe account at https://stripe.com
# 2. Get API keys from Dashboard
# 3. Set webhook endpoint: https://your-app.railway.app/webhooks/stripe
# 4. Add webhook secret to environment variables
```

**PhonePe/UPI Setup (India):**
```bash
# 1. Register as PhonePe merchant
# 2. Get merchant ID and API credentials
# 3. Configure QR code generation
# 4. Test payment flow
```

### 3. Configure Email Service

**Option A: SendGrid (Free tier: 100 emails/day)**
```bash
railway variables set SENDGRID_API_KEY=your_key
railway variables set FROM_EMAIL=noreply@yourdomain.com
```

**Option B: AWS SES (Free tier: 62,000 emails/month)**
```bash
railway variables set AWS_ACCESS_KEY_ID=your_key
railway variables set AWS_SECRET_ACCESS_KEY=your_secret
railway variables set AWS_REGION=us-east-1
```

### 4. Set Up Monitoring

**Sentry (Error Tracking - Free tier)**
```bash
# Install Sentry
pip install sentry-sdk

# Configure
railway variables set SENTRY_DSN=your_dsn
```

**Prometheus + Grafana (Already configured)**
```bash
# Access Grafana dashboard
open http://localhost:3000
# Default credentials: admin/admin
```

### 5. Configure OAuth Providers

**Google OAuth:**
1. Go to https://console.cloud.google.com
2. Create OAuth 2.0 credentials
3. Add authorized redirect URI: `https://your-app.railway.app/auth/oauth/google/callback`
4. Set environment variables:
```bash
railway variables set GOOGLE_CLIENT_ID=your_client_id
railway variables set GOOGLE_CLIENT_SECRET=your_secret
```

**GitHub OAuth:**
1. Go to https://github.com/settings/developers
2. Create OAuth App
3. Set callback URL: `https://your-app.railway.app/auth/oauth/github/callback`
4. Set environment variables:
```bash
railway variables set GITHUB_CLIENT_ID=your_client_id
railway variables set GITHUB_CLIENT_SECRET=your_secret
```

### 6. Security Checklist

- [ ] HTTPS enabled (automatic with Railway/Vercel)
- [ ] Environment variables secured
- [ ] Database backups configured
- [ ] Rate limiting enabled
- [ ] CORS configured properly
- [ ] JWT secret is strong (32+ characters)
- [ ] MFA enabled for admin accounts
- [ ] Webhook signatures verified
- [ ] SQL injection protection (using ORM)
- [ ] XSS protection (React escapes by default)

### 7. Performance Optimization

```bash
# Enable Redis caching
railway variables set REDIS_URL=your_redis_url

# Configure CDN for static assets
# Vercel provides automatic CDN

# Enable gzip compression (automatic with Railway)

# Set up database connection pooling
railway variables set DB_POOL_SIZE=20
```

### 8. Backup Strategy

**Database Backups (Railway):**
```bash
# Automatic daily backups included
# Manual backup:
railway run pg_dump > backup.sql
```

**Code Backups:**
```bash
# Push to GitHub
git remote add origin https://github.com/yourusername/autoos.git
git push -u origin main
```

### 9. Testing in Production

```bash
# Run smoke tests
npm run test:e2e

# Test free trial flow
# 1. Sign up new user
# 2. Activate free trial
# 3. Submit workflow
# 4. Verify credit deduction
# 5. Check trial expiration

# Test payment flow
# 1. Upgrade from trial
# 2. Complete payment (card or QR)
# 3. Verify subscription activation
# 4. Test usage limits
```

### 10. Launch Announcement

**Prepare:**
- [ ] Landing page ready
- [ ] Documentation complete
- [ ] Support email configured
- [ ] Social media accounts created
- [ ] Demo video recorded
- [ ] Pricing page live
- [ ] Terms of Service published
- [ ] Privacy Policy published

**Launch Channels:**
- Product Hunt
- Hacker News
- Reddit (r/SideProject, r/startups)
- Twitter/X
- LinkedIn
- Dev.to
- Medium

---

## Environment Variables Reference

### Required Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/autoos
REDIS_URL=redis://host:6379

# Authentication
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
JWT_EXPIRATION=3600
REFRESH_TOKEN_EXPIRATION=604800

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Payment
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
PHONEPE_MERCHANT_ID=...
PHONEPE_API_KEY=...

# Email
SENDGRID_API_KEY=SG...
FROM_EMAIL=noreply@yourdomain.com

# OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# Monitoring
SENTRY_DSN=https://...
```

### Optional Variables

```bash
# Features
ENABLE_MFA=true
ENABLE_OAUTH=true
ENABLE_QR_PAYMENTS=true
ENABLE_FREE_TRIAL=true

# Limits
FREE_TRIAL_DAYS=30
FREE_TRIAL_CREDITS=10
FREE_TRIAL_WORKFLOWS=10
FREE_TRIAL_AGENTS=2

# Performance
DB_POOL_SIZE=20
REDIS_POOL_SIZE=10
MAX_WORKERS=4
```

---

## Quick Commands Reference

```bash
# Start development
docker-compose up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec api alembic upgrade head

# Create admin user
docker-compose exec api python -m scripts.create_admin

# Run tests
docker-compose exec api pytest

# Deploy to Railway
railway up

# Deploy to Vercel
cd frontend/web && vercel --prod

# Check deployment status
railway status

# View production logs
railway logs

# Rollback deployment
railway rollback
```

---

## Support & Resources

- **Documentation**: See all `*.md` files in project root
- **Issues**: Create GitHub issue
- **Email**: support@yourdomain.com
- **Discord**: Join community server
- **Status Page**: https://status.yourdomain.com

---

## Next Steps

1. **Complete Phase 9 Implementation** - Follow tasks 31-42 in tasks.md
2. **Test Locally** - Verify all features work with docker-compose
3. **Deploy to Railway** - Get live in 30 minutes
4. **Configure Payments** - Set up Stripe and PhonePe
5. **Launch** - Announce on Product Hunt and social media

**Estimated Time to Launch: 2-3 days** (with Phase 9 implementation)

**Estimated Cost: $0-50/month** (depending on usage and chosen platform)

---

*Last Updated: 2026-02-08*
