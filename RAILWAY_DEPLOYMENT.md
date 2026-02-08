# Railway Deployment Guide 🚂

Complete guide to deploy AUTOOS Omega on Railway.

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. GitHub account with this repository
3. Stripe account (optional, for payments)
4. OpenAI API key

## Step 1: Push to GitHub

```bash
# Add remote (replace with your repo URL)
git remote add origin https://github.com/VasuOnFire/autoos-omega.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 2: Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your `autoos-omega` repository
4. Railway will detect the configuration automatically

## Step 3: Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a `DATABASE_URL` variable

## Step 4: Add Redis

1. Click "New" again
2. Select "Database" → "Redis"
3. Railway will automatically create a `REDIS_URL` variable

## Step 5: Configure Environment Variables

In your Railway project settings, add these variables:

### Required Variables

```env
# Database (automatically set by Railway)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_HOST=0.0.0.0
API_PORT=$PORT
CORS_ORIGINS=https://your-frontend-domain.railway.app

# OpenAI (required for AI features)
OPENAI_API_KEY=sk-...
```

### Optional Variables (for full features)

```env
# Stripe Payment (optional)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email Service (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@autoos.ai

# OAuth (optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
```

## Step 6: Deploy Backend

Railway will automatically:
1. Install Python dependencies from `requirements.txt`
2. Start the FastAPI server using the `Procfile`
3. Expose the service on a public URL

Your backend will be available at: `https://your-project.railway.app`

## Step 7: Deploy Frontend (Separate Service)

1. In your Railway project, click "New"
2. Select "GitHub Repo" again
3. Choose the same repository
4. Set the root directory to `frontend/web`
5. Add environment variables:

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

Railway will:
1. Install Node.js dependencies
2. Build the Next.js app
3. Serve the frontend

Your frontend will be available at: `https://your-frontend.railway.app`

## Step 8: Initialize Database

After deployment, run the database initialization:

```bash
# Using Railway CLI
railway run python -c "from src.autoos.auth.models import init_db; init_db()"

# Or connect to your database and run
psql $DATABASE_URL < scripts/init-db.sql
```

## Step 9: Configure Custom Domain (Optional)

1. Go to your service settings
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Update DNS records as instructed
5. Update `CORS_ORIGINS` environment variable

## Step 10: Set Up Webhooks (Optional)

For Stripe webhooks:

1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://your-backend.railway.app/payments/webhook`
3. Select events to listen to
4. Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

## Monitoring & Logs

### View Logs
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# View logs
railway logs
```

### Metrics
Railway provides built-in metrics:
- CPU usage
- Memory usage
- Network traffic
- Request count

Access metrics in your project dashboard.

## Scaling

Railway automatically scales based on:
- Traffic
- Resource usage
- Configuration

To configure scaling:
1. Go to service settings
2. Adjust "Replicas" and "Resources"
3. Set auto-scaling rules

## Cost Optimization

### Free Tier
- $5 free credit per month
- Suitable for development/testing

### Pro Plan ($20/month)
- Unlimited projects
- Custom domains
- Priority support
- Better performance

### Tips to Reduce Costs
1. Use smaller database instances for development
2. Enable auto-sleep for inactive services
3. Optimize Docker images
4. Use caching effectively

## Troubleshooting

### Build Fails
- Check `railway.json` configuration
- Verify `requirements.txt` is complete
- Check Python version compatibility

### Database Connection Issues
- Verify `DATABASE_URL` is set
- Check database is running
- Ensure migrations are applied

### Frontend Can't Connect to Backend
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS configuration
- Ensure backend is deployed and running

### Environment Variables Not Working
- Restart the service after adding variables
- Check variable names match exactly
- Verify no typos in values

## Health Checks

Railway automatically monitors:
- HTTP endpoint health
- Service availability
- Resource usage

Configure custom health checks:
1. Go to service settings
2. Add health check endpoint: `/health`
3. Set check interval and timeout

## Backup & Recovery

### Database Backups
Railway automatically backs up PostgreSQL:
- Daily backups
- 7-day retention
- Point-in-time recovery

### Manual Backup
```bash
# Export database
railway run pg_dump $DATABASE_URL > backup.sql

# Restore database
railway run psql $DATABASE_URL < backup.sql
```

## CI/CD

Railway automatically deploys on:
- Push to main branch
- Pull request merge
- Manual trigger

Configure deployment:
1. Go to project settings
2. Set deployment branch
3. Configure build settings
4. Set deployment triggers

## Security Best Practices

1. **Use Environment Variables** - Never commit secrets
2. **Enable HTTPS** - Railway provides SSL automatically
3. **Set Strong JWT Secret** - Use a long random string
4. **Configure CORS** - Restrict to your domains only
5. **Enable Rate Limiting** - Protect against abuse
6. **Regular Updates** - Keep dependencies updated
7. **Monitor Logs** - Watch for suspicious activity

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/VasuOnFire/autoos-omega/issues

## Next Steps

After deployment:
1. Test all endpoints
2. Verify authentication works
3. Test payment integration
4. Set up monitoring alerts
5. Configure custom domain
6. Enable auto-scaling
7. Set up CI/CD pipeline

---

**Deployment Complete! 🎉**

Your AUTOOS Omega is now live on Railway!

Frontend: https://your-frontend.railway.app
Backend: https://your-backend.railway.app
API Docs: https://your-backend.railway.app/docs
