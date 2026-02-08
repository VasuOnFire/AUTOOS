# 🔒 HTTPS Setup Guide for AUTOOS

Complete guide to get secure HTTPS links for your AUTOOS application - **100% FREE!**

---

## 🎯 What You'll Get

After following this guide, you'll have:
- ✅ `https://autoos.vercel.app` (Web App)
- ✅ `https://autoos.up.railway.app` (Backend API)
- ✅ `https://yourdomain.com` (Custom Domain - Optional)
- ✅ Automatic SSL certificates
- ✅ Secure encrypted connections
- ✅ Green padlock in browser

**Total Cost: $0** (completely free!)

---

## 🚀 Quick Start (5 Minutes)

### Option 1: Automatic HTTPS (Easiest - FREE)

When you deploy to these platforms, HTTPS is **automatic**:

```bash
# 1. Deploy Backend to Railway
railway up
# You get: https://autoos.up.railway.app ✅

# 2. Deploy Frontend to Vercel
vercel --prod
# You get: https://autoos.vercel.app ✅

# Done! Both have HTTPS automatically! 🎉
```

**No configuration needed!** SSL certificates are automatic and free.

---

## 📋 Method 1: Free Hosting with Auto-HTTPS

### Backend (Railway)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up

# 5. Get your HTTPS URL
railway domain

# Output: https://autoos-production.up.railway.app
```

**Your Backend API**: `https://autoos-production.up.railway.app`
- ✅ HTTPS enabled automatically
- ✅ SSL certificate included
- ✅ Renews automatically
- ✅ Cost: FREE

### Frontend (Vercel)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Navigate to web app
cd frontend/web

# 3. Deploy
vercel --prod

# Output: https://autoos.vercel.app
```

**Your Web App**: `https://autoos.vercel.app`
- ✅ HTTPS enabled automatically
- ✅ SSL certificate included
- ✅ Global CDN
- ✅ Cost: FREE

### Alternative: Render.com

```bash
# 1. Sign up at render.com

# 2. Connect GitHub repo

# 3. Deploy

# You get: https://autoos.onrender.com
```

**Your App**: `https://autoos.onrender.com`
- ✅ HTTPS automatic
- ✅ Cost: FREE

---

## 📋 Method 2: Custom Domain with FREE HTTPS

### Step 1: Get a Domain

#### Option A: Free Domain (Freenom)

```bash
# 1. Go to freenom.com

# 2. Search for domain
# Available: .tk, .ml, .ga, .cf, .gq

# 3. Register (FREE for 12 months)
# Example: autoos.tk, autoos.ml

# 4. Renew every 12 months (still free)
```

**Cost**: $0 forever

#### Option B: Paid Domain (Recommended)

```bash
# Buy from:
# - Namecheap: $8-12/year
# - Google Domains: $12/year
# - Cloudflare: $10/year

# Example: autoos.com, autoos.io, autoos.app
```

**Cost**: $8-12/year

### Step 2: Connect Domain to Vercel (Web App)

```bash
# 1. Go to Vercel Dashboard
# vercel.com/dashboard

# 2. Select your project

# 3. Go to Settings > Domains

# 4. Add your domain
# Enter: autoos.com

# 5. Vercel will show DNS records to add

# 6. Add these records to your domain:
# Type: A
# Name: @
# Value: 76.76.21.21

# Type: CNAME
# Name: www
# Value: cname.vercel-dns.com

# 7. Wait 5-60 minutes for DNS propagation

# 8. Vercel automatically provisions SSL certificate

# Done! Your site is now at: https://autoos.com
```

**Your Web App**: `https://autoos.com`
- ✅ HTTPS automatic
- ✅ SSL certificate free
- ✅ Auto-renews
- ✅ Cost: $0 (domain cost only)

### Step 3: Connect Domain to Railway (Backend)

```bash
# 1. Go to Railway Dashboard
# railway.app/dashboard

# 2. Select your project

# 3. Go to Settings > Domains

# 4. Click "Add Domain"

# 5. Enter: api.autoos.com

# 6. Railway will show DNS record

# 7. Add CNAME record to your domain:
# Type: CNAME
# Name: api
# Value: autoos-production.up.railway.app

# 8. Wait for DNS propagation

# Done! Your API is now at: https://api.autoos.com
```

**Your Backend API**: `https://api.autoos.com`
- ✅ HTTPS automatic
- ✅ SSL certificate free
- ✅ Cost: $0

---

## 📋 Method 3: Cloudflare (FREE SSL + CDN)

Cloudflare provides FREE SSL certificates and makes your site faster!

### Setup Cloudflare

