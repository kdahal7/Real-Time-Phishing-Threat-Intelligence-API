# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Docker (Easiest)

```bash
# 1. Navigate to project directory
cd "Real-Time Phishing Threat Intelligence API"

# 2. Build and start all services
docker-compose up --build

# 3. Wait for services to start (about 1-2 minutes)
# You'll see: "Phishing Threat Intelligence API Gateway - ONLINE"

# 4. Test the API
curl "http://localhost:8080/api/v1/scan-url?url=http://paypal-secure-login.tk"
```

**That's it!** All three services (Redis, ML Service, Spring Gateway) are running.

---

### Option 2: Manual Setup (For Development)

#### Step 1: Setup ML Service

```bash
# Navigate to ml-service
cd ml-service

# Install Python dependencies
pip install -r requirements.txt

# Generate training dataset
python scripts/generate_dataset.py

# Train the model (takes 2-3 minutes)
python scripts/train_model.py

# Start ML service
uvicorn app.main:app --reload --port 8000
```

Leave this terminal running and open a new one.

#### Step 2: Start Redis

```bash
# Install Redis or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

#### Step 3: Start Spring Boot Gateway

```bash
# Navigate to spring-gateway
cd spring-gateway

# Build and run
mvn spring-boot:run
```

---

## ✅ Verify Everything Works

### 1. Check Services are Running

```bash
# ML Service health
curl http://localhost:8000/health

# Spring Gateway health
curl http://localhost:8080/api/v1/health

# Redis
redis-cli ping  # Should return "PONG"
```

### 2. Test Phishing Detection

```bash
# Test a suspicious URL
curl "http://localhost:8080/api/v1/scan-url?url=http://secure-paypal-verify.tk"

# Expected: prediction: "Phishing", high riskScore

# Test a legitimate URL
curl "http://localhost:8080/api/v1/scan-url?url=https://github.com"

# Expected: prediction: "Benign", low riskScore
```

### 3. Test Caching

```bash
# First request (cache miss - slower)
curl "http://localhost:8080/api/v1/scan-url?url=http://test-phishing-site.tk"
# Note the responseTimeMs (should be ~80-120ms)

# Second request (cache hit - much faster)
curl "http://localhost:8080/api/v1/scan-url?url=http://test-phishing-site.tk"
# Note the responseTimeMs (should be <10ms) and fromCache: true
```

---

## 🎯 What to Do Next

### 1. Explore the APIs

**ML Service (Python):**
- Interactive docs: http://localhost:8000/docs
- Try different URLs in the Swagger UI

**Spring Gateway (Java):**
- Health: http://localhost:8080/actuator/health
- Stats: http://localhost:8080/api/v1/stats

### 2. Examine the Code

Start with these key files:
1. [ml-service/app/feature_extractor.py](ml-service/app/feature_extractor.py) - See how features are extracted
2. [spring-gateway/src/main/java/.../service/UrlScanService.java](spring-gateway/src/main/java/com/cisco/security/phishing/service/UrlScanService.java) - See caching logic

### 3. Customize

- Adjust cache TTL: Edit `application.properties`
- Add more features: Modify `feature_extractor.py`
- Retrain model: Run `python scripts/train_model.py` with your data

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8080
netstat -ano | findstr :8080  # Windows
lsof -i :8080  # Mac/Linux

# Kill the process or change port in application.properties
```

### ML Model Not Found

```bash
# Make sure you trained the model
cd ml-service
python scripts/train_model.py

# Check if model exists
ls models/phishing_model.pkl  # Should exist
```

### Redis Connection Failed

```bash
# Make sure Redis is running
redis-cli ping

# If not running, start Redis
redis-server
# Or with Docker:
docker run -d -p 6379:6379 redis:7-alpine
```

### Maven Build Errors

```bash
# Make sure Java 17+ is installed
java -version

# Clean and rebuild
cd spring-gateway
mvn clean install
```

---

## 📊 Sample Test URLs

**Phishing (should return high risk):**
- `http://paypal-secure-login.tk`
- `http://secure-account-verify.xyz`
- `http://192.168.1.100/login`
- `http://www.paypa1.com/signin`
- `http://google.com@evil-site.tk`

**Legitimate (should return low risk):**
- `https://github.com`
- `https://google.com`
- `https://microsoft.com`
- `https://stackoverflow.com`

---

## 🎓 Learn More

- Read the [full README](README.md) for architecture details
- Check [ml-service/README.md](ml-service/README.md) for ML specifics
- Check [spring-gateway/README.md](spring-gateway/README.md) for Java details

---

## 💡 Pro Tips

1. **View Logs**: Watch the console output to see caching in action
2. **Use Postman**: Import the API and save test cases
3. **Monitor Redis**: Use `redis-cli monitor` to see cache operations
4. **Metrics**: Check Spring Actuator at `/actuator/metrics`

---

**Now you're ready to use your Real-Time Phishing Detection API! 🎉**

---

## 🌐 Want to Deploy Online?

**Quick Deploy**: See [DEPLOY_QUICK.md](DEPLOY_QUICK.md) (15-minute guide)
**Full Options**: See [DEPLOYMENT.md](DEPLOYMENT.md) (all platforms)

**Easiest**: Push to GitHub → Deploy on [Render.com](https://render.com) (Free tier available!)

Your API will be live at: `https://your-api.onrender.com/api/v1/scan-url`
