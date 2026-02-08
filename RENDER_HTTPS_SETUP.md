# 🔒 HTTPS Setup for AUTOOS on Render

Complete guide to get secure HTTPS links for your AUTOOS deployment on Render - **100% FREE & AUTOMATIC!**

---

## 🎯 What You'll Get

After deploying to Render, you automatically get:
- ✅ `https://autoos-backend.onrender.com` (Backend API)
- ✅ `https://autoos-frontend.onrender.com` (Web App)
- ✅ FREE SSL certificates (auto-provisioned)
- ✅ Auto-renewal (no maintenance needed)
- ✅ Green padlock 🔒 in browser

**Total Cost: $0** - HTTPS is included FREE with Render!

---

## 🚀 Automatic HTTPS (Default)

### Good News: HTTPS is Automatic on Render!

When you deploy to Render using the Blueprint (render.yaml), **HTTPS is enabled automatically**:

1. **Deploy your app** using the Blueprint
2. **Render provisions SSL certificates** automatically
3. **HTTPS URLs are ready** immediately
4. **Certificates auto-renew** every 90 days

**No configuration needed!** 🎉

### Your HTTPS URLs

After deployment, you'll get:

```
Backend API:  https://autoos-backend.onrender.com
Frontend Web: https://autoos-frontend.onrender.com
```

Both URLs have:
- ✅ Valid SSL certificates
- ✅ HTTPS enabled
- ✅ Secure connections
- ✅ Green padlock in browser

---

## 📋 Step-by-Step: Deploy with HTTPS

### Step 1: Deploy to Render

```bash
# 1. Go to Render Dashboard
https://dashboard.render.com

# 2. Click "New" → "Blueprint"

# 3. Connect your GitHub repo
# Select: VasuOnFire/AUTOOS

# 4. Render detects render.yaml automatically

# 5. Set environment variables:
STRIPE_SECRET_KEY=<your Stripe test key>
STRIPE_WEBHOOK_SECRET=whsec_placeholder_update_after_deploy
OPENAI_API_KEY=<optional>

# 6. Click "Apply"

# 7. Wait 5-10 minutes for deployment

# 8. Done! Your HTTPS URLs are ready! 🎉
```

### Step 2: Get Your HTTPS URLs

```bash
# After deployment completes:

# 1. Go to Render Dashboard
# 2. Click on "autoos-backend" service
# 3. Copy the URL (starts with https://)
# Example: https://autoos-backend.onrender.com

# 4. Click on "autoos-frontend" service
# 5. Copy the URL (starts with https://)
# Example: https://autoos-frontend.onrender.com

# Both URLs have HTTPS automatically! ✅
```

### Step 3: Update Frontend to Use Backend HTTPS URL

The frontend needs to know your backend HTTPS URL:

```bash
# In Render Dashboard:

# 1. Go to "autoos-frontend" service
# 2. Click "Environment" tab
# 3. Add environment variable:
NEXT_PUBLIC_API_URL=https://autoos-backend.onrender.com

# 4. Save (service will auto-redeploy)

# Done! Frontend now connects to backend via HTTPS
```

---

## 🌐 Custom Domain with FREE HTTPS

Want to use your own domain? Render makes it easy!

### Option 1: Free Subdomain (Render Default)

You already have this:
```
https://autoos-backend.onrender.com
https://autoos-frontend.onrender.com
```

**Cost**: FREE ✅

### Option 2: Custom Domain (Your Own Domain)

#### Step 1: Get a Domain

**Free Options:**
- Freenom: Free domains (.tk, .ml, .ga, .cf, .gq)
- Cost: $0/year

**Paid Options:**
- Namecheap: $8-12/year
- Google Domains: $12/year
- Cloudflare: $10/year

#### Step 2: Add Custom Domain to Render

**For Frontend (Web App):**

```bash
# 1. Go to Render Dashboard
# 2. Select "autoos-frontend" service
# 3. Click "Settings" tab
# 4. Scroll to "Custom Domains"
# 5. Click "Add Custom Domain"
# 6. Enter your domain: autoos.com
# 7. Render shows DNS records to add

# 8. Add these DNS records at your domain registrar:
Type: A
Name: @
Value: <IP shown by Render>

Type: CNAME
Name: www
Value: autoos-frontend.onrender.com

# 9. Wait 5-60 minutes for DNS propagation
# 10. Render automatically provisions SSL certificate
# 11. Done! Your site is at: https://autoos.com
```

