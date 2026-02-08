#!/bin/bash

# AUTOOS Deployment Script
# Deploys backend to Railway and frontend to Vercel

set -e  # Exit on error

echo "=========================================="
echo "🚀 AUTOOS Deployment Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found${NC}"
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI not found${NC}"
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

echo -e "${GREEN}✅ CLI tools ready${NC}"
echo ""

# ==========================================
# PART 1: Deploy Backend to Railway
# ==========================================

echo "=========================================="
echo "📦 PART 1: Deploy Backend to Railway"
echo "=========================================="
echo ""

# Login to Railway
echo -e "${BLUE}Logging in to Railway...${NC}"
railway login

# Initialize Railway project
echo -e "${BLUE}Initializing Railway project...${NC}"
railway init

# Add PostgreSQL
echo -e "${BLUE}Adding PostgreSQL database...${NC}"
railway add postgresql

# Add Redis
echo -e "${BLUE}Adding Redis cache...${NC}"
railway add redis

# Set environment variables
echo ""
echo -e "${YELLOW}⚙️  Setting environment variables...${NC}"
echo ""

# Prompt for API keys
read -p "Enter your OpenAI API key: " OPENAI_KEY
read -p "Enter your Anthropic API key: " ANTHROPIC_KEY

# Set variables
railway variables set OPENAI_API_KEY="$OPENAI_KEY"
railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_KEY"
railway variables set UPI_ID="vasu7993457842@axl"
railway variables set UPI_MERCHANT_NAME="AUTOOS"
railway variables set JWT_SECRET=$(openssl rand -base64 32)
railway variables set ENVIRONMENT="production"
railway variables set LOG_LEVEL="INFO"

echo -e "${GREEN}✅ Environment variables set${NC}"
echo ""

# Deploy to Railway
echo -e "${BLUE}Deploying backend to Railway...${NC}"
railway up

echo ""
echo -e "${GREEN}✅ Backend deployed to Railway!${NC}"
echo ""

# Get Railway URL
RAILWAY_URL=$(railway status --json | grep -o '"url":"[^"]*' | cut -d'"' -f4)
echo -e "${GREEN}Backend URL: ${RAILWAY_URL}${NC}"
echo ""

# ==========================================
# PART 2: Deploy Frontend to Vercel
# ==========================================

echo "=========================================="
echo "🎨 PART 2: Deploy Frontend to Vercel"
echo "=========================================="
echo ""

# Go to frontend directory
cd frontend/web

# Login to Vercel
echo -e "${BLUE}Logging in to Vercel...${NC}"
vercel login

# Set environment variable for API URL
echo -e "${BLUE}Setting API URL...${NC}"
echo "NEXT_PUBLIC_API_URL=${RAILWAY_URL}" > .env.production

# Deploy to Vercel
echo -e "${BLUE}Deploying frontend to Vercel...${NC}"
vercel --prod

echo ""
echo -e "${GREEN}✅ Frontend deployed to Vercel!${NC}"
echo ""

# Get Vercel URL
VERCEL_URL=$(vercel inspect --json | grep -o '"url":"[^"]*' | cut -d'"' -f4)
echo -e "${GREEN}Frontend URL: ${VERCEL_URL}${NC}"
echo ""

# Go back to root
cd ../..

# ==========================================
# PART 3: Verify Deployment
# ==========================================

echo "=========================================="
echo "✅ PART 3: Verify Deployment"
echo "=========================================="
echo ""

echo -e "${BLUE}Testing backend health...${NC}"
curl -s "${RAILWAY_URL}/health" && echo -e "${GREEN}✅ Backend is healthy${NC}" || echo -e "${RED}❌ Backend health check failed${NC}"
echo ""

echo -e "${BLUE}Testing frontend...${NC}"
curl -s -o /dev/null -w "%{http_code}" "${VERCEL_URL}" | grep -q "200" && echo -e "${GREEN}✅ Frontend is accessible${NC}" || echo -e "${RED}❌ Frontend not accessible${NC}"
echo ""

# ==========================================
# PART 4: Summary
# ==========================================

echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}Your AUTOOS system is now live!${NC}"
echo ""
echo "📍 URLs:"
echo "  Backend:  ${RAILWAY_URL}"
echo "  Frontend: ${VERCEL_URL}"
echo "  API Docs: ${RAILWAY_URL}/docs"
echo ""
echo "💳 Payment Details:"
echo "  UPI ID: vasu7993457842@axl"
echo "  Merchant: AUTOOS"
echo ""
echo "📧 Next Steps:"
echo "  1. Test the system: ${VERCEL_URL}"
echo "  2. Configure Stripe (optional)"
echo "  3. Set up email service"
echo "  4. Complete Phase 9 implementation"
echo "  5. Launch on Product Hunt!"
echo ""
echo "📚 Documentation:"
echo "  - QUICK_DEPLOY.md"
echo "  - ACCESS_CODE_SYSTEM.md"
echo "  - PAYMENT_SETUP.md"
echo "  - FINAL_IMPLEMENTATION_SUMMARY.md"
echo ""
echo -e "${GREEN}Happy launching! 🚀${NC}"
echo ""
