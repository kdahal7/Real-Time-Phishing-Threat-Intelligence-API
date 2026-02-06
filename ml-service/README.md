# ML Service Quick Start

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Generate training dataset
python scripts/generate_dataset.py

# Train the model
python scripts/train_model.py
```

## Run Service

```bash
# Development mode
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Test Endpoint

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypal-secure-login.tk"}'
```

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.