**For Backend (API):**

```bash
# 1. Go to Render Dashboard
# 2. Select "autoos-backend" service
# 3. Click "Settings" tab
# 4. Scroll to "Custom Domains"
# 5. Click "Add Custom Domain"
# 6. Enter subdomain: api.autoos.com
# 7. Render shows DNS record to add

# 8. Add this DNS record at your domain registrar:
Type: CNAME
Name: api
Value: autoos-backend.onrender.com

# 9. Wait for DNS propagation
# 10. Render automatically provisions SSL certificate
# 11. Done! Your API is at: https://api.autoos.com
```

### Step 3: Update Environment Variables

```bash
# Update frontend environment variable:

# In Render Dashboard:
# 1. Go to "autoos-frontend" service
# 2. Click "Environment" tab
# 3. Update:
NEXT_PUBLIC_API_URL=https://api.autoos.com

# 4. Save (auto-redeploys)

# Done! Your custom domain has HTTPS! 🎉
```

---

## 🔧 SSL Certificate Details

### Render's SSL Certificates

Render uses **Let's Encrypt** certificates:

- ✅ **FREE** - No cost
- ✅ **Automatic** - Provisioned on deployment
- ✅ **Auto-renewal** - Renews every 90 days automatically
- ✅ **Wildcard support** - Supports subdomains
- ✅ **TLS 1.2 & 1.3** - Modern encryption
- ✅ **A+ SSL rating** - Industry standard

### Certificate Lifecycle

```
Day 1:   Deploy → SSL certificate provisioned automatically
Day 60:  Render starts renewal process
Day 90:  New certificate issued automatically
Day 180: Process repeats
```

**You don't need to do anything!** Render handles everything.

---

## ✅ Verify HTTPS is Working

### Test 1: Check Your URLs

```bash
# Open in browser:
https://autoos-frontend.onrender.com
https://autoos-backend.onrender.com

# Look for:
# ✅ Green padlock 🔒 in address bar
# ✅ "Connection is secure" message
# ✅ No warnings or errors
```

### Test 2: Test SSL Certificate

```bash
# Check SSL certificate details:
curl -I https://autoos-backend.onrender.com

# Should show:
# HTTP/2 200
# server: Render
```

### Test 3: SSL Labs Test

```bash
# 1. Go to: https://www.ssllabs.com/ssltest/
# 2. Enter: autoos-backend.onrender.com
# 3. Click "Submit"
# 4. Wait for results

# Expected grade: A or A+
```

### Test 4: Test API Endpoints

```bash
# Test health endpoint:
curl https://autoos-backend.onrender.com/health

# Should return:
# {"status": "healthy"}

# Test with browser:
# Open: https://autoos-backend.onrender.com/docs
# Should show: FastAPI Swagger UI
```

---

## 🔒 Security Best Practices

### 1. Force HTTPS Redirects

Render automatically redirects HTTP → HTTPS, but you can enforce it in code:

```python
# src/autoos/intent/api.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Force HTTPS in production
        if request.url.scheme == "http" and "onrender.com" in str(request.url):
            url = request.url.replace(scheme="https")
            return RedirectResponse(url=url, status_code=301)
        return await call_next(request)

app.add_middleware(HTTPSRedirectMiddleware)
```

### 2. Update CORS Settings

```python
# src/autoos/intent/api.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://autoos-frontend.onrender.com",
        "https://autoos.com",  # If using custom domain
        "https://www.autoos.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Set Secure Headers

```python
# src/autoos/intent/api.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "autoos-backend.onrender.com",
        "api.autoos.com"  # If using custom domain
    ]
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### 4. Update Stripe Webhook URL

After deployment, update your Stripe webhook:

