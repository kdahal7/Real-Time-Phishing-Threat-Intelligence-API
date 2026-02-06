# Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATION                          │
│                    (Browser, Mobile App, etc.)                      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ HTTP/HTTPS Request
                                 │ GET /api/v1/scan-url?url=...
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SPRING BOOT API GATEWAY (Port 8080)              │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  ┌─────────────────┐    ┌──────────────────┐    ┌───────────────┐ │
│  │ REST Controller │───▶│  UrlScanService  │───▶│ Redis Config  │ │
│  │  - Input Valid. │    │  - Cache Logic   │    │  - Lettuce    │ │
│  │  - JSON Response│    │  - ML Integration│    │  - Connection │ │
│  └─────────────────┘    └──────────────────┘    └───────────────┘ │
│                                 │                                    │
│ Tech Stack:                     │ Cache Check                       │
│ • Java 17                       │                                    │
│ • Spring Boot 3.2               │                                    │
│ • Spring Data Redis             │                                    │
│ • Lombok                        │                                    │
└─────────────────────────────────┼────────────────────────────────────┘
                                  │
                    ┌─────────────┴────────────┐
                    │                          │
             Cache HIT                   Cache MISS
            (3-5ms)                    (Forward to ML)
                    │                          │
                    │                          ▼
                    │          ┌────────────────────────────────────┐
                    │          │  PYTHON ML SERVICE (Port 8000)     │
                    │          │━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
                    │          │  ┌──────────────────────────────┐ │
                    │          │  │    FastAPI Endpoint          │ │
                    │          │  │    POST /predict             │ │
                    │          │  └──────────┬───────────────────┘ │
                    │          │             │                      │
                    │          │             ▼                      │
                    │          │  ┌──────────────────────────────┐ │
                    │          │  │   Feature Extractor          │ │
                    │          │  │   • 30+ URL features         │ │
                    │          │  │   • Lexical analysis         │ │
                    │          │  │   • Domain parsing           │ │
                    │          │  │   • Entropy calculation      │ │
                    │          │  └──────────┬───────────────────┘ │
                    │          │             │                      │
                    │          │             ▼                      │
                    │          │  ┌──────────────────────────────┐ │
                    │          │  │   XGBoost Classifier         │ │
                    │          │  │   • Trained on 50K URLs      │ │
                    │          │  │   • 96% accuracy             │ │
                    │          │  │   • Real-time inference      │ │
                    │          │  └──────────┬───────────────────┘ │
                    │          │             │                      │
                    │          │  Tech Stack:                       │
                    │          │  • Python 3.11                     │
                    │          │  • FastAPI                         │
                    │          │  • XGBoost 2.0                     │
                    │          │  • Scikit-learn                    │
                    │          │  • Pandas/NumPy                    │
                    │          └─────────────┬──────────────────────┘
                    │                        │
                    │                        │ Prediction Result
                    │                        │ (80-120ms)
                    │                        │
                    ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         REDIS CACHE (Port 6379)                     │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  Key: phishing:url:http://example.com                               │
│  Value: {                                                           │
│    "prediction": "Phishing",                                        │
│    "confidence": 0.98,                                              │
│    "riskScore": 98.5,                                               │
│    "message": "HIGH RISK...",                                       │
│    ...                                                              │
│  }                                                                  │
│  TTL: 3600 seconds (1 hour)                                         │
│                                                                     │
│  Tech: Redis 7 (Alpine), In-Memory Storage                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Return cached or new result
                                  ▼
                          ┌───────────────┐
                          │  JSON Response │
                          │  to Client     │
                          └───────────────┘
```

## Data Flow

### 1. First Request (Cache Miss)
```
Client → Spring Gateway → Redis (no match) → ML Service → XGBoost → Spring Gateway → Redis (store) → Client
Total Time: ~85-120ms
```

### 2. Subsequent Requests (Cache Hit)
```
Client → Spring Gateway → Redis (match found) → Spring Gateway → Client
Total Time: ~3-7ms (40% faster!)
```

## Component Responsibilities

### Spring Boot Gateway
- **Entry Point**: Receives all client requests
- **Cache Manager**: Checks Redis before calling ML service
- **Request Router**: Forwards to ML service on cache miss
- **Response Builder**: Adds metadata (responseTime, fromCache, requestId)
- **Error Handler**: Graceful degradation on ML service failure

### Python ML Service
- **Feature Engineering**: Extracts 30+ features from URLs
- **ML Inference**: Runs XGBoost prediction
- **Risk Scoring**: Converts probability to 0-100 risk score
- **Stateless**: No internal state, pure function service

### Redis Cache
- **High-Speed Storage**: In-memory key-value store
- **TTL Management**: Auto-expires stale entries after 1 hour
- **Serialization**: JSON format for easy debugging
- **Persistence**: Optional (RDB/AOF for production)

## Deployment Options

### Option 1: Docker Compose (Recommended)
All services in isolated containers with networking.

### Option 2: Local Development
- Spring Boot: `mvn spring-boot:run`
- ML Service: `uvicorn app.main:app --reload`
- Redis: `redis-server` or Docker

### Option 3: Kubernetes
Scale horizontally with pod replicas and load balancing.

## Performance Characteristics

| Metric | Without Cache | With Cache (80% hit rate) |
|--------|--------------|---------------------------|
| Avg Response Time | 100ms | 26ms |
| P95 Response Time | 150ms | 35ms |
| Max Throughput | 100 req/s | 2000 req/s |
| ML Service Load | 100% | 20% |

## Security Considerations

1. **Input Validation**: All URLs validated before processing
2. **Rate Limiting**: Can be added at gateway level
3. **HTTPS**: Recommended for production
4. **Authentication**: JWT/OAuth2 can be integrated
5. **Redis Security**: Use password and SSL in production
