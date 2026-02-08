# 🔧 Render Deployment Error Fixes

Quick fixes for common Render deployment errors.

---

## 🚨 Error: "Module not found"

### Symptoms:
```
ModuleNotFoundError: No module named 'autoos'
```

### Cause:
Python can't find the autoos module

### Fix:
Update `render.yaml` startCommand:

```yaml
startCommand: PYTHONPATH=/opt/render/project/src:$PYTHONPATH uvicorn src.autoos.intent.api:app --host 0.0.0.0 --port $PORT
```

Or use the start script:
```yaml
startCommand: bash start.sh
```

---

## 🚨 Error: "Database connection failed"

### Symptoms:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

### Cause:
Database not ready or DATABASE_URL not set

### Fix:

**Option 1: Wait for database**
- Database takes 2-3 minutes to provision
- Check Render dashboard → Databases
- Wait until status shows "Available"

**Option 2: Check environment variable**
```bash
# In Render Dashboard:
# 1. Go to backend service
# 2. Click "Environment" tab
# 3. Verify DATABASE_URL is set
# 4. Should look like: postgresql://user:pass@host/db
```

**Option 3: Make database optional (temporary)**
- Use the fixed API that handles missing database gracefully
- Copy `api_fixed.py` to `api.py`

---

## 🚨 Error: "Redis connection failed"

### Symptoms:
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

### Cause:
Redis not ready or REDIS_URL not set

### Fix:

**Option 1: Check Redis status**
- Go to Render dashboard → Databases
- Check Redis status
- Note: Free Redis expires after 30 days

**Option 2: Make Redis optional**
- Use the fixed API that handles missing Redis gracefully

---

## 🚨 Error: "Port binding failed"

### Symptoms:
```
Error: Cannot bind to port 8000
OSError: [Errno 98] Address already in use
```

### Cause:
Not using Render's $PORT variable

### Fix:
Update startCommand in `render.yaml`:

```yaml
startCommand: uvicorn src.autoos.intent.api:app --host 0.0.0.0 --port $PORT
```

Make sure you're using `$PORT` (not hardcoded 8000)

---

## 🚨 Error: "Build timeout"

### Symptoms:
```
Build exceeded maximum time limit (15 minutes)
```

### Cause:
Build taking too long

### Fix:

**Option 1: Optimize requirements.txt**
```bash
# Remove unused packages
# Keep only essential ones for MVP
```

**Option 2: Use build cache**
```yaml
buildCommand: pip install --cache-dir /tmp/pip-cache -r requirements.txt
```

**Option 3: Upgrade to paid tier**
- Paid tier has longer build timeout
- Faster build servers

---

## 🚨 Error: "Health check failed"

### Symptoms:
```
Service failed health check
Your service is not responding
```

### Cause:
App not responding on expected port or crashing

### Fix:

**Step 1: Check logs**
```bash
# In Render Dashboard:
# 1. Go to your service
# 2. Click "Logs" tab
# 3. Look for startup errors
```

**Step 2: Verify health endpoint**
```bash
# Make sure /health endpoint exists
# Test locally first:
curl http://localhost:8000/health
```

**Step 3: Check startup**
```bash
# Ensure app starts without errors
# Check for import errors
# Verify all dependencies installed
```

---

## 🚨 Error: "Out of memory"

### Symptoms:
```
Killed
Process exited with code 137
```

### Cause:
Using more than 512MB RAM (free tier limit)

### Fix:

**Option 1: Optimize memory usage**
```python
# Use lazy imports
def heavy_function():
    import heavy_library  # Import only when needed
    return heavy_library.do_something()

# Don't load everything at startup
```

**Option 2: Upgrade to paid tier**
- Starter plan: $7/mo with 512MB RAM
- Standard plan: $25/mo with 2GB RAM

---

## 🚨 Error: "Environment variable not set"

### Symptoms:
```
KeyError: 'STRIPE_SECRET_KEY'
ValueError: DATABASE_URL is required
```

### Cause:
Required environment variable missing

### Fix:

```bash
# In Render Dashboard:
# 1. Go to your service
# 2. Click "Environment" tab
# 3. Add missing variables:

DATABASE_URL=<from database service>
REDIS_URL=<from redis service>
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret
OPENAI_API_KEY=sk-your_key
JWT_SECRET_KEY=<generate random string>
```

---

## 🚨 Error: "Import error"

### Symptoms:
```
ImportError: cannot import name 'SessionMemory'
ModuleNotFoundError: No module named 'autoos.memory'
```

### Cause:
Python path not set correctly

### Fix:

**Option 1: Set PYTHONPATH**
```yaml
# In render.yaml:
envVars:
  - key: PYTHONPATH
    value: /opt/render/project/src
```

**Option 2: Use absolute imports**
```python
# Instead of:
from autoos.memory.session_memory import SessionMemory

# Use:
from src.autoos.memory.session_memory import SessionMemory
```

**Option 3: Add __init__.py files**
```bash
# Make sure these exist:
src/__init__.py
src/autoos/__init__.py
src/autoos/memory/__init__.py
```

---

## 🚨 Error: "Stripe error"

### Symptoms:
```
stripe.error.AuthenticationError: Invalid API Key
```

### Cause:
Stripe API key not set or invalid

### Fix:

```bash
# 1. Get your Stripe test key
# Go to: https://dashboard.stripe.com/test/apikeys

# 2. Copy the SECRET key (starts with sk_test_)

# 3. Add to Render environment:
STRIPE_SECRET_KEY=sk_test_your_actual_key_here

# 4. Restart service
```

---

## ✅ Quick Fix Checklist

Before asking for help, check:

- [ ] All environment variables set in Render
- [ ] Database status is "Available"
- [ ] Redis status is "Available" (if using)
- [ ] Build completed successfully
- [ ] Logs show no import errors
- [ ] Health endpoint returns 200
- [ ] Using $PORT variable (not hardcoded)
- [ ] PYTHONPATH set correctly
- [ ] All dependencies in requirements.txt

---

## 🆘 Emergency Fix: Minimal Working Version

If nothing works, use this minimal version:

### 1. Create `minimal_api.py`:

```python
from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(title="AUTOOS Omega API")

@app.get("/")
def root():
    return {"status": "running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "port": os.getenv("PORT", "8000"),
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 2. Update `render.yaml`:

```yaml
startCommand: uvicorn minimal_api:app --host 0.0.0.0 --port $PORT
```

### 3. Deploy

This minimal version will work 100% and you can add features gradually.

---

## 📞 Still Having Issues?

### Check These:

1. **Render Status Page**
   - https://status.render.com
   - Check for ongoing incidents

2. **Render Logs**
   - Enable "Live tail" in dashboard
   - Look for the FIRST error (not subsequent ones)

3. **Test Locally First**
   ```bash
   # Make sure it works locally:
   pip install -r requirements.txt
   export PORT=8000
   uvicorn src.autoos.intent.api:app --reload
   
   # Test:
   curl http://localhost:8000/health
   ```

4. **Render Community**
   - https://community.render.com
   - Very helpful community

---

## 🎯 Most Common Fix

**90% of deployment errors are fixed by:**

1. Setting environment variables correctly
2. Using $PORT variable
3. Waiting for database to be ready
4. Setting PYTHONPATH

**Try these first!**

---

**Good luck! Your app will be running soon! 🚀**
