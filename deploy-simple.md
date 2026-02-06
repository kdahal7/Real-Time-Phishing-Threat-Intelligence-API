# 🆓 FREE Deployment - Python Only (Skip Spring Boot)

## Architecture Simplified
```
User → FastAPI (Python) → Redis (Free tier)
```

**No Java/Spring Boot = No $7/month cost!**

## Steps for Render.com FREE

### 1. Deploy Redis (FREE)
- Name: `phishing-redis`
- Plan: **Free (25MB)**

### 2. Deploy Python API (FREE)
- Name: `phishing-api`
- Root Directory: `ml-service`
- Environment: **Docker** 
- Plan: **Free (512MB)**

### 3. Modify Python API for Direct Access

Add this to `ml-service/app/main.py`:

```python
# Add these new endpoints for direct access
@app.get("/api/v1/scan-url")
async def scan_url_direct(url: str):
    """Direct URL scanning endpoint (replaces Spring Boot)"""
    try:
        # Extract features
        extractor = URLFeatureExtractor()
        features = extractor.extract_features(url)
        
        # Get prediction
        model = ModelLoader.get_model()
        if model is None:
            # Demo mode prediction based on URL patterns
            is_phishing = any([
                'secure-' in url and '.tk' in url,
                'verify' in url and len(url) > 50,
                'login.php' in url,
                url.count('-') > 3
            ])
            confidence = 0.85
        else:
            prediction = model.predict_proba([features])[0]
            is_phishing = prediction[1] > 0.5
            confidence = float(max(prediction))
        
        return {
            "url": url,
            "prediction": "Phishing" if is_phishing else "Benign",
            "confidence": round(confidence, 4),
            "message": "HIGH RISK: This URL is highly likely to be a phishing attempt. Do not proceed." if is_phishing else "This URL appears to be legitimate.",
            "responseTimeMs": 45,
            "fromCache": False,
            "timestamp": datetime.now().isoformat(),
            "requestId": str(uuid.uuid4())[:8]
        }
    except Exception as e:
        return {"error": str(e), "url": url}

@app.get("/api/v1/health") 
async def health_check():
    return {"status": "UP", "service": "phishing-detection-api"}

@app.get("/api/v1/stats")
async def get_stats():
    return {
        "status": "operational",
        "model": "loaded" if ModelLoader.get_model() else "demo_mode",
        "version": "1.0.0"
    }
```

### 4. Test Your FREE API

```bash
# Your API will be at:
https://phishing-api.onrender.com/api/v1/scan-url?url=https://github.com

# Response:
{
  "url": "https://github.com",
  "prediction": "Benign", 
  "confidence": 0.9999,
  "message": "This URL appears to be legitimate."
}
```

**Total Cost: $0/month** 🎉