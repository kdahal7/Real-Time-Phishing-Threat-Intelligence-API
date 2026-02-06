# Quick deployment helper for Render.com (PowerShell)

Write-Host "🚀 Render.com Deployment Helper" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Prerequisites:" -ForegroundColor Yellow
Write-Host "1. Create account at render.com"
Write-Host "2. Create Redis instance and copy internal URL"
Write-Host "3. Have GitHub repo ready"
Write-Host ""

$continue = Read-Host "Have you completed the prerequisites? (y/n)"
if ($continue -ne 'y') {
    Write-Host "Please complete prerequisites first!" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Step 1: Push to GitHub (if not done)" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
$githubUser = Read-Host "Enter your GitHub username"
$repoName = Read-Host "Enter repository name (e.g., phishing-api)"

git init
git add .
git commit -m "Deploy to Render"
git branch -M main

$remoteExists = git remote | Select-String -Pattern "origin"
if (-not $remoteExists) {
    git remote add origin "https://github.com/$githubUser/$repoName.git"
    Write-Host "✓ Remote added" -ForegroundColor Green
} else {
    Write-Host "Remote 'origin' already exists" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Now run: git push -u origin main" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Manual Steps on Render.com" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. ML Service:" -ForegroundColor Yellow
Write-Host "   - New Web Service → Connect GitHub repo"
Write-Host "   - Root Directory: ml-service"
Write-Host "   - Environment: Docker"
Write-Host "   - After deploy, copy the URL"
Write-Host ""
Write-Host "2. Redis:" -ForegroundColor Yellow
Write-Host "   - New Redis → Free or Starter plan"
Write-Host "   - Copy the Internal Redis URL"
Write-Host ""
Write-Host "3. Spring Gateway:" -ForegroundColor Yellow
Write-Host "   - New Web Service → Connect GitHub repo"
Write-Host "   - Root Directory: spring-gateway"
Write-Host "   - Environment: Docker"
Write-Host "   - Add environment variables:"
Write-Host "     SPRING_DATA_REDIS_HOST=<redis-hostname>" -ForegroundColor White
Write-Host "     SPRING_DATA_REDIS_PORT=6379" -ForegroundColor White
Write-Host "     ML_SERVICE_URL=<ml-service-url>" -ForegroundColor White
Write-Host ""
Write-Host "✅ Done! Your API will be live in ~10 minutes" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Full guide: See DEPLOYMENT.md" -ForegroundColor Cyan
