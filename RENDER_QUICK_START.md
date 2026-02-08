# 🚀 Render Quick Start - Deploy in 5 Minutes!

## Step 1: Go to Render Dashboard
👉 https://dashboard.render.com

## Step 2: Deploy with Blueprint (Easiest!)

1. Click **"New +"** → **"Blueprint"**
2. Connect your GitHub repository: `VasuOnFire/autoos-omega`
3. Render will detect `render.yaml` automatically
4. Click **"Apply"**

## Step 3: Add Required Environment Variables

After services are created, add these to the **backend service**:

### Minimum Required (to get started):
```
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET_KEY=your-random-secret-key
```

### Generate JWT Secret:
Run this in your terminal:
```bash
openssl rand -hex 32
```

## Step 4: Wait for Deployment

- Backend: ~5 minutes
- Frontend: ~3 minutes
- Database: ~2 minutes

## Step 5: Access Your App!

- **Frontend:** `https://autoos-frontend.onrender.com`
- **Backend API:** `https://autoos-backend.onrender.com`
- **API Docs:** `https://autoos-backend.onrender.com/docs`

---

## ⚠️ Important Notes

### Free Tier Limitations:
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- 750 hours/month free (enough for 1 service 24/7)

### Database:
- PostgreSQL: Free for 90 days
- Redis: Free for 30 days
- After trial, upgrade or data will be deleted

### To Keep Services Always On:
- Upgrade to Starter plan ($7/month per service)
- Or use a cron job to ping your service every 10 minutes

---

## 🎯 What You Get

✅ Complete AUTOOS Omega system
✅ AI-powered workflow automation
✅ Authentication system (sign up/sign in/MFA)
✅ Payment processing (Stripe + QR codes)
✅ Real-time dashboard
✅ Agent orchestration
✅ Free SSL certificate
✅ Auto-deploy from GitHub

---

## 📚 Full Documentation

For detailed setup, troubleshooting, and advanced configuration:
👉 See `RENDER_DEPLOYMENT.md`

---

## 🆘 Quick Troubleshooting

**Service won't start?**
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure DATABASE_URL and REDIS_URL are correct

**Can't connect to API?**
- Update NEXT_PUBLIC_API_URL in frontend
- Check CORS settings in backend
- Verify both services are deployed

**Database errors?**
- Run database initialization script
- Check DATABASE_URL format
- Ensure database is running

---

**Need Help?** Check `RENDER_DEPLOYMENT.md` for complete guide!

**Ready to deploy?** 👉 https://dashboard.render.com
