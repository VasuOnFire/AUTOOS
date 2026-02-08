#!/bin/bash

# AUTOOS Omega - Push to GitHub Script
# Run this script to push your code to GitHub

echo "🚀 Pushing AUTOOS Omega to GitHub..."
echo ""

# Step 1: Add GitHub remote
echo "📡 Adding GitHub remote..."
git remote add origin https://github.com/VasuOnFire/autoos-omega.git 2>/dev/null || echo "Remote already exists"

# Step 2: Verify remote
echo "✓ Verifying remote..."
git remote -v

# Step 3: Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
echo "You may be asked for your GitHub credentials:"
echo "  Username: VasuOnFire"
echo "  Password: Use your Personal Access Token (not your GitHub password)"
echo ""

git push -u origin main

# Check if push was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Your code is now on GitHub!"
    echo ""
    echo "🔗 View your repository at:"
    echo "   https://github.com/VasuOnFire/autoos-omega"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Go to https://railway.app/new"
    echo "   2. Click 'Deploy from GitHub repo'"
    echo "   3. Select 'autoos-omega'"
    echo "   4. Add PostgreSQL and Redis databases"
    echo "   5. Configure environment variables"
    echo "   6. Deploy!"
    echo ""
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo ""
    echo "1. Repository doesn't exist on GitHub"
    echo "   → Create it at: https://github.com/new"
    echo "   → Name: autoos-omega"
    echo "   → Don't initialize with README"
    echo ""
    echo "2. Authentication failed"
    echo "   → Use Personal Access Token, not password"
    echo "   → Create token at: https://github.com/settings/tokens"
    echo "   → Select 'repo' scope"
    echo ""
    echo "3. Remote already exists with different URL"
    echo "   → Run: git remote remove origin"
    echo "   → Then run this script again"
    echo ""
fi
