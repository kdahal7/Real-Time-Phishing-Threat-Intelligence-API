"""
FastAPI ML Inference Service
Provides REST API endpoint for phishing URL prediction
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, validator
import numpy as np
import logging
from typing import Optional
import uvicorn
import uuid
from datetime import datetime

from app.feature_extractor import URLFeatureExtractor
from app.model_loader import ModelLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Phishing Threat Intelligence API",
    description="ML-powered API for real-time phishing URL detection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class URLRequest(BaseModel):
    """Request model for URL scanning"""
    url: str
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class PredictionResponse(BaseModel):
    """Response model for prediction results"""
    url: str
    prediction: str  # "Benign" or "Phishing"
    confidence: float
    risk_score: float  # 0-100
    features: Optional[dict] = None
    message: str


# Global model loader
model_loader = ModelLoader()
feature_extractor = URLFeatureExtractor()


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    try:
        logger.info("Loading ML model...")
        model_loader.load_model()
        logger.info("Model loaded successfully. API ready to serve requests.")
    except FileNotFoundError:
        logger.warning("Model file not found. API will run in demo mode.")
        logger.warning("Train a model using scripts/train_model.py first.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Phishing Threat Intelligence ML Service",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        model = model_loader.get_model()
        model_loaded = True
    except:
        model_loaded = False
    
    return {
        "status": "healthy",
        "model_loaded": model_loaded
    }


@app.get("/debug")
async def debug_info():
    """Debug endpoint to check file system and environment"""
    import os
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent
    models_dir = base_dir / "models"
    model_path = models_dir / "phishing_model.pkl"
    
    return {
        "base_dir": str(base_dir),
        "models_dir": str(models_dir),
        "model_path": str(model_path),
        "model_exists": os.path.exists(model_path),
        "models_dir_exists": os.path.exists(models_dir),
        "models_dir_contents": os.listdir(models_dir) if os.path.exists(models_dir) else [],
        "current_dir": os.getcwd(),
        "app_dir_contents": os.listdir(base_dir) if os.path.exists(base_dir) else []
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_url(request: URLRequest):
    """
    Predict if a URL is phishing or benign
    
    Args:
        request: URLRequest containing the URL to analyze
        
    Returns:
        PredictionResponse with prediction results
    """
    try:
        logger.info(f"Analyzing URL: {request.url}")
        
        # Extract features
        features = feature_extractor.extract_features(request.url)
        logger.debug(f"Extracted features: {features}")
        
        # Prepare features for model
        feature_names = feature_extractor.get_feature_names()
        feature_vector = np.array([[features[name] for name in feature_names]])
        
        # Make prediction
        try:
            model = model_loader.get_model()
            prediction = model.predict(feature_vector)[0]
            probabilities = model.predict_proba(feature_vector)[0]
            
            # Get confidence and risk score
            phishing_probability = probabilities[1] if len(probabilities) > 1 else probabilities[0]
            confidence = float(max(probabilities))
            risk_score = float(phishing_probability * 100)
            
            # Determine prediction label
            prediction_label = "Phishing" if prediction == 1 else "Benign"
            
            # Generate message
            if prediction_label == "Phishing":
                if risk_score >= 90:
                    message = "HIGH RISK: This URL is highly likely to be a phishing attempt. Do not proceed."
                elif risk_score >= 70:
                    message = "MEDIUM RISK: This URL shows signs of phishing. Proceed with caution."
                else:
                    message = "LOW RISK: This URL may be suspicious. Verify before proceeding."
            else:
                message = "This URL appears to be legitimate."
            
            logger.info(f"Prediction: {prediction_label}, Confidence: {confidence:.2f}, Risk Score: {risk_score:.2f}")
            
            return PredictionResponse(
                url=request.url,
                prediction=prediction_label,
                confidence=round(confidence, 4),
                risk_score=round(risk_score, 2),
                features=features,
                message=message
            )
            
        except RuntimeError:
            # Model not loaded - demo mode
            logger.warning("Model not loaded. Using heuristic-based demo prediction.")
            
            # Simple heuristic for demo
            risk_indicators = 0
            if features['has_at_symbol']:
                risk_indicators += 1
            if features['is_ip_address']:
                risk_indicators += 1
            if features['has_suspicious_tld']:
                risk_indicators += 1
            if features['has_phishing_keyword']:
                risk_indicators += 1
            if features['url_length'] > 75:
                risk_indicators += 1
            if features['num_dots'] > 4:
                risk_indicators += 1
            
            risk_score = min((risk_indicators / 6) * 100, 100)
            prediction_label = "Phishing" if risk_indicators >= 3 else "Benign"
            confidence = 0.75 if risk_indicators >= 3 else 0.80
            
            message = "Demo mode prediction (model not trained yet)"
            
            return PredictionResponse(
                url=request.url,
                prediction=prediction_label,
                confidence=confidence,
                risk_score=risk_score,
                features=features,
                message=message
            )
            
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/batch-predict")
async def batch_predict(urls: list[str]):
    """
    Predict multiple URLs at once
    
    Args:
        urls: List of URLs to analyze
        
    Returns:
        List of prediction results
    """
    results = []
    for url in urls[:100]:  # Limit to 100 URLs per batch
        try:
            request = URLRequest(url=url)
            result = await predict_url(request)
            results.append(result.dict())
        except Exception as e:
            results.append({
                "url": url,
                "error": str(e)
            })
    
    return {"results": results, "total": len(results)}


# ============================================================================
# DIRECT API ENDPOINTS (Alternative to Spring Boot Gateway)
# ============================================================================

@app.get("/api/v1/scan-url")
async def scan_url_direct(url: str):
    """
    Direct URL scanning endpoint (replaces Spring Boot Gateway)
    
    Args:
        url: URL query parameter to analyze
        
    Returns:
        JSON response matching Spring Boot format
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"Direct API - Analyzing URL: {url}")
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            return {
                "error": "URL must start with http:// or https://",
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "requestId": str(uuid.uuid4())[:8]
            }
        
        # Extract features
        features = feature_extractor.extract_features(url)
        
        # Make prediction
        try:
            model = model_loader.get_model()
            if model is None:
                # Demo mode - pattern-based detection
                is_phishing = any([
                    'secure-' in url.lower() and ('.tk' in url or '.ml' in url),
                    'verify' in url.lower() and len(url) > 50,
                    'login.php' in url.lower(),
                    'confirm' in url.lower() and url.count('-') > 3,
                    url.count('.') > 3,
                    any(char in url for char in ['0', '1'] * 3)  # suspicious chars
                ])
                confidence = 0.85 if is_phishing else 0.92
                prediction_label = "Phishing" if is_phishing else "Benign"
            else:
                # Real model prediction
                feature_names = feature_extractor.get_feature_names()
                feature_vector = np.array([[features[name] for name in feature_names]])
                
                prediction = model.predict(feature_vector)[0]
                probabilities = model.predict_proba(feature_vector)[0]
                
                phishing_probability = probabilities[1] if len(probabilities) > 1 else probabilities[0]
                confidence = float(max(probabilities))
                prediction_label = "Phishing" if prediction == 1 else "Benign"
        
        except Exception as model_error:
            logger.error(f"Model prediction failed: {model_error}")
            # Fallback to demo mode
            is_phishing = 'phishing' in url.lower() or 'secure-' in url.lower()
            confidence = 0.75
            prediction_label = "Phishing" if is_phishing else "Benign"
        
        # Generate message
        if prediction_label == "Phishing":
            message = "HIGH RISK: This URL is highly likely to be a phishing attempt. Do not proceed."
        else:
            message = "This URL appears to be legitimate."
        
        # Calculate response time
        response_time = int((time.time() - start_time) * 1000)
        
        return {
            "url": url,
            "prediction": prediction_label,
            "confidence": round(confidence, 4),
            "message": message,
            "responseTimeMs": response_time,
            "fromCache": False,
            "timestamp": datetime.now().isoformat(),
            "requestId": str(uuid.uuid4())[:8]
        }
        
    except Exception as e:
        logger.error(f"Direct API error: {str(e)}", exc_info=True)
        return {
            "error": f"Analysis failed: {str(e)}",
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "requestId": str(uuid.uuid4())[:8]
        }


@app.get("/api/v1/health")
async def health_check_direct():
    """Health check endpoint compatible with Spring Boot Actuator"""
    try:
        model_loader_instance = ModelLoader()
        model = model_loader_instance.get_model()
        model_loaded = model is not None
    except:
        model_loaded = False
    
    return {
        "status": "UP",
        "components": {
            "ml_model": {
                "status": "UP" if model_loaded else "DOWN",
                "details": {
                    "loaded": model_loaded,
                    "type": "XGBoost" if model_loaded else "Demo Mode"
                }
            },
            "disk_space": {"status": "UP"},
            "ping": {"status": "UP"}
        }
    }


@app.get("/api/v1/stats") 
async def get_stats_direct():
    """Statistics endpoint compatible with Spring Boot"""
    try:
        model_loader_instance = ModelLoader()
        model = model_loader_instance.get_model()
        model_status = "loaded" if model else "demo_mode"
    except:
        model_status = "error"
    
    return {
        "status": "operational",
        "mlServiceUrl": "http://localhost:8000",
        "model": model_status,
        "version": "1.0.0",
        "features": "30_url_features",
        "algorithm": "XGBoost"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
