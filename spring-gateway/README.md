# Spring Boot Gateway Quick Start

## Prerequisites

- Java 17+
- Maven 3.9+
- Redis running on localhost:6379

## Build

```bash
mvn clean package
```

## Run

```bash
# Make sure Redis is running first
# Then start the Spring Boot application
mvn spring-boot:run
```

Or run the JAR directly:

```bash
java -jar target/phishing-api-gateway-1.0.0.jar
```

## Test the API

```bash
# Scan a URL (GET method)
curl "http://localhost:8080/api/v1/scan-url?url=http://paypal-secure-login.tk"

# Scan a URL (POST method)
curl -X POST "http://localhost:8080/api/v1/scan-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://secure-paypal-verify.tk"}'

# Health check
curl http://localhost:8080/api/v1/health

# Cache stats
curl http://localhost:8080/api/v1/stats
```

## Configuration

Edit `src/main/resources/application.properties`:

- `ml.service.url`: URL of the Python ML service (default: http://localhost:8000)
- `cache.ttl.seconds`: Cache TTL in seconds (default: 3600 = 1 hour)
- `spring.data.redis.host`: Redis host (default: localhost)
- `spring.data.redis.port`: Redis port (default: 6379)
