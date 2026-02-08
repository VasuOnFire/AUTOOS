#!/usr/bin/env bash
# Startup script for AUTOOS Omega on Render

set -e  # Exit on error

echo "🚀 Starting AUTOOS Omega..."

# Check if we're on Render
if [ "$RENDER" = "true" ]; then
    echo "📍 Running on Render"
    echo "🔧 Environment: Production"
else
    echo "📍 Running locally"
    echo "🔧 Environment: Development"
fi

# Check required environment variables
echo "🔍 Checking environment variables..."

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  WARNING: DATABASE_URL not set"
else
    echo "✅ DATABASE_URL configured"
fi

if [ -z "$REDIS_URL" ]; then
    echo "⚠️  WARNING: REDIS_URL not set"
else
    echo "✅ REDIS_URL configured"
fi

if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo "⚠️  WARNING: STRIPE_SECRET_KEY not set"
else
    echo "✅ STRIPE_SECRET_KEY configured"
fi

# Get port from environment or default to 8000
PORT=${PORT:-8000}
echo "🌐 Starting server on port $PORT..."

# Start the server
echo "🎯 Launching FastAPI application..."
exec uvicorn src.autoos.intent.api:app \
    --host 0.0.0.0 \
    --port $PORT \
    --log-level info \
    --no-access-log
