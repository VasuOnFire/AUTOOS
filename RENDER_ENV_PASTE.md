# 🎯 Render Environment Variables - Copy & Paste Method

**Great news!** You CAN add environment variables using the "Add from .env" feature!

---

## 📋 Quick Method (Copy & Paste)

### Step 1: Copy the Environment Variables

Copy everything below (Ctrl+A, Ctrl+C):

```env
PYTHON_VERSION=3.11.0
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production
```

### Step 2: Paste in Render

1. Go to your service in Render dashboard
2. Click **"Environment"** tab
3. Click **"Add from .env"** button
4. Paste the copied text
5. Click **"Add variables"**

**Done!** ✅

---

## 🔐 Complete Environment Variables

Here's the COMPLETE list with all optional features:

### For Backend Service

```env
# Required - Basic Configuration
PYTHON_VERSION=3.11.0
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production

# Optional - AI Features (add later)
OPENAI_API_KEY=sk-your-key-here

# Optional - Payment Features (add later)
STRIPE_SECRET_KEY=sk_test_your-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-key
STRIPE_WEBHOOK_SECRET=whsec_your-secret

# Optional - Email Notifications (add later)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional - Social Login (add later)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### For Frontend Service

```env
NODE_VERSION=18.17.0
NEXT_PUBLIC_API_URL=https://autoos-backend.onrender.com
```

---

## 🚀 Deployment Steps with Environment Variables

### Step 1: Deploy Backend

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub: **VasuOnFire/AUTOOS**
4. Configure:
   - **Name**: `autoos-backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn src.autoos.intent.api_minimal:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables**:
   - Click **"Environment"** tab
   - Click **"Add from .env"**
   - Paste the backend variables (from above)
   - Click **"Add variables"**

6. Click **"Create Web Service"**

### Step 2: Create Database

1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `autoos-db`
   - **Plan**: Free
3. Click **"Create Database"**
4. Copy the **Internal Database URL**

### Step 3: Add Database URL to Backend

1. Go back to your backend service
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add:
   - **Key**: `DATABASE_URL`
   - **Value**: (paste the database URL)
5. Click **"Save"**

### Step 4: Create Redis

1. Click **"New +"** → **"Redis"**
2. Configure:
   - **Name**: `autoos-redis`
   - **Plan**: Free
3. Click **"Create Redis"**
4. Copy the **Internal Redis URL**

### Step 5: Add Redis URL to Backend

1. Go back to your backend service
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add:
   - **Key**: `REDIS_URL`
   - **Value**: (paste the Redis URL)
5. Click **"Save"**

### Step 6: Deploy Frontend

1. Click **"New +"** → **"Static Site"**
2. Connect GitHub: **VasuOnFire/AUTOOS**
3. Configure:
   - **Name**: `autoos-frontend`
   - **Root Directory**: `frontend/web`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `frontend/web/out`

4. **Add Environment Variables**:
   - Click **"Environment"** tab
   - Click **"Add from .env"**
   - Paste:
     ```env
     NODE_VERSION=18.17.0
     NEXT_PUBLIC_API_URL=https://autoos-backend.onrender.com
     ```
   - Click **"Add variables"**

5. Click **"Create Static Site"**

---

## 📝 Environment Variables Explained

### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `PYTHON_VERSION` | `3.11.0` | Python version for backend |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `ENVIRONMENT` | `production` | Environment mode |
| `DATABASE_URL` | (from database) | PostgreSQL connection |
| `REDIS_URL` | (from Redis) | Redis connection |
| `NODE_VERSION` | `18.17.0` | Node.js version |
| `NEXT_PUBLIC_API_URL` | (backend URL) | Frontend API endpoint |

### Optional Variables (Add Later)

| Variable | Description | When to Add |
|----------|-------------|-------------|
| `OPENAI_API_KEY` | OpenAI API key | For AI features |
| `STRIPE_SECRET_KEY` | Stripe secret key | For payments |
| `STRIPE_PUBLISHABLE_KEY` | Stripe public key | For payments |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | For payment webhooks |
| `SMTP_HOST` | Email server | For email notifications |
| `SMTP_PORT` | Email port | For email notifications |
| `SMTP_USER` | Email username | For email notifications |
| `SMTP_PASSWORD` | Email password | For email notifications |
| `GOOGLE_CLIENT_ID` | Google OAuth ID | For Google login |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | For Google login |

---

## 🎯 Quick Copy-Paste Templates

### Minimal Setup (Works Immediately)

```env
PYTHON_VERSION=3.11.0
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production
```

### With AI Features

```env
PYTHON_VERSION=3.11.0
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production
OPENAI_API_KEY=sk-your-openai-key-here
```

### With Payment Features

```env
PYTHON_VERSION=3.11.0
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
```

### Full Setup (All Features)

```env
PYTHON_VERSION=3.11.0
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production
OPENAI_API_KEY=sk-your-openai-key-here
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

---

## 🔧 How to Get API Keys

### OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Click **"Create new secret key"**
3. Copy the key (starts with `sk-`)
4. Paste in Render

### Stripe Keys

1. Go to: https://dashboard.stripe.com/test/apikeys
2. Copy **"Secret key"** (starts with `sk_test_`)
3. Copy **"Publishable key"** (starts with `pk_test_`)
4. For webhook secret:
   - Go to: https://dashboard.stripe.com/test/webhooks
   - Create endpoint: `https://autoos-backend.onrender.com/webhooks/stripe`
   - Copy the signing secret (starts with `whsec_`)

### Gmail SMTP (for emails)

1. Go to: https://myaccount.google.com/apppasswords
2. Create app password
3. Use:
   - Host: `smtp.gmail.com`
   - Port: `587`
   - User: your Gmail address
   - Password: the app password

### Google OAuth (for social login)

1. Go to: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID
3. Add authorized redirect: `https://autoos-backend.onrender.com/auth/oauth/google/callback`
4. Copy Client ID and Client Secret

---

## ✅ Verification

After adding environment variables:

1. **Check Backend**:
   ```
   https://autoos-backend.onrender.com/health
   ```
   Should return: `{"status": "healthy"}`

2. **Check Frontend**:
   ```
   https://autoos-frontend.onrender.com
   ```
   Should show the homepage

3. **Check API Docs**:
   ```
   https://autoos-backend.onrender.com/docs
   ```
   Should show interactive API documentation

---

## 🐛 Troubleshooting

### Issue: "Add variables" button is disabled

**Solution**: Make sure you pasted valid `.env` format:
```
KEY=VALUE
KEY2=VALUE2
```

### Issue: Variables not working

**Solution**: 
1. Check for typos in variable names
2. Make sure no extra spaces
3. Restart the service after adding variables

### Issue: Database/Redis connection fails

**Solution**:
1. Make sure you copied the **Internal URL** (not External)
2. Check the URL format is correct
3. Wait 2-3 minutes for services to connect

---

## 🎉 Success!

Your environment variables are now configured!

**Next Steps**:
1. ✅ Deploy your services
2. ✅ Test the endpoints
3. ✅ Add optional API keys later
4. ✅ Monitor logs for any issues

---

**Built with ❤️ by Vasu (@VasuOnFire)**

**Need help?** Check:
- `START_HERE_DEPLOYMENT.md` - Deployment guide
- `RENDER_TROUBLESHOOTING.md` - Common issues
- `API_KEYS_SETUP_GUIDE.md` - How to get API keys
