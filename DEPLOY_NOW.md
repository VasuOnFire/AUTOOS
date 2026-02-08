# 🚀 Deploy AUTOOS Now - Simple Guide

## Quick Deploy (30 Minutes)

Follow these exact steps to deploy your AUTOOS system.

---

## Prerequisites

You need:
1. **OpenAI API Key** - Get from https://platform.openai.com/api-keys
2. **Anthropic API Key** - Get from https://console.anthropic.com/
3. **GitHub Account** - Free at https://github.com
4. **Railway Account** - Free at https://railway.app
5. **Vercel Account** - Free at https://vercel.com

---

## Option 1: Automatic Deployment (Recommended)

### Run the deployment script:

```bash
./deploy.sh
```

The script will:
1. Install Railway and Vercel CLIs
2. Deploy backend to Railway
3. Add PostgreSQL and Redis
4. Set environment variables
5. Deploy frontend to Vercel
6. Test both deployments
7. Show you the URLs

**That's it!** Your system will be live in 30 minutes.

---

## Option 2: Manual Deployment (Step by Step)

### Step 1: Install CLIs (5 minutes)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Install Vercel CLI
npm install -g vercel
```

### Step 2: Deploy Backend to Railway (10 minutes)

```bash
# Login to Railway
railway login

# Initialize project
railway init

# Add PostgreSQL
railway add postgresql

# Add Redis
railway add redis

# Set environment variables
railway variables set OPENAI_API_KEY=sk-your-openai-key-here
railway variables set ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
railway variables set UPI_ID=vasu7993457842@axl
railway variables set UPI_MERCHANT_NAME=AUTOOS
railway variables set JWT_SECRET=$(openssl rand -base64 32)

# Deploy
railway up
```

**Your backend is now live!** 🎉

Get your backend URL:
```bash
railway status
```

### Step 3: Deploy Frontend to Vercel (10 minutes)

```bash
# Go to frontend directory
cd frontend/web

# Login to Vercel
vercel login

# Set API URL (replace with your Railway URL)
echo "NEXT_PUBLIC_API_URL=https://your-app.railway.app" > .env.production

# Deploy
vercel --prod
```

**Your frontend is now live!** 🎉

### Step 4: Test Your Deployment (5 minutes)

```bash
# Test backend health
curl https://your-app.railway.app/health

# Test API docs
open https://your-app.railway.app/docs

# Test frontend
open https://your-app.vercel.app
```

---

## What You Get

### Backend (Railway)
- **URL**: `https://your-app.railway.app`
- **API Docs**: `https://your-app.railway.app/docs`
- **Database**: PostgreSQL (free tier)
- **Cache**: Redis (free tier)
- **Cost**: $0/month (free tier)

### Frontend (Vercel)
- **URL**: `https://your-app.vercel.app`
- **CDN**: Global edge network
- **HTTPS**: Automatic SSL certificate
- **Cost**: $0/month (free tier)

---

## Environment Variables

### Required Variables

```bash
# LLM API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Payment
UPI_ID=vasu7993457842@axl
UPI_MERCHANT_NAME=AUTOOS

# Security
JWT_SECRET=your-random-secret-32-chars

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Optional Variables

```bash
# Stripe (for card payments)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Email Service
SENDGRID_API_KEY=SG...
FROM_EMAIL=noreply@yourdomain.com

# OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

---

## Verify Deployment

### 1. Check Backend

```bash
# Health check
curl https://your-app.railway.app/health

# Expected response:
# {"status": "healthy"}
```

### 2. Check API Documentation

```bash
# Open API docs
open https://your-app.railway.app/docs
```

You should see interactive API documentation.

### 3. Check Frontend

```bash
# Open frontend
open https://your-app.vercel.app
```

You should see the AUTOOS dashboard.

### 4. Test Workflow Submission

```bash
# Submit test workflow
curl -X POST https://your-app.railway.app/intents \
  -H "Content-Type: application/json" \
  -d '{"intent": "Analyze the weather and suggest activities"}'
```

---

## Custom Domain (Optional)

### Add Domain to Railway (Backend)

```bash
# In Railway dashboard
railway domain

# Follow prompts to add your domain
# Example: api.yourdomain.com
```

### Add Domain to Vercel (Frontend)

```bash
# Add domain
vercel domains add yourdomain.com

# Follow DNS instructions
# Add CNAME record: yourdomain.com -> cname.vercel-dns.com
```

**Cost**: $8-12/year for domain (optional)

---

## Monitoring

### Railway Dashboard

```
https://railway.app/dashboard
```

