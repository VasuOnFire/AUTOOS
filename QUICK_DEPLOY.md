# ⚡ AUTOOS - Quick Deploy Guide

Get AUTOOS live in **30 minutes** with **$0/month** cost!

---

## 🎯 What You'll Get

- ✅ Complete AUTOOS system running in the cloud
- ✅ Automatic HTTPS with free SSL certificate
- ✅ PostgreSQL database (free tier)
- ✅ Redis cache (free tier)
- ✅ Web UI accessible from anywhere
- ✅ API with automatic documentation
- ✅ No credit card required for deployment

---

## 📋 Prerequisites

1. **GitHub Account** (free)
2. **Railway Account** (free) - https://railway.app
3. **Vercel Account** (free) - https://vercel.com
4. **API Keys** (free trials available):
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

---

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Code (5 minutes)

```bash
# 1. Clone or download AUTOOS
git clone https://github.com/yourusername/autoos.git
cd autoos

# 2. Create GitHub repository
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/autoos.git
git push -u origin main
```

### Step 2: Deploy Backend to Railway (10 minutes)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Create new project
railway init

# 4. Add PostgreSQL database
railway add postgresql

# 5. Add Redis cache
railway add redis

# 6. Set environment variables
railway variables set OPENAI_API_KEY=sk-your-openai-key-here
railway variables set ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
railway variables set JWT_SECRET=$(openssl rand -base64 32)
railway variables set SECRET_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# 7. Deploy!
railway up
```

**Your backend is now live!** 🎉

Railway will give you a URL like: `https://autoos-production.up.railway.app`

### Step 3: Deploy Frontend to Vercel (10 minutes)

```bash
# 1. Go to frontend directory
cd frontend/web

# 2. Install Vercel CLI
npm install -g vercel

# 3. Login to Vercel
vercel login

# 4. Set API URL
echo "NEXT_PUBLIC_API_URL=https://autoos-production.up.railway.app" > .env.production

# 5. Deploy!
vercel --prod
```

**Your frontend is now live!** 🎉

Vercel will give you a URL like: `https://autoos.vercel.app`

### Step 4: Verify Deployment (5 minutes)

```bash
# 1. Check backend health
curl https://autoos-production.up.railway.app/health

# 2. Check API docs
open https://autoos-production.up.railway.app/docs

# 3. Check frontend
open https://autoos.vercel.app

# 4. Test workflow submission
curl -X POST https://autoos-production.up.railway.app/intents \
  -H "Content-Type: application/json" \
  -d '{"intent": "Analyze the weather and suggest activities"}'
```

---

## 🎨 Access Your System

### Web UI
```
https://autoos.vercel.app
```

### API
```
https://autoos-production.up.railway.app
```

### API Documentation
```
https://autoos-production.up.railway.app/docs
```

### Metrics (Prometheus)
```
https://autoos-production.up.railway.app/metrics
```

---

## 🔧 Optional: Custom Domain (5 minutes)

### Add Custom Domain to Railway (Backend)

```bash
# In Railway dashboard
railway domain

# Follow prompts to add your domain
# Example: api.yourdomain.com
```

### Add Custom Domain to Vercel (Frontend)

```bash
# In Vercel dashboard
vercel domains add yourdomain.com

# Follow DNS instructions
# Add CNAME record: yourdomain.com -> cname.vercel-dns.com
```

**Cost**: $8-12/year for domain (optional)

---

## 📊 Monitor Your Deployment

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

## 🔐 Security Checklist

After deployment, verify:

- [ ] HTTPS is enabled (automatic)
- [ ] Environment variables are set
- [ ] Database is accessible
- [ ] Redis is connected
- [ ] API keys are working
- [ ] CORS is configured
- [ ] Rate limiting is active

---

## 🎯 Next Steps

### 1. Complete Phase 9 (Authentication & Payment)

Follow the implementation guide in `PHASE_9_STATUS.md`:

```bash
# Estimated time: 7-10 days
# Tasks: 31-42 in .kiro/specs/autoos-omega/tasks.md
```

Features to add:
- User authentication (signup, signin, MFA)
- Free trial (30 days, no credit card)
- Payment processing (Stripe + QR codes)
- Subscription management
- Email notifications

### 2. Configure Payment Providers

**Stripe** (for card payments):
```bash
# 1. Create account: https://stripe.com
# 2. Get API keys from dashboard
# 3. Add to Railway:
railway variables set STRIPE_SECRET_KEY=sk_live_...
railway variables set STRIPE_PUBLISHABLE_KEY=pk_live_...
```

