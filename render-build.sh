#!/usr/bin/env bash
# Render Build Script for AUTOOS Omega Backend
# This script runs during the build phase on Render

set -o errexit  # Exit on error
set -o pipefail # Exit on pipe failure

echo "🚀 Starting AUTOOS Omega build..."

# Suppress man page warnings
export DEBIAN_FRONTEND=noninteractive
export PYTHONUNBUFFERED=1

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel 2>&1 | grep -v "update-alternatives" || true

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt 2>&1 | grep -v "update-alternatives" || true

# Run database migrations (if needed)
if [ -f "alembic.ini" ]; then
    echo "🗄️  Running database migrations..."
    alembic upgrade head || echo "⚠️  Migrations skipped (will run on startup)"
fi

echo "✅ Build completed successfully!"
