#!/bin/bash
# Quick deployment script for Render.com
# Make sure you've already created Redis instance and got the URLs

echo "🚀 Render.com Deployment Helper"
echo "================================"
echo ""
echo "Prerequisites:"
echo "1. Create account at render.com"
echo "2. Create Redis instance and copy internal URL"
echo "3. Have GitHub repo ready"
echo ""

read -p "Have you completed the prerequisites? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Please complete prerequisites first!"
    exit 1
fi

echo ""
echo "Step 1: Push to GitHub (if not done)"
echo "===================================="
read -p "Enter your GitHub username: " github_user
read -p "Enter repository name (e.g., phishing-api): " repo_name

git init
git add .
git commit -m "Deploy to Render"
git branch -M main

if git remote | grep -q origin; then
    echo "Remote 'origin' already exists"
else
    git remote add origin "https://github.com/$github_user/$repo_name.git"
fi

echo ""
echo "Push to GitHub with: git push -u origin main"
echo ""

echo "Step 2: Manual Steps on Render.com"
echo "==================================="
echo ""
echo "1. ML Service:"
echo "   - New Web Service → Connect GitHub repo"
echo "   - Root Directory: ml-service"
echo "   - Environment: Docker"
echo "   - After deploy, copy the URL"
echo ""
echo "2. Redis:"
echo "   - New Redis → Free or Starter plan"
echo "   - Copy the Internal Redis URL"
echo ""
echo "3. Spring Gateway:"
echo "   - New Web Service → Connect GitHub repo"
echo "   - Root Directory: spring-gateway"
echo "   - Environment: Docker"
echo "   - Add environment variables:"
echo "     SPRING_DATA_REDIS_HOST=<redis-hostname>"
echo "     SPRING_DATA_REDIS_PORT=6379"
echo "     ML_SERVICE_URL=<ml-service-url>"
echo ""
echo "✅ Done! Your API will be live in ~10 minutes"