```bash
# 1. Sign up at cloudflare.com (FREE)

# 2. Add your domain
# Click "Add Site"
# Enter: autoos.com

# 3. Cloudflare scans your DNS records

# 4. Update nameservers at your domain registrar
# Change to Cloudflare nameservers:
# - ns1.cloudflare.com
# - ns2.cloudflare.com

# 5. Wait for activation (5-60 minutes)

# 6. Configure SSL/TLS
# Go to SSL/TLS > Overview
# Select: "Full (strict)"

# 7. Enable "Always Use HTTPS"
# Go to SSL/TLS > Edge Certificates
# Turn on "Always Use HTTPS"

# 8. Enable "Automatic HTTPS Rewrites"
# Turn on "Automatic HTTPS Rewrites"

# Done! Your site now has HTTPS: https://autoos.com
```

**Benefits**:
- ✅ FREE SSL certificate
- ✅ Global CDN (faster loading)
- ✅ DDoS protection
- ✅ Web Application Firewall
- ✅ Analytics
- ✅ Auto-minify CSS/JS
- ✅ Cost: $0

---

## 📋 Method 4: Let's Encrypt (Self-Hosted)

If you're hosting on your own server, use Let's Encrypt for FREE SSL.

### Install Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx

# macOS
brew install certbot
```

### Get SSL Certificate

```bash
# 1. Stop any service using port 80
sudo systemctl stop nginx

# 2. Get certificate
sudo certbot certonly --standalone -d autoos.com -d www.autoos.com

# 3. Certbot will ask for email
# Enter your email for renewal notifications

# 4. Agree to terms

# 5. Certificate saved to:
# /etc/letsencrypt/live/autoos.com/fullchain.pem
# /etc/letsencrypt/live/autoos.com/privkey.pem
```

### Configure Nginx

```bash
# Edit Nginx config
sudo nano /etc/nginx/sites-available/autoos

