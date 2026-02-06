# 🚀 Deployment Guide - Going Live Online

## Overview

This guide covers multiple ways to deploy your Real-Time Phishing Threat Intelligence API to the cloud. Choose based on your needs:

- **Easiest**: Render.com (Free tier available)
- **Production-Ready**: AWS with ECS or DigitalOcean
- **Enterprise**: Kubernetes on AWS/Azure/GCP
- **Budget**: Railway, Fly.io, or Heroku alternatives

---

## 🎯 Option 1: Render.com (Recommended for Quick Deployment)

**Pros**: Free tier, easy setup, automatic HTTPS, supports Docker
**Time**: ~15 minutes

### Step 1: Prepare Your Code

1. Create a GitHub repository:
```bash
cd "Real-Time Phishing Threat Intelligence API"
git init
git add .
git commit -m "Initial commit - Phishing API"
git remote add origin https://github.com/kdahal7/Real-Time-Phishing-Threat-Intelligence-API.git
git push -u origin main
```

### Step 2: Deploy Redis

1. Go to [Render.com](https://render.com) and sign up
2. Click "New +" → "Redis"
3. Name: `phishing-redis`
4. Plan: Free (25MB) or Starter ($7/month for 256MB)
5. Click "Create Redis Instance"
6. **Copy the Internal Redis URL** (looks like: `redis://red-xxxxx:6379`)

### Step 3: Deploy ML Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `phishing-ml-service`
   - **Root Directory**: `ml-service`
   - **Environment**: Docker
   - **Dockerfile Path**: `ml-service/Dockerfile`
   - **Plan**: Free (512MB RAM) or Starter ($7/month for 512MB)
4. **Before deploying**, add environment variables:
   - (None required for ML service)
5. Click "Create Web Service"
6. **Copy the service URL** (e.g., `https://phishing-ml-service.onrender.com`)

### Step 4: Deploy Spring Boot Gateway

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `phishing-api-gateway`
   - **Root Directory**: `spring-gateway`
   - **Environment**: Docker
   - **Dockerfile Path**: `spring-gateway/Dockerfile`
   - **Plan**: Starter ($7/month for 512MB) - Java needs more RAM
4. **Add Environment Variables**:
   - `SPRING_DATA_REDIS_HOST`: (paste Redis URL hostname from Step 2, remove `redis://` and `:6379`)
   - `SPRING_DATA_REDIS_PORT`: `6379`
   - `ML_SERVICE_URL`: (paste ML service URL from Step 3)
   - `CACHE_TTL_SECONDS`: `3600`
5. Click "Create Web Service"

### Step 5: Test Your Deployment

```bash
# Replace with your actual gateway URL
curl "https://phishing-api-gateway.onrender.com/api/v1/scan-url?url=http://paypal-secure-login.tk"
```

**Note**: Free tier services sleep after 15 minutes of inactivity. First request may take 30-60 seconds to wake up.

**Total Cost**: Free (with sleep) or $14/month (always-on)

---

## 🐳 Option 2: DigitalOcean App Platform

**Pros**: Simple, affordable ($12/month), good performance
**Time**: ~20 minutes

### Prerequisites
- DigitalOcean account
- Credit card (required even for free credits)

### Step 1: Create App

1. Go to [DigitalOcean](https://www.digitalocean.com)
2. Click "Create" → "Apps"
3. Connect your GitHub repository
4. Select your repository and branch

### Step 2: Configure Services

DigitalOcean will auto-detect your docker-compose.yml. Configure each:

#### Redis
- **Type**: Database
- **Engine**: Redis
- **Plan**: $15/month (or use managed Redis for $10/month)

#### ML Service
- **Type**: Web Service
- **Root Directory**: `ml-service`
- **Dockerfile**: `ml-service/Dockerfile`
- **HTTP Port**: 8000
- **Plan**: Basic ($5/month for 512MB)

#### Spring Gateway
- **Type**: Web Service
- **Root Directory**: `spring-gateway`
- **Dockerfile**: `spring-gateway/Dockerfile`
- **HTTP Port**: 8080
- **Plan**: Professional ($12/month for 1GB) - Java needs more RAM
- **Environment Variables**:
  - `SPRING_DATA_REDIS_HOST`: `${redis.HOSTNAME}`
  - `SPRING_DATA_REDIS_PORT`: `${redis.PORT}`
  - `ML_SERVICE_URL`: `http://${ml-service.PRIVATE_URL}:8000`

### Step 3: Deploy

- Click "Create Resources"
- Wait 5-10 minutes for build and deployment
- Your API will be at: `https://phishing-api-gateway-xxxxx.ondigitalocean.app`

**Total Cost**: ~$27/month

---

## ☁️ Option 3: AWS (Production-Ready)

**Pros**: Enterprise-grade, scalable, full control
**Time**: ~1 hour

### Architecture on AWS

```
Internet → ALB → ECS Fargate (Spring Gateway)
                      ↓
              ECS Fargate (ML Service)
                      ↓
              ElastiCache Redis
```

### Step 1: Prerequisites

```bash
# Install AWS CLI
# Windows (PowerShell as Admin):
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Configure AWS credentials
aws configure
# Enter: Access Key, Secret Key, Region (e.g., us-east-1), format (json)
```

### Step 2: Create ECR Repositories

```bash
# Create repositories for Docker images
aws ecr create-repository --repository-name phishing-ml-service
aws ecr create-repository --repository-name phishing-gateway

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

### Step 3: Build and Push Images

```bash
cd "Real-Time Phishing Threat Intelligence API"

# Build ML Service
cd ml-service
# First, train the model locally
python scripts/generate_dataset.py
python scripts/train_model.py
# Build and push
docker build -t phishing-ml-service .
docker tag phishing-ml-service:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/phishing-ml-service:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/phishing-ml-service:latest

# Build Spring Gateway
cd ../spring-gateway
docker build -t phishing-gateway .
docker tag phishing-gateway:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/phishing-gateway:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/phishing-gateway:latest
```

### Step 4: Create Infrastructure

#### 4.1 Create VPC and Subnets (using AWS Console or CLI)

```bash
# Use default VPC or create new one
aws ec2 describe-vpcs
```

#### 4.2 Create ElastiCache Redis

```bash
# Via AWS Console:
# 1. Go to ElastiCache → Redis → Create
# 2. Cluster name: phishing-redis
# 3. Node type: cache.t3.micro ($13/month)
# 4. Number of replicas: 0 (for dev) or 1+ (for prod)
# 5. Subnet group: Create new in your VPC
# 6. Security group: Allow port 6379 from ECS
```

#### 4.3 Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name phishing-api-cluster
```

#### 4.4 Create Task Definitions

Create `ml-service-task.json`:
```json
{
  "family": "phishing-ml-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "ml-service",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/phishing-ml-service:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/phishing-ml-service",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Create `gateway-task.json`:
```json
{
  "family": "phishing-gateway",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "gateway",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/phishing-gateway:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "SPRING_DATA_REDIS_HOST",
          "value": "your-redis-endpoint.cache.amazonaws.com"
        },
        {
          "name": "ML_SERVICE_URL",
          "value": "http://ml-service.local:8000"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/phishing-gateway",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register tasks:
```bash
aws ecs register-task-definition --cli-input-json file://ml-service-task.json
aws ecs register-task-definition --cli-input-json file://gateway-task.json
```

#### 4.5 Create ECS Services with ALB

```bash
# This is complex - easier via AWS Console:
# 1. Go to ECS → Clusters → phishing-api-cluster
# 2. Create Service for ML service (internal)
# 3. Create Service for Gateway (with ALB for public access)
# 4. Configure security groups to allow communication
```

### Step 5: Access Your API

Your API will be available at the ALB DNS name:
```
http://phishing-alb-xxxxx.us-east-1.elb.amazonaws.com/api/v1/scan-url?url=...
```

**AWS Costs Estimate**:
- ECS Fargate: ~$30/month (2 services)
- ElastiCache Redis: ~$13/month
- ALB: ~$16/month
- ECR storage: ~$1/month
- **Total**: ~$60/month

---

## 🚢 Option 4: Railway.app (Easiest Paid Option)

**Pros**: Super simple, $5 credit free, great DX
**Time**: ~10 minutes

### Steps

1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects docker-compose.yml
6. Add environment variables for gateway:
   - `SPRING_DATA_REDIS_HOST`: (Railway provides this automatically)
   - `ML_SERVICE_URL`: (Railway provides this automatically)
7. Click Deploy

Railway automatically:
- Builds Docker images
- Sets up networking between services
- Provides HTTPS URLs
- Handles Redis

**Cost**: ~$20/month after free credits

---

## 🌐 Option 5: Google Cloud Run (Serverless)

**Pros**: Pay per use, auto-scaling, $300 free credits
**Time**: ~30 minutes

### Architecture

```
Cloud Run (Gateway) → Cloud Run (ML) → Memorystore Redis
```

### Steps

```bash
# Install gcloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable redis.googleapis.com

# Build and push ML service
cd ml-service
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/phishing-ml-service

# Deploy ML service
gcloud run deploy phishing-ml-service \
  --image gcr.io/YOUR_PROJECT_ID/phishing-ml-service \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --allow-unauthenticated

# Build and push Gateway
cd ../spring-gateway
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/phishing-gateway

# Create Memorystore Redis
gcloud redis instances create phishing-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0

# Deploy Gateway (with VPC connector to access Redis)
gcloud run deploy phishing-gateway \
  --image gcr.io/YOUR_PROJECT_ID/phishing-gateway \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --allow-unauthenticated \
  --set-env-vars SPRING_DATA_REDIS_HOST=10.x.x.x \
  --set-env-vars ML_SERVICE_URL=https://phishing-ml-service-xxx.run.app
```

**Cost**: ~$15/month (with generous free tier)

---

## 🎯 Option 6: Azure Container Apps (Microsoft)

**Pros**: Great for Spring Boot, $200 free credit
**Time**: ~30 minutes

### Steps

```bash
# Install Azure CLI
# Download from: https://aka.ms/installazurecliwindows

# Login
az login

# Create resource group
az group create --name phishing-api-rg --location eastus

# Create container registry
az acr create --resource-group phishing-api-rg --name phishingacr --sku Basic

# Build and push images
az acr build --registry phishingacr --image phishing-ml-service:latest ./ml-service
az acr build --registry phishingacr --image phishing-gateway:latest ./spring-gateway

# Create Azure Cache for Redis
az redis create --resource-group phishing-api-rg --name phishing-redis --location eastus --sku Basic --vm-size c0

# Create Container Apps environment
az containerapp env create --name phishing-env --resource-group phishing-api-rg --location eastus

# Deploy ML service
az containerapp create \
  --name phishing-ml-service \
  --resource-group phishing-api-rg \
  --environment phishing-env \
  --image phishingacr.azurecr.io/phishing-ml-service:latest \
  --target-port 8000 \
  --ingress external

# Deploy Gateway
az containerapp create \
  --name phishing-gateway \
  --resource-group phishing-api-rg \
  --environment phishing-env \
  --image phishingacr.azurecr.io/phishing-gateway:latest \
  --target-port 8080 \
  --ingress external \
  --env-vars SPRING_DATA_REDIS_HOST=phishing-redis.redis.cache.windows.net ML_SERVICE_URL=https://phishing-ml-service.azurecontainerapps.io
```

**Cost**: ~$25/month

---

## 📊 Cost Comparison

| Platform | Monthly Cost | Free Tier | Ease | Best For |
|----------|--------------|-----------|------|----------|
| **Render** | $0-14 | Yes (with sleep) | ⭐⭐⭐⭐⭐ | Quick demos |
| **Railway** | $20 | $5 credit | ⭐⭐⭐⭐⭐ | Side projects |
| **DigitalOcean** | $27 | $200 credit | ⭐⭐⭐⭐ | Small business |
| **Google Cloud Run** | $15 | $300 credit | ⭐⭐⭐ | Serverless |
| **AWS ECS** | $60 | 12mo free tier | ⭐⭐⭐ | Enterprise |
| **Azure** | $25 | $200 credit | ⭐⭐⭐ | .NET shops |

---

## 🔒 Production Checklist

Before going live, ensure:

### Security
- [ ] Enable HTTPS (most platforms do this automatically)
- [ ] Add Redis password authentication
- [ ] Implement rate limiting (add to Spring Boot)
- [ ] Add API key authentication for production use
- [ ] Set up CORS properly (currently set to `*`)
- [ ] Use environment variables for all secrets
- [ ] Enable firewall rules (only allow necessary ports)

### Performance
- [ ] Train model on real phishing data (not just synthetic)
- [ ] Increase Redis instance size for higher traffic
- [ ] Set up auto-scaling rules
- [ ] Configure CDN for static assets (if any)
- [ ] Enable response compression

### Monitoring
- [ ] Set up application monitoring (New Relic, DataDog, or cloud-native)
- [ ] Configure log aggregation
- [ ] Set up alerts for errors and high latency
- [ ] Monitor Redis memory usage
- [ ] Track API usage and costs

### Reliability
- [ ] Set up health checks
- [ ] Configure auto-restart on failure
- [ ] Use Redis cluster for high availability (production)
- [ ] Set up database backups (if using persistent storage)
- [ ] Create staging environment for testing

---

## 🚀 Quick Decision Tree

**I want it free for demos:**
→ Use **Render.com** (free tier with sleep)

**I want it always-on and simple ($20/mo):**
→ Use **Railway.app**

**I want production-ready and affordable ($25-30/mo):**
→ Use **DigitalOcean App Platform**

**I need enterprise features and scalability:**
→ Use **AWS ECS** or **Google Cloud Run**

**I'm already using Azure:**
→ Use **Azure Container Apps**

---

## 📝 Post-Deployment Testing

Once deployed, test with:

```bash
# Replace with your actual URL
export API_URL="https://your-api.onrender.com"

# Test phishing detection
curl "$API_URL/api/v1/scan-url?url=http://paypal-secure-login.tk"

# Test legitimate URL
curl "$API_URL/api/v1/scan-url?url=https://github.com"

# Test caching (run twice, second should be faster)
curl "$API_URL/api/v1/scan-url?url=http://test-caching.tk"
curl "$API_URL/api/v1/scan-url?url=http://test-caching.tk"

# Check health
curl "$API_URL/api/v1/health"

# Check stats
curl "$API_URL/api/v1/stats"
```

---

## 🆘 Troubleshooting

### Services won't start
- Check logs in platform dashboard
- Verify environment variables are set correctly
- Ensure Redis URL format is correct
- Check if ports are correctly configured

### ML Service out of memory
- Increase memory allocation (1GB minimum recommended)
- Consider using a smaller model or feature set
- Enable memory limits in Docker

### High latency
- Check Redis connection (should be in same region/network)
- Monitor ML service response times
- Consider adding more cache capacity
- Enable connection pooling

### Redis connection errors
- Verify Redis URL includes port (`:6379`)
- Check security groups/firewall rules
- Ensure services are in same VPC/network
- Test Redis connectivity: `redis-cli -h HOST -p 6379 ping`

---

## 🎓 Next Steps After Deployment

1. **Custom Domain**: Add your own domain (most platforms support this)
2. **SSL Certificate**: Platforms usually include free SSL
3. **Monitoring**: Set up Prometheus + Grafana or use platform tools
4. **CI/CD**: Set up GitHub Actions for auto-deploy on push
5. **Load Testing**: Use tools like Apache JMeter or k6
6. **Documentation**: Create API docs with Swagger/OpenAPI

---

**Need help? Check platform-specific documentation or the main README troubleshooting section.**

**Ready to deploy? Start with Render.com for the quickest path to production! 🚀**
