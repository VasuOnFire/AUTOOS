# 🔧 Render Deployment Troubleshooting Guide

Complete guide to fix common errors when deploying AUTOOS Omega to Render.

---

## ⚠️ Common Build Warnings (Safe to Ignore)

### Warning: update-alternatives man page warnings

```
update-alternatives: warning: skip creation of /usr/share/man/man1/lzma.1.gz
```

**Status**: ✅ **SAFE TO IGNORE**

**Explanation**:
- These are warnings from the package manager installing compression utilities
- They occur during system package installation
- They do NOT affect your application
- Your app will work perfectly fine

**Why it happens**:
- Render's build environment doesn't include man (manual) pages
- Some packages try to register man pages that don't exist
- This is normal and expected

**Fix** (Optional - to clean up logs):
- Use the provided `render-build.sh` script
- It filters out these warnings for cleaner logs

---

## 🚨 Critical Errors & Solutions

### Error 1: Module Not Found

```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause**: Dependencies not installed

**Solution**:
```bash
# Check requirements.txt exists
# Verify buildCommand in render.yaml:
buildCommand: pip install -r requirements.txt

# Or use the build script:
buildCommand: bash render-build.sh
```

### Error 2: Port Binding Error

```
Error: Cannot bind to port 8000
```

**Cause**: Not using Render's $PORT variable

**Solution**:
```python
# In src/autoos/intent/api.py
# Make sure you're using the PORT environment variable

import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

**In render.yaml**:
```yaml
startCommand: uvicorn src.autoos.intent.api:app --host 0.0.0.0 --port $PORT
```

### Error 3: Database Connection Failed

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Cause**: Database not ready or wrong connection string

**Solution**:
```bash
# 1. Check database is created in Render dashboard
# 2. Verify DATABASE_URL environment variable
# 3. Wait for database to be fully provisioned (takes 2-3 minutes)

# In render.yaml, ensure:
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: autoos-db
      property: connectionString
```

### Error 4: Redis Connection Failed

```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Cause**: Redis not ready or wrong connection string

**Solution**:
```bash
# 1. Check Redis is created in Render dashboard
# 2. Verify REDIS_URL environment variable
# 3. Redis free tier expires after 30 days - check if still active

# In render.yaml, ensure:
envVars:
  - key: REDIS_URL
    fromDatabase:
      name: autoos-redis
      property: connectionString
```

### Error 5: Build Timeout

```
Build exceeded maximum time limit
```

**Cause**: Build taking too long (>15 minutes on free tier)

**Solution**:
```bash
# 1. Optimize requirements.txt - remove unused packages
# 2. Use build cache
# 3. Consider upgrading to paid tier for faster builds

# Add to render.yaml:
buildCommand: pip install --no-cache-dir -r requirements.txt
```

### Error 6: Out of Memory

```
Killed
Process exited with code 137
```

**Cause**: Build or runtime using too much memory

**Solution**:
```bash
# Free tier has 512MB RAM limit

# 1. Reduce memory usage in code
# 2. Optimize imports (lazy loading)
# 3. Consider upgrading to paid tier

# In your code, use lazy imports:
def heavy_function():
    import heavy_library  # Import only when needed
    return heavy_library.do_something()
```

### Error 7: Environment Variable Not Set

```
KeyError: 'STRIPE_SECRET_KEY'
```

**Cause**: Required environment variable missing

**Solution**:
```bash
# 1. Go to Render Dashboard
# 2. Select your service
# 3. Click "Environment" tab
# 4. Add missing variables:

STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
OPENAI_API_KEY=sk-your_key_here
```

### Error 8: Python Version Mismatch

```
ERROR: This package requires Python >=3.11
```

**Cause**: Wrong Python version

**Solution**:
```yaml
# In render.yaml:
envVars:
  - key: PYTHON_VERSION
    value: 3.11.0

# Or create runtime.txt:
python-3.11.0
```

### Error 9: Frontend Build Failed

```
npm ERR! code ELIFECYCLE
```

**Cause**: Node.js build error

**Solution**:
```bash
# 1. Check package.json exists in frontend/web
# 2. Verify Node version

# In render.yaml:
rootDir: frontend/web
buildCommand: npm install && npm run build
envVars:
  - key: NODE_VERSION
    value: 18.17.0
```

### Error 10: Health Check Failed

```
Service failed health check
```

**Cause**: App not responding on expected port

**Solution**:
```bash
# 1. Ensure app listens on 0.0.0.0 (not localhost)
# 2. Use $PORT environment variable
# 3. Add health check endpoint

# In src/autoos/intent/api.py:
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## 🔍 Debugging Steps

### Step 1: Check Build Logs

```bash
# In Render Dashboard:
# 1. Go to your service
# 2. Click "Logs" tab
# 3. Look for errors in build phase
# 4. Note the exact error message
```

### Step 2: Check Runtime Logs

```bash
# In Render Dashboard:
# 1. Go to your service
# 2. Click "Logs" tab
# 3. Filter by "All logs"
# 4. Look for errors after "Starting service"
```

### Step 3: Verify Environment Variables

```bash
# In Render Dashboard:
# 1. Go to your service
# 2. Click "Environment" tab
# 3. Verify all required variables are set
# 4. Check for typos in variable names
```