# Add this configuration:
server {
    listen 80;
    server_name autoos.com www.autoos.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name autoos.com www.autoos.com;

    ssl_certificate /etc/letsencrypt/live/autoos.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/autoos.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Save and exit (Ctrl+X, Y, Enter)

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Auto-Renewal

```bash
# Certbot automatically sets up renewal
# Test renewal
sudo certbot renew --dry-run

# Renewal happens automatically every 60 days
# Check renewal timer
sudo systemctl status certbot.timer
```

**Your Site**: `https://autoos.com`
- ✅ FREE SSL certificate
- ✅ Auto-renews every 90 days
- ✅ Cost: $0

---

## 🔧 Update Your App to Use HTTPS

### Update Frontend Environment Variables

```bash
# frontend/web/.env.production
NEXT_PUBLIC_API_URL=https://api.autoos.com
NEXT_PUBLIC_WS_URL=wss://api.autoos.com
```

### Update Backend CORS Settings

```python
# src/autoos/intent/api.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://autoos.com",
        "https://www.autoos.com",
        "https://autoos.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Force HTTPS Redirects

```python
# src/autoos/intent/api.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.scheme == "http":
            url = request.url.replace(scheme="https")
            return RedirectResponse(url=url, status_code=301)
        return await call_next(request)

app.add_middleware(HTTPSRedirectMiddleware)
```

---

## ✅ Verify HTTPS is Working

### Test Your HTTPS Setup

```bash
# 1. Check SSL certificate
curl -I https://autoos.com

# Should show: HTTP/2 200

# 2. Test SSL grade
# Go to: ssllabs.com/ssltest
# Enter: autoos.com
# Should get: A or A+ rating

# 3. Check browser
# Open: https://autoos.com
# Look for green padlock 🔒 in address bar

# 4. Test API
curl https://api.autoos.com/health

# Should return: {"status": "healthy"}
```

### Common Issues

#### Issue 1: "Not Secure" Warning

```bash
# Cause: Mixed content (HTTP resources on HTTPS page)

# Fix: Update all URLs to HTTPS
# Check for:
# - <img src="http://...">
# - <script src="http://...">
# - fetch("http://...")

# Change all to HTTPS or relative URLs
```

#### Issue 2: Certificate Not Valid

```bash
# Cause: DNS not propagated yet

# Fix: Wait 5-60 minutes for DNS propagation

# Check DNS:
dig autoos.com
nslookup autoos.com
```

#### Issue 3: ERR_CERT_COMMON_NAME_INVALID

```bash
# Cause: Certificate doesn't match domain

# Fix: Regenerate certificate with correct domain
sudo certbot delete --cert-name autoos.com
sudo certbot certonly --standalone -d autoos.com -d www.autoos.com
```

---

## 🎯 Complete HTTPS Setup Checklist

### Pre-Deployment

- [ ] Choose hosting platform (Vercel/Railway recommended)
- [ ] Decide on domain (free subdomain or custom)
- [ ] Sign up for hosting accounts

### Deployment

- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Vercel
- [ ] Verify both have HTTPS URLs
- [ ] Test API endpoints work over HTTPS
- [ ] Test web app loads over HTTPS

### Custom Domain (Optional)

- [ ] Purchase or get free domain
- [ ] Add domain to Vercel
- [ ] Add subdomain to Railway (api.yourdomain.com)
- [ ] Update DNS records
- [ ] Wait for DNS propagation
- [ ] Verify SSL certificates issued
- [ ] Test custom domain works

### Configuration

- [ ] Update frontend API URL to HTTPS
- [ ] Update backend CORS settings
- [ ] Add HTTPS redirect middleware
- [ ] Update all internal URLs to HTTPS
- [ ] Test all features work over HTTPS

### Verification

- [ ] Check green padlock in browser
- [ ] Test SSL certificate at ssllabs.com
- [ ] Verify no mixed content warnings
- [ ] Test on multiple browsers
- [ ] Test on mobile devices
- [ ] Verify auto-renewal is configured

---

## 💰 Cost Comparison

| Method | SSL Cost | Domain Cost | Total/Year |
|--------|----------|-------------|------------|
| **Vercel + Railway** | FREE | FREE subdomain | **$0** |
| **Vercel + Railway + Freenom** | FREE | FREE | **$0** |
| **Vercel + Railway + Namecheap** | FREE | $10 | **$10** |
| **Cloudflare** | FREE | $10 | **$10** |
| **Let's Encrypt + VPS** | FREE | $10 + $5/mo VPS | **$70** |
| **Paid SSL** | $50-200 | $10 | **$60-210** |

**Recommended**: Vercel + Railway = **$0/year** ✅

---

## 🚀 Quick Setup Commands

### Complete FREE Setup (5 Minutes)

```bash
# 1. Deploy Backend
npm install -g @railway/cli
railway login
railway init
railway up
railway domain
# Save URL: https://autoos.up.railway.app

# 2. Deploy Frontend
npm install -g vercel
cd frontend/web
# Update .env.production with Railway URL
echo "NEXT_PUBLIC_API_URL=https://autoos.up.railway.app" > .env.production
vercel --prod
# Save URL: https://autoos.vercel.app

# 3. Done! You have HTTPS! 🎉
# Web App: https://autoos.vercel.app
# API: https://autoos.up.railway.app
```

---

## 📱 Mobile App HTTPS

Mobile apps automatically use HTTPS when connecting to your API:

```javascript
// frontend/mobile/config.js
export const API_URL = 'https://api.autoos.com';

// All requests will use HTTPS automatically
fetch(`${API_URL}/workflows`)
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 🖥️ Desktop App HTTPS

Desktop apps also use HTTPS for API calls:

```javascript
// frontend/desktop/main.js
const API_URL = 'https://api.autoos.com';

// Electron automatically handles HTTPS
fetch(`${API_URL}/workflows`)
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 🎓 Understanding HTTPS

### What is HTTPS?

HTTPS = HTTP + SSL/TLS encryption

**Benefits**:
- 🔒 Encrypted data transmission
- ✅ Verified server identity
- 🛡️ Protection from man-in-the-middle attacks
- 📈 Better SEO ranking
- 🚀 Required for modern web features
- 💳 Required for payment processing

### How SSL Certificates Work

1. **Browser** requests website
2. **Server** sends SSL certificate
3. **Browser** verifies certificate
4. **Encrypted connection** established
5. **Data** transmitted securely

### Certificate Types

| Type | Validation | Cost | Use Case |
|------|------------|------|----------|
| **Domain Validated (DV)** | Domain only | FREE | Most websites |
| **Organization Validated (OV)** | Company verified | $50-200/year | Business sites |
| **Extended Validation (EV)** | Full verification | $200-500/year | Banks, e-commerce |

**For AUTOOS**: DV certificate (FREE) is perfect! ✅

---

## 🎉 You're Done!

Your AUTOOS app now has secure HTTPS links!

**What You Achieved**:
- ✅ Secure encrypted connections
- ✅ Green padlock in browser
- ✅ Professional HTTPS URLs
- ✅ FREE SSL certificates
- ✅ Auto-renewal configured
- ✅ Ready for production

**Your HTTPS URLs**:
- Web App: `https://autoos.vercel.app`
- Backend API: `https://autoos.up.railway.app`
- Custom Domain: `https://autoos.com` (optional)

**Total Cost**: $0 (completely free!)

**Next Steps**:
1. Share your HTTPS link with users
2. Submit to Product Hunt
3. Add to your resume/portfolio
4. Start getting users!

**Good luck! 🚀**
