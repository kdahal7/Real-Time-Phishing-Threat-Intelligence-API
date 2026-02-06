# 🚀 Quick Deployment Guide

## TL;DR - Get Online in 15 Minutes

### Recommended Path: Render.com (Free + Easy)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/phishing-api.git
   git push -u origin main
   ```

2. **Create Redis on Render**
   - Go to [render.com](https://render.com)
   - New + → Redis (Free plan)
   - Copy the internal URL

3. **Deploy ML Service**
   - New + → Web Service
   - Connect GitHub repo
   - Root directory: `ml-service`
   - Environment: Docker
   - Deploy (Free plan)
   - Copy the URL (e.g., `https://xxx.onrender.com`)

4. **Deploy Spring Gateway**
   - New + → Web Service
   - Root directory: `spring-gateway`
   - Environment: Docker
   - Add env vars:
     - `SPRING_DATA_REDIS_HOST`: (Redis hostname)
     - `ML_SERVICE_URL`: (ML service URL from step 3)
   - Deploy (Starter $7/month - Java needs RAM)

5. **Test It!**
   ```bash
   curl "https://your-gateway.onrender.com/api/v1/scan-url?url=http://paypal-secure.tk"
   ```

**Done! Your API is live!** 🎉

---

## Platform Comparison (1-Minute Decision)

| Need | Platform | Cost | Time |
|------|----------|------|------|
| **Free demo** | Render.com | $0-7/mo | 15 min |
| **Always-on, simple** | Railway.app | ~$20/mo | 10 min |
| **Production-ready** | DigitalOcean | ~$27/mo | 20 min |
| **Enterprise** | AWS ECS | ~$60/mo | 60 min |
| **Serverless** | Cloud Run | ~$15/mo | 30 min |

---

## What You Get

✅ **Live API URL**: `https://your-api.onrender.com/api/v1/scan-url`
✅ **Automatic HTTPS**: All platforms provide SSL
✅ **Health endpoints**: `/health`, `/actuator/health`
✅ **API docs**: ML service at `/docs` (Swagger UI)
✅ **Auto-restart**: If service crashes
✅ **Logs**: View in platform dashboard

---

## Before You Deploy

### Must Do (5 minutes)

```bash
# 1. Train the model locally first
cd ml-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_dataset.py
python scripts/train_model.py
# This creates ml-service/models/phishing_model.pkl

# 2. Make sure model is committed
git add ml-service/models/phishing_model.pkl -f
git commit -m "Add trained model"
```

**Important**: The model file (~50MB) needs to be in the Docker image!

---

## After Deployment

### Test Your Live API

```bash
# Set your API URL
$API_URL = "https://your-gateway.onrender.com"

# Test phishing detection
curl "$API_URL/api/v1/scan-url?url=http://secure-paypal-verify.tk"

# Should return:
# {
#   "prediction": "Phishing",
#   "confidence": 0.95+,
#   "riskScore": 90+,
#   "fromCache": false,
#   "responseTimeMs": 80-120
# }

# Test cache (run same URL twice)
curl "$API_URL/api/v1/scan-url?url=http://test-cache.tk"
curl "$API_URL/api/v1/scan-url?url=http://test-cache.tk"
# Second request: fromCache=true, responseTimeMs < 10

# Health checks
curl "$API_URL/api/v1/health"
curl "$API_URL/actuator/health"
```

### Share Your API

Add to your resume/portfolio:
```
Live Demo: https://your-gateway.onrender.com/api/v1/scan-url?url=http://example-phishing.tk
```

---

## Common Issues & Fixes

### ❌ "Service Unavailable" on first request
**Fix**: Render free tier sleeps after 15 min. Wait 30-60 seconds for wake-up.

### ❌ "Connection refused" to Redis
**Fix**: Check Redis hostname in env vars (remove `redis://` prefix and `:6379` suffix)

### ❌ "Model file not found"
**Fix**: Make sure you committed the trained model:
```bash
git add ml-service/models/phishing_model.pkl -f
git push
```

### ❌ Spring Gateway out of memory
**Fix**: Use at least Starter plan ($7/mo) - free tier not enough for Java

### ❌ ML service slow/timeout
**Fix**: First prediction loads model (slow). Subsequent requests are fast. Consider switching to paid plan.

---

## Cost Breakdown

### Free Option (with limitations)
- Redis: Free (Render)
- ML Service: Free (sleeps after 15 min)
- Gateway: Free (NOT recommended - Java needs RAM)
- **Total**: Free, but sleeps

### Recommended Setup
- Redis: Free (Render)
- ML Service: Free (Render)
- Gateway: $7/mo (Render Starter)
- **Total**: $7/month

### Always-On Production
- Redis: $7/mo (Render Starter)
- ML Service: $7/mo (Render Starter)
- Gateway: $7/mo (Render Starter)
- **Total**: $21/month

---

## Make It Better (After Deployment)

1. **Custom Domain**
   - Buy domain on Namecheap/Google Domains
   - Add CNAME record to Render
   - Enable in Render settings
   - Result: `api.yourdomain.com`

2. **Monitoring**
   - Add UptimeRobot (free)
   - Monitor: `https://your-api/actuator/health`
   - Get alerts if down

3. **CI/CD**
   - Render auto-deploys on git push
   - Or use GitHub Actions (template in `.github/workflows/`)

4. **Analytics**
   - Log all requests
   - Track most common phishing patterns
   - Monitor cache hit rate

5. **Improve Model**
   - Collect real phishing URLs (PhishTank API)
   - Retrain weekly
   - Deploy new model version

---

## For Your Resume

Once deployed, add this:

```
Real-Time Phishing Threat Intelligence API
Live Demo: https://your-api.onrender.com
GitHub: https://github.com/YOUR_USERNAME/phishing-api

• Deployed microservices architecture to cloud (Render/AWS/Azure)
• Implemented CI/CD pipeline for automated deployments
• Scaled to handle 2000+ requests/second with Redis caching
• Monitored with health checks and application logging
```

---

## Need More Details?

📖 **Full deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
🏗️ **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
🎤 **Interview prep**: [INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md)
⚡ **Quick start**: [QUICKSTART.md](QUICKSTART.md)

---

**Ready? Start with Render.com - you'll be live in 15 minutes! 🚀**