```bash
# 1. Go to: https://dashboard.stripe.com/test/webhooks
# 2. Click your webhook
# 3. Update URL to:
https://autoos-backend.onrender.com/api/payment/webhook

# 4. Save
# 5. Copy the webhook secret
# 6. Update in Render:
#    - Go to "autoos-backend" service
#    - Environment tab
#    - Update STRIPE_WEBHOOK_SECRET
#    - Save
```

---

## 🐛 Troubleshooting

### Issue 1: "Not Secure" Warning

**Cause**: Mixed content (HTTP resources on HTTPS page)

**Fix**:
```bash
# Check your code for HTTP URLs:
grep -r "http://" frontend/web/src/

# Change all to HTTPS or relative URLs:
# Bad:  src="http://example.com/image.jpg"
# Good: src="https://example.com/image.jpg"
# Good: src="/images/image.jpg"
```

### Issue 2: SSL Certificate Not Issued

**Cause**: DNS not propagated yet

**Fix**:
```bash
# Wait 5-60 minutes for DNS propagation

# Check DNS status:
dig autoos.com
nslookup autoos.com

# Check Render dashboard for certificate status
```

### Issue 3: CORS Errors

**Cause**: Frontend URL not in CORS allowed origins

**Fix**:
```python
# Update CORS settings in src/autoos/intent/api.py
allow_origins=[
    "https://autoos-frontend.onrender.com",  # Add your frontend URL
]
```

### Issue 4: API Connection Failed

**Cause**: Wrong API URL in frontend

**Fix**:
```bash
# In Render Dashboard:
# 1. Go to "autoos-frontend" service
# 2. Environment tab
# 3. Check NEXT_PUBLIC_API_URL value
# 4. Should be: https://autoos-backend.onrender.com
# 5. Update if wrong
# 6. Save (auto-redeploys)
```

---

## 📊 HTTPS Status Checklist

### Pre-Deployment
- [ ] Code pushed to GitHub
- [ ] render.yaml configured
- [ ] Environment variables ready

### Deployment
- [ ] Deployed to Render via Blueprint
- [ ] Backend service running
- [ ] Frontend service running
- [ ] Both services have HTTPS URLs

### Configuration
- [ ] Frontend has backend HTTPS URL
- [ ] CORS settings updated
- [ ] Security headers added
- [ ] Stripe webhook URL updated

### Verification
- [ ] Green padlock in browser
- [ ] No mixed content warnings
- [ ] SSL Labs test passes (A/A+)
- [ ] API endpoints work over HTTPS
- [ ] Frontend loads over HTTPS
- [ ] All features work correctly

### Custom Domain (Optional)
- [ ] Domain purchased/registered
- [ ] DNS records added
- [ ] DNS propagated
- [ ] SSL certificate issued
- [ ] Custom domain works
- [ ] Environment variables updated

---

## 💰 Cost Summary

| Item | Cost | Notes |
|------|------|-------|
| **Render Hosting** | FREE | Free tier available |
| **SSL Certificate** | FREE | Included with Render |
| **Auto-Renewal** | FREE | Automatic |
| **Custom Domain** | $0-12/year | Optional |
| **Total** | **$0-12/year** | HTTPS is FREE! |

---

## 🎉 Success!

Your AUTOOS app now has secure HTTPS links on Render!

**What You Have**:
- ✅ Secure HTTPS URLs
- ✅ FREE SSL certificates
- ✅ Auto-renewal configured
- ✅ Green padlock in browser
- ✅ Production-ready security

**Your HTTPS URLs**:
```
Frontend: https://autoos-frontend.onrender.com
Backend:  https://autoos-backend.onrender.com
```

**Next Steps**:
1. Test all features work over HTTPS
2. Update Stripe webhook URL
3. Share your secure link with users
4. (Optional) Add custom domain

**Your app is secure and ready for users! 🚀**

---

## 📞 Support

**Render Documentation**:
- SSL/TLS: https://render.com/docs/tls-ssl
- Custom Domains: https://render.com/docs/custom-domains
- Troubleshooting: https://render.com/docs/troubleshooting

**Need Help?**:
- Render Community: https://community.render.com
- Render Support: support@render.com

---

**Remember**: HTTPS on Render is automatic and FREE. Just deploy and you're secure! 🔒✨