View:
- Deployment logs
- Resource usage
- Database metrics
- Environment variables

### Vercel Dashboard

```
https://vercel.com/dashboard
```

View:
- Deployment status
- Analytics
- Performance metrics
- Build logs

---

## Troubleshooting

### Backend Not Starting

```bash
# Check logs
railway logs

# Common issues:
# 1. Missing environment variables
railway variables

# 2. Database connection failed
railway run psql

# 3. Redis connection failed
railway run redis-cli ping
```

### Frontend Not Loading

```bash
# Check Vercel logs
vercel logs

# Common issues:
# 1. Wrong API URL
cat frontend/web/.env.production

# 2. Build failed
vercel --debug
```

### Database Issues

```bash
# Connect to database
railway run psql

# Check tables
\dt

# Run migrations
railway run alembic upgrade head
```

---

## Update Deployment

### Update Backend

```bash
# Make changes to code
git add .
git commit -m "Update backend"

# Deploy
railway up
```

### Update Frontend

```bash
cd frontend/web

# Make changes to code
git add .
git commit -m "Update frontend"

# Deploy
vercel --prod
```

---

## Rollback Deployment

### Rollback Backend

```bash
# View deployments
railway status

# Rollback to previous
railway rollback
```

### Rollback Frontend

```bash
# View deployments
vercel ls

# Rollback to previous
vercel rollback
```

---

## Cost Breakdown

### Free Tier (Perfect for Starting)

| Service | Free Tier | Cost |
|---------|-----------|------|
| Railway | $5 credit/month | $0 |
| Vercel | 100 GB bandwidth | $0 |
| PostgreSQL | 1 GB storage | $0 |
| Redis | 100 MB storage | $0 |
| **Total** | | **$0/month** |

### When You Grow

| Service | Paid Tier | Cost |
|---------|-----------|------|
| Railway | $5/month + usage | $10-50/month |
| Vercel | Pro plan | $20/month |
| PostgreSQL | Larger database | $10-30/month |
| Redis | More memory | $5-20/month |
| **Total** | | **$45-120/month** |

---

## Next Steps After Deployment

### 1. Test Access Code System

```bash
# Generate test access code
python src/autoos/auth/access_code.py
```

### 2. Test QR Payment

```bash
# Generate test QR code
python scripts/test_qr_payment.py
```

### 3. Configure Stripe (Optional)

```bash
# Add Stripe keys
railway variables set STRIPE_SECRET_KEY=sk_live_...
railway variables set STRIPE_PUBLISHABLE_KEY=pk_live_...
```

### 4. Set Up Email Service

```bash
# Add SendGrid key
railway variables set SENDGRID_API_KEY=SG...
railway variables set FROM_EMAIL=noreply@yourdomain.com
```

### 5. Complete Phase 9

Follow `PHASE_9_STATUS.md` to implement:
- Authentication API endpoints
- Payment API endpoints
- Frontend components
- Email notifications

### 6. Launch!

- Announce on Product Hunt
- Share on social media
- Get first users
- Start accepting payments to `vasu7993457842@axl`

---

## Support

### Documentation
- `QUICK_DEPLOY.md` - This guide
- `ACCESS_CODE_SYSTEM.md` - Access code guide
- `PAYMENT_SETUP.md` - Payment setup
- `FINAL_IMPLEMENTATION_SUMMARY.md` - Complete summary

### Help
- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- GitHub Issues: Create an issue
- Email: support@autoos.ai

---

## Quick Commands Reference

```bash
# Deploy backend
railway up

# Deploy frontend
cd frontend/web && vercel --prod

# View backend logs
railway logs

# View frontend logs
vercel logs

# Check backend status
railway status

# Check frontend status
vercel ls

# Rollback backend
railway rollback

# Rollback frontend
vercel rollback

# Update environment variable
railway variables set KEY=value

# Connect to database
railway run psql

# Connect to Redis
railway run redis-cli
```

---

## Success Checklist

- [ ] Railway CLI installed
- [ ] Vercel CLI installed
- [ ] Backend deployed to Railway
- [ ] PostgreSQL added
- [ ] Redis added
- [ ] Environment variables set
- [ ] Frontend deployed to Vercel
- [ ] API URL configured
- [ ] Health check passes
- [ ] API docs accessible
- [ ] Frontend loads correctly
- [ ] Test workflow submitted
- [ ] HTTPS working
- [ ] Monitoring configured

---

**Your AUTOOS system is ready to deploy!** 🚀

Run `./deploy.sh` or follow the manual steps above.

*Last Updated: February 8, 2026*
