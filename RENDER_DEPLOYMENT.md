# Render Deployment Guide 🚀

Complete step-by-step guide to deploy AUTOOS Omega on Render.

## Why Render?

- ✅ **Free Tier:** 750 hours/month free (enough for 1 service 24/7)
- ✅ **Auto-Deploy:** Automatic deployments from GitHub
- ✅ **Free PostgreSQL:** 90-day free database
- ✅ **Free Redis:** 30-day free cache
- ✅ **SSL Included:** Free HTTPS certificates
- ✅ **Easy Setup:** Simple configuration

## Prerequisites

1. ✅ Render account (sign up at https://render.com)
2. ✅ GitHub repository (already done: https://github.com/VasuOnFire/autoos-omega)
3. ✅ OpenAI API key (for AI features)

---

## 🎯 Quick Deploy (Recommended)

### Option 1: One-Click Deploy with Blueprint

1. **Go to Render Dashboard:** https://dashboard.render.com
2. **Click "New" → "Blueprint"**
3. **Connect GitHub repository:** `VasuOnFire/autoos-omega`
4. **Render will detect `render.yaml`** and create all services automatically
5. **Add required environment variables** (see below)
6. **Click "Apply"** and wait for deployment

### Option 2: Manual Setup (Step-by-Step)

Follow the detailed steps below if you prefer manual configuration.

---

## 📋 Step-by-Step Manual Deployment

### Step 1: Create PostgreSQL Database

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name:** `autoos-db`
   - **Database:** `autoos`
   - **User:** `autoos`
   - **Region:** Oregon (US West)
   - **Plan:** Free
4. Click **"Create Database"**
5. **Copy the Internal Database URL** (starts with `postgresql://`)

### Step 2: Create Redis Instance

1. Click **"New +"** → **"Redis"**
2. Configure:
   - **Name:** `autoos-redis`
   - **Region:** Oregon (US West)
   - **Plan:** Free (30 days)
3. Click **"Create Redis"**
4. **Copy the Internal Redis URL** (starts with `redis://`)

### Step 3: Deploy Backend API

1. Click **"New +"** → **"Web Service"**
2. **Connect GitHub:** Select `VasuOnFire/autoos-omega`
3. Configure:
   - **Name:** `autoos-backend`
   - **Region:** Oregon (US West)
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn src.autoos.intent.api:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

4. **Add Environment Variables:**

   Click "Advanced" → "Add Environment Variable"

   **Required Variables:**
   ```
   PYTHON_VERSION=3.11.0
   DATABASE_URL=<paste-your-postgres-url>
   REDIS_URL=<paste-your-redis-url>
   JWT_SECRET_KEY=<generate-random-string>
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   OPENAI_API_KEY=<your-openai-key>
   ```

   **Optional Variables (for full features):**
   ```
   STRIPE_SECRET_KEY=<your-stripe-key>
   STRIPE_PUBLISHABLE_KEY=<your-stripe-pub-key>
   STRIPE_WEBHOOK_SECRET=<your-webhook-secret>
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=<your-email>
   SMTP_PASSWORD=<your-app-password>
   GOOGLE_CLIENT_ID=<your-google-client-id>
   GOOGLE_CLIENT_SECRET=<your-google-secret>
   ```

5. Click **"Create Web Service"**

### Step 4: Deploy Frontend

1. Click **"New +"** → **"Web Service"**
2. **Connect GitHub:** Select `VasuOnFire/autoos-omega`
3. Configure:
   - **Name:** `autoos-frontend`
   - **Region:** Oregon (US West)
   - **Branch:** `main`
   - **Root Directory:** `frontend/web`
   - **Runtime:** Node
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npm start`
   - **Plan:** Free

4. **Add Environment Variables:**
   ```
   NODE_VERSION=18.17.0
   NEXT_PUBLIC_API_URL=https://autoos-backend.onrender.com
   ```
   (Replace with your actual backend URL from Step 3)

5. Click **"Create Web Service"**

### Step 5: Initialize Database

After backend is deployed:

1. Go to your backend service
2. Click **"Shell"** tab
3. Run:
   ```bash
   python -c "from src.autoos.auth.models import init_db; init_db()"
   ```

Or connect to your database and run:
```bash
psql $DATABASE_URL < scripts/init-db.sql
```

---

## 🔐 Environment Variables Reference

### Backend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `REDIS_URL` | Redis connection string | `redis://host:port` |
| `JWT_SECRET_KEY` | Secret for JWT tokens | Generate with `openssl rand -hex 32` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |

### Frontend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://autoos-backend.onrender.com` |

### Optional Variables

| Variable | Description |
|----------|-------------|
| `STRIPE_SECRET_KEY` | For payment processing |
| `SMTP_HOST` | For email notifications |
| `GOOGLE_CLIENT_ID` | For OAuth login |

---

## 🌐 Your Live URLs

After deployment, you'll have:

- **Frontend:** `https://autoos-frontend.onrender.com`
- **Backend API:** `https://autoos-backend.onrender.com`
- **API Docs:** `https://autoos-backend.onrender.com/docs`
- **Database:** Internal URL (not public)
- **Redis:** Internal URL (not public)

---

## 💰 Cost Breakdown

### Free Tier (Perfect for Development)

- **Web Services:** 750 hours/month free (1 service 24/7)
- **PostgreSQL:** Free for 90 days, then $7/month
- **Redis:** Free for 30 days, then $10/month
- **Bandwidth:** 100 GB/month free
- **SSL:** Free forever

### Paid Plans (For Production)

- **Starter:** $7/month per service
- **Standard:** $25/month per service
- **Pro:** $85/month per service

**Recommendation:** Start with free tier, upgrade backend to Starter ($7/mo) when ready for production.

---

## 🔧 Configuration Tips

### 1. Auto-Deploy from GitHub

Render automatically deploys when you push to GitHub:
- Push to `main` branch → Auto-deploy
- Configure in service settings → "Auto-Deploy"

### 2. Custom Domain

1. Go to service settings
2. Click "Custom Domain"
3. Add your domain
4. Update DNS records as instructed
5. SSL certificate auto-generated

### 3. Environment Groups

Create environment groups for shared variables:
1. Dashboard → "Environment Groups"
2. Create group (e.g., "Production")
3. Add variables
4. Link to services

### 4. Health Checks

Render automatically monitors:
- HTTP endpoint health
- Service availability
- Auto-restart on failure

Configure custom health check:
- Path: `/health`
- Interval: 30 seconds
- Timeout: 10 seconds

---

## 📊 Monitoring & Logs

### View Logs

1. Go to your service
2. Click "Logs" tab
3. Real-time log streaming
4. Filter by severity

### Metrics

Render provides:
- CPU usage
- Memory usage
- Request count
- Response times
- Error rates

### Alerts

Set up alerts:
1. Service settings → "Alerts"
2. Configure thresholds
3. Add email/Slack notifications

---

## 🐛 Troubleshooting

### Build Fails

**Issue:** Python dependencies fail to install
**Solution:** 
- Check `requirements.txt` is complete
- Verify Python version in environment variables
- Check build logs for specific errors

**Issue:** Node build fails
**Solution:**
- Ensure `package.json` is in `frontend/web`
- Check Node version compatibility
- Verify all dependencies are listed

### Database Connection Issues

**Issue:** Can't connect to database
**Solution:**
- Verify `DATABASE_URL` is set correctly
- Use **Internal Database URL** (not external)
- Check database is running
- Ensure migrations are applied

### Frontend Can't Reach Backend

**Issue:** API calls fail with CORS errors
**Solution:**
- Update `NEXT_PUBLIC_API_URL` with correct backend URL
- Add frontend URL to CORS origins in backend
- Verify both services are deployed

### Service Keeps Restarting

**Issue:** Service crashes on startup
**Solution:**
- Check logs for error messages
- Verify all required environment variables are set
- Ensure start command is correct
- Check for missing dependencies

---

## 🚀 Performance Optimization

### 1. Enable Caching

Use Redis for:
- Session storage
- API response caching
- Rate limiting

### 2. Database Optimization

- Add indexes to frequently queried columns
- Use connection pooling
- Enable query caching

### 3. Frontend Optimization

- Enable Next.js image optimization
- Use static generation where possible
- Implement code splitting

### 4. CDN Integration

- Use Render's built-in CDN
- Cache static assets
- Optimize images

---

## 🔒 Security Best Practices

1. **Environment Variables**
   - Never commit secrets to Git
   - Use Render's secret management
   - Rotate keys regularly

2. **Database Security**
   - Use internal URLs only
   - Enable SSL connections
   - Regular backups

3. **API Security**
   - Enable rate limiting
   - Use JWT authentication
   - Implement CORS properly

4. **HTTPS**
   - Render provides free SSL
   - Force HTTPS redirects
   - Use secure cookies

---

## 📦 Backup & Recovery

### Database Backups

Render automatically backs up PostgreSQL:
- Daily backups
- 7-day retention (free tier)
- 30-day retention (paid plans)

### Manual Backup

```bash
# Export database
pg_dump $DATABASE_URL > backup.sql

# Restore database
psql $DATABASE_URL < backup.sql
```

### Disaster Recovery

1. Keep `render.yaml` in version control
2. Document all environment variables
3. Regular database backups
4. Test restore procedures

---

## 🎓 Next Steps

After deployment:

1. ✅ **Test all endpoints** - Visit `/docs` for API documentation
2. ✅ **Verify authentication** - Test sign up/sign in
3. ✅ **Check database** - Ensure tables are created
4. ✅ **Test payments** - If using Stripe integration
5. ✅ **Set up monitoring** - Configure alerts
6. ✅ **Add custom domain** - Point your domain to Render
7. ✅ **Enable auto-deploy** - Push to deploy automatically
8. ✅ **Upgrade plan** - When ready for production

---

## 📚 Resources

- **Render Docs:** https://render.com/docs
- **Render Status:** https://status.render.com
- **Community Forum:** https://community.render.com
- **GitHub Repo:** https://github.com/VasuOnFire/autoos-omega

---

## 🆘 Support

Need help?

1. **Check Render Docs:** https://render.com/docs
2. **Community Forum:** https://community.render.com
3. **GitHub Issues:** https://github.com/VasuOnFire/autoos-omega/issues
4. **Render Support:** support@render.com

---

## ✅ Deployment Checklist

- [ ] Create Render account
- [ ] Create PostgreSQL database
- [ ] Create Redis instance
- [ ] Deploy backend service
- [ ] Deploy frontend service
- [ ] Set all environment variables
- [ ] Initialize database
- [ ] Test API endpoints
- [ ] Test frontend
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring
- [ ] Enable auto-deploy

---

**🎉 Congratulations! Your AUTOOS Omega is now live on Render!**

**Frontend:** https://autoos-frontend.onrender.com
**Backend:** https://autoos-backend.onrender.com
**API Docs:** https://autoos-backend.onrender.com/docs

---

**Built with ❤️ by Vasu (@VasuOnFire)**