**PhonePe** (for QR/UPI payments in India):
```bash
# 1. Register as merchant: https://www.phonepe.com/business
# 2. Get credentials
# 3. Add to Railway:
railway variables set PHONEPE_MERCHANT_ID=...
railway variables set PHONEPE_API_KEY=...
```

### 3. Set Up Email Service

**Option A: SendGrid** (Free: 100 emails/day)
```bash
# 1. Create account: https://sendgrid.com
# 2. Get API key
# 3. Add to Railway:
railway variables set SENDGRID_API_KEY=SG...
railway variables set FROM_EMAIL=noreply@yourdomain.com
```

**Option B: AWS SES** (Free: 62,000 emails/month)
```bash
# 1. Set up AWS SES
# 2. Verify domain
# 3. Add to Railway:
railway variables set AWS_ACCESS_KEY_ID=...
railway variables set AWS_SECRET_ACCESS_KEY=...
railway variables set AWS_REGION=us-east-1
```

### 4. Enable Monitoring

**Sentry** (Error tracking - Free tier):
```bash
# 1. Create account: https://sentry.io
# 2. Create project
# 3. Add to Railway:
railway variables set SENTRY_DSN=https://...
```

### 5. Configure OAuth Providers

**Google OAuth**:
```bash
# 1. Go to: https://console.cloud.google.com
# 2. Create OAuth credentials
# 3. Add redirect URI: https://your-api.railway.app/auth/oauth/google/callback
# 4. Add to Railway:
railway variables set GOOGLE_CLIENT_ID=...
railway variables set GOOGLE_CLIENT_SECRET=...
```

**GitHub OAuth**:
```bash
# 1. Go to: https://github.com/settings/developers
# 2. Create OAuth App
# 3. Add callback URL: https://your-api.railway.app/auth/oauth/github/callback
# 4. Add to Railway:
railway variables set GITHUB_CLIENT_ID=...
railway variables set GITHUB_CLIENT_SECRET=...
```

---

## 💰 Cost Breakdown

### Free Tier (Perfect for Testing)

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

## 🆘 Troubleshooting

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
cat .env.production

# 2. Build failed
vercel --debug

# 3. CORS error
# Add your Vercel domain to CORS_ORIGINS in Railway
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

### Redis Issues

```bash
# Test Redis connection
railway run redis-cli ping

# Should return: PONG
```

---

## 📚 Useful Commands

### Railway Commands

```bash
# View logs
railway logs

# View logs (follow)
railway logs -f

# Run command in Railway environment
railway run <command>

# Connect to database
railway run psql

# Connect to Redis
railway run redis-cli

# View environment variables
railway variables

# Set environment variable
railway variables set KEY=value

# Deploy
railway up

# Check status
railway status

# Rollback
railway rollback
```

### Vercel Commands

```bash
# Deploy
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs

# View domains
vercel domains ls

# Add domain
vercel domains add yourdomain.com

# Remove deployment
vercel rm <deployment-url>
```

---

## 🎓 Learning Resources

### Documentation
- `README.md` - Main documentation
- `LAUNCH_CHECKLIST.md` - Complete launch guide
- `PHASE_9_STATUS.md` - Implementation status
- `COMPLETE_SYSTEM_SUMMARY.md` - System overview

### Video Tutorials (Coming Soon)
- Quick deploy walkthrough
- Phase 9 implementation guide
- Payment integration tutorial
- Security best practices

### Community
- GitHub Discussions
- Discord Server
- Stack Overflow (tag: autoos)

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway account created
- [ ] Vercel account created
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

## 🎉 Success!

Your AUTOOS system is now live and accessible from anywhere!

**What you have**:
- ✅ Production-ready backend
- ✅ Beautiful frontend
- ✅ Automatic HTTPS
- ✅ Free hosting
- ✅ Scalable infrastructure
- ✅ Complete monitoring

**What's next**:
1. Complete Phase 9 (auth & payment)
2. Configure payment providers
3. Set up email service
4. Enable OAuth
5. Launch! 🚀

---

## 📞 Need Help?

- **Documentation**: See all `*.md` files
- **Issues**: GitHub Issues
- **Email**: support@yourdomain.com
- **Discord**: Join community server

---

**Congratulations! You've deployed AUTOOS in 30 minutes!** 🎊

*Now go build something amazing!* 🚀

---

*Last Updated: February 8, 2026*
