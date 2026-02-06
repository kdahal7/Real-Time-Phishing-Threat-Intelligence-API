# Setup script for Windows (PowerShell)
# Real-Time Phishing Threat Intelligence API

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phishing API Setup Script (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check Python
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python 3 is not installed" -ForegroundColor Red
    Write-Host "Install from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Java
try {
    $javaVersion = java -version 2>&1
    Write-Host "✓ Java found" -ForegroundColor Green
} catch {
    Write-Host "✗ Java is not installed" -ForegroundColor Red
    Write-Host "Install from: https://www.oracle.com/java/technologies/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Maven
try {
    $mavenVersion = mvn -version 2>&1
    Write-Host "✓ Maven found" -ForegroundColor Green
} catch {
    Write-Host "✗ Maven is not installed" -ForegroundColor Red
    Write-Host "Install from: https://maven.apache.org/download.cgi" -ForegroundColor Yellow
    exit 1
}

# Check Redis
Write-Host "`nChecking Redis..." -ForegroundColor Yellow
$redisRunning = Get-Process -Name redis-server -ErrorAction SilentlyContinue
if (-not $redisRunning) {
    Write-Host "Redis is not running. Starting via Docker..." -ForegroundColor Yellow
    docker run -d -p 6379:6379 --name phishing-redis redis:7-alpine
    Start-Sleep -Seconds 3
}
Write-Host "✓ Redis available" -ForegroundColor Green

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Setting up ML Service" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Set-Location ml-service

# Create virtual environment
Write-Host "`nCreating Python virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Generate dataset
Write-Host "`nGenerating training dataset (50,000 URLs)..." -ForegroundColor Yellow
python scripts\generate_dataset.py

# Train model
Write-Host "`nTraining XGBoost model..." -ForegroundColor Yellow
python scripts\train_model.py

Write-Host "✓ ML Service setup complete" -ForegroundColor Green

# Deactivate venv
deactivate

Set-Location ..

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Building Spring Boot Gateway" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Set-Location spring-gateway

# Build with Maven
Write-Host "`nBuilding Spring Boot application..." -ForegroundColor Yellow
mvn clean package -DskipTests

Write-Host "✓ Spring Gateway build complete" -ForegroundColor Green

Set-Location ..

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host "`nTo start the services:" -ForegroundColor Yellow
Write-Host "`n1. Start ML Service:" -ForegroundColor Cyan
Write-Host "   cd ml-service" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor White

Write-Host "`n2. Start Redis (if not running):" -ForegroundColor Cyan
Write-Host "   docker run -d -p 6379:6379 redis:7-alpine" -ForegroundColor White

Write-Host "`n3. Start Spring Gateway:" -ForegroundColor Cyan
Write-Host "   cd spring-gateway" -ForegroundColor White
Write-Host "   mvn spring-boot:run" -ForegroundColor White

Write-Host "`nOr use Docker Compose:" -ForegroundColor Cyan
Write-Host "   docker-compose up --build" -ForegroundColor White

Write-Host "`nAPI will be available at: http://localhost:8080" -ForegroundColor Green
Write-Host ""
