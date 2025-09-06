#!/bin/bash

echo "🚀 Health Symptom Checker Deployment Script"
echo "=========================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - Health Symptom Checker"
    echo "✅ Git repository initialized"
    echo ""
    echo "⚠️  IMPORTANT: Please create a GitHub repository and run:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/health-symptom-checker.git"
    echo "   git push -u origin main"
    echo ""
else
    echo "📤 Pushing changes to GitHub..."
    git add .
    git commit -m "Update for deployment"
    git push
    echo "✅ Changes pushed to GitHub"
fi

echo ""
echo "🌐 Next Steps:"
echo "1. Go to https://railway.app and deploy your backend"
echo "2. Go to https://vercel.com and deploy your frontend"
echo "3. Follow the instructions in DEPLOYMENT.md"
echo ""
echo "📋 Don't forget to:"
echo "- Set your OpenAI API key in Railway environment variables"
echo "- Set REACT_APP_API_URL in Vercel environment variables"
echo "- Update CORS settings after getting your URLs"
