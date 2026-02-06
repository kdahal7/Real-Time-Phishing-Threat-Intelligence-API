#!/bin/bash

# Setup script for Real-Time Phishing Threat Intelligence API
# This script sets up the entire project on Linux/Mac

echo "=========================================="
echo "Phishing API Setup Script"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check Java
if ! command -v java &> /dev/null; then
    echo -e "${RED}Java is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Java found${NC}"

# Check Maven
if ! command -v mvn &> /dev/null; then
    echo -e "${RED}Maven is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Maven found${NC}"

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    echo -e "${RED}Redis is not installed. Installing via Docker...${NC}"
    docker run -d -p 6379:6379 --name phishing-redis redis:7-alpine
fi
echo -e "${GREEN}✓ Redis available${NC}"

echo ""
echo "=========================================="
echo "Setting up ML Service"
echo "=========================================="

cd ml-service

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Generate dataset
echo "Generating training dataset (50,000 URLs)..."
python scripts/generate_dataset.py

# Train model
echo "Training XGBoost model..."
python scripts/train_model.py

echo -e "${GREEN}✓ ML Service setup complete${NC}"
cd ..

echo ""
echo "=========================================="
echo "Building Spring Boot Gateway"
echo "=========================================="

cd spring-gateway

# Build with Maven
echo "Building Spring Boot application..."
mvn clean package -DskipTests

echo -e "${GREEN}✓ Spring Gateway build complete${NC}"
cd ..

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="

echo ""
echo "To start the services:"
echo ""
echo "1. Start ML Service:"
echo "   cd ml-service && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "2. Start Redis (if not running):"
echo "   redis-server"
echo ""
echo "3. Start Spring Gateway:"
echo "   cd spring-gateway && mvn spring-boot:run"
echo ""
echo "Or use Docker:"
echo "   docker-compose up --build"
echo ""
echo "API will be available at: http://localhost:8080"
echo ""