### Step 4: Test Locally

```bash
# Test your app locally first:
cd /path/to/AUTOOS

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://localhost/autoos
export REDIS_URL=redis://localhost:6379
export STRIPE_SECRET_KEY=sk_test_your_key

# Run the app
uvicorn src.autoos.intent.api:app --reload

# Test in browser:
http://localhost:8000/docs
```

### Step 5: Check Service Status

```bash
# In Render Dashboard:
# 1. Go to your service
# 2. Check status indicator:
#    - Green = Running
#    - Yellow = Building
#    - Red = Failed
# 3. Click "Events" to see deployment history
```

---

## 📊 Performance Issues

### Issue: Slow Build Times

**Solution**:
```yaml
# Use build cache
buildCommand: pip install --cache-dir /tmp/pip-cache -r requirements.txt

# Or upgrade to paid tier for faster builds
```

### Issue: Slow Response Times

**Solution**:
```bash
# 1. Check if using free tier (spins down after inactivity)
# 2. Upgrade to paid tier for always-on service
# 3. Optimize database queries
# 4. Add caching with Redis
```

### Issue: Database Queries Slow

**Solution**:
```python
# Add database indexes
# Use connection pooling
# Optimize queries

# In your models:
class User(Base):
    __tablename__ = "users"
    email = Column(String, index=True)  # Add index
```

---

## 🔐 Security Issues

### Issue: Exposed API Keys

**Solution**:
```bash
# NEVER commit API keys to Git
# Use environment variables only

# Check .gitignore includes:
.env
.env.local
.env.production
```

### Issue: CORS Errors

**Solution**:
```python
# In src/autoos/intent/api.py:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://autoos-frontend.onrender.com",
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 💾 Database Issues

### Issue: Database Not Created

**Solution**:
```bash
# 1. Check render.yaml has database definition
# 2. Verify database appears in Render dashboard
# 3. Wait 2-3 minutes for provisioning
# 4. Check "Databases" section in dashboard
```

### Issue: Migrations Failed

**Solution**:
```bash
# Run migrations manually:
# 1. Connect to your service shell (if available)
# 2. Run: alembic upgrade head

# Or add to buildCommand:
buildCommand: pip install -r requirements.txt && alembic upgrade head
```

### Issue: Database Connection Pool Exhausted

**Solution**:
```python
# In your database config:
engine = create_engine(
    DATABASE_URL,
    pool_size=5,  # Limit connections
    max_overflow=10,
    pool_pre_ping=True  # Check connections before use
)
```

---

## 📱 Frontend Issues

### Issue: API URL Not Set

**Solution**:
```bash
# In Render Dashboard (frontend service):
# Environment tab:
NEXT_PUBLIC_API_URL=https://autoos-backend.onrender.com
```

### Issue: Build Fails - Missing Dependencies

**Solution**:
```bash
# Check package.json in frontend/web
# Ensure all dependencies are listed

# In render.yaml:
buildCommand: npm ci && npm run build  # Use 'ci' for clean install
```

---

## 🆘 Getting Help

### Render Support

- **Documentation**: https://render.com/docs
- **Community**: https://community.render.com
- **Support**: support@render.com

### Check Service Status

- **Render Status**: https://status.render.com
- Check if there are any ongoing incidents

### Useful Commands

```bash
# View logs in real-time
# (In Render Dashboard, enable "Live tail")

# Download logs
# (In Render Dashboard, click "Download logs")

# Restart service
# (In Render Dashboard, click "Manual Deploy" > "Clear build cache & deploy")
```

---

## ✅ Deployment Checklist

Before deploying, verify:

- [ ] Code pushed to GitHub
- [ ] render.yaml configured correctly
- [ ] requirements.txt includes all dependencies
- [ ] Environment variables set in Render
- [ ] Database and Redis services created
- [ ] Build command correct
- [ ] Start command correct
- [ ] Health check endpoint exists
- [ ] CORS configured for frontend URL
- [ ] API keys are valid (Stripe, OpenAI)

---

## 🎯 Quick Fixes

### Fix 1: Clean Build

```bash
# In Render Dashboard:
# 1. Go to service
# 2. Click "Manual Deploy"
# 3. Select "Clear build cache & deploy"
# 4. Wait for rebuild
```

### Fix 2: Restart Service

```bash
# In Render Dashboard:
# 1. Go to service
# 2. Click "Manual Deploy"
# 3. Select "Deploy latest commit"
```

### Fix 3: Check Logs

```bash
# In Render Dashboard:
# 1. Go to service
# 2. Click "Logs"
# 3. Enable "Live tail"
# 4. Look for errors
```

---

## 📞 Still Having Issues?

If you're still experiencing problems:

1. **Check the logs** - Most errors are explained in the logs
2. **Verify environment variables** - Missing variables cause most issues
3. **Test locally first** - Ensure app works on your machine
4. **Check Render status** - Verify no ongoing incidents
5. **Ask for help** - Render community is very helpful

**Remember**: The man page warnings you saw are **NOT errors** and can be safely ignored! Your app will work fine. 🎉

---

**Good luck with your deployment! 🚀**
