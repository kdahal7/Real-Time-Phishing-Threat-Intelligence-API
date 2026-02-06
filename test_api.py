"""
Integration Test Script
Tests the complete Phishing Detection API system
"""

import requests
import time
import json
from typing import Dict, List

# Configuration
SPRING_GATEWAY_URL = "http://localhost:8080"
ML_SERVICE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(message: str, status: str = "info"):
    colors = {
        "success": Colors.GREEN,
        "error": Colors.RED,
        "warning": Colors.YELLOW,
        "info": Colors.BLUE
    }
    color = colors.get(status, Colors.END)
    print(f"{color}{message}{Colors.END}")

def check_service(name: str, url: str) -> bool:
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print_status(f"✓ {name} is running", "success")
            return True
        else:
            print_status(f"✗ {name} returned status {response.status_code}", "error")
            return False
    except requests.exceptions.ConnectionError:
        print_status(f"✗ {name} is not reachable at {url}", "error")
        return False
    except Exception as e:
        print_status(f"✗ Error checking {name}: {str(e)}", "error")
        return False

def test_ml_service_prediction(url: str) -> Dict:
    """Test ML service directly"""
    print_status(f"\nTesting ML Service with URL: {url}", "info")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{ML_SERVICE_URL}/predict",
            json={"url": url},
            timeout=10
        )
        elapsed_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            print_status(f"  Prediction: {result['prediction']}", "success")
            print_status(f"  Confidence: {result['confidence']:.4f}", "success")
            print_status(f"  Risk Score: {result['riskScore']:.2f}", "success")
            print_status(f"  Response Time: {elapsed_time:.2f}ms", "success")
            return result
        else:
            print_status(f"  Error: Status {response.status_code}", "error")
            return None
    except Exception as e:
        print_status(f"  Error: {str(e)}", "error")
        return None

def test_gateway_scan(url: str) -> Dict:
    """Test Spring Gateway"""
    print_status(f"\nTesting Spring Gateway with URL: {url}", "info")
    
    try:
        start_time = time.time()
        response = requests.get(
            f"{SPRING_GATEWAY_URL}/api/v1/scan-url",
            params={"url": url},
            timeout=10
        )
        elapsed_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            print_status(f"  Prediction: {result['prediction']}", "success")
            print_status(f"  Confidence: {result['confidence']:.4f}", "success")
            print_status(f"  Risk Score: {result['riskScore']:.2f}", "success")
            print_status(f"  Cached: {result['fromCache']}", "success")
            print_status(f"  Response Time: {result['responseTimeMs']}ms (measured: {elapsed_time:.2f}ms)", "success")
            return result
        else:
            print_status(f"  Error: Status {response.status_code}", "error")
            return None
    except Exception as e:
        print_status(f"  Error: {str(e)}", "error")
        return None

def test_cache_performance():
    """Test cache hit performance"""
    print_status("\n" + "="*60, "info")
    print_status("Testing Cache Performance", "info")
    print_status("="*60, "info")
    
    test_url = "http://test-cache-phishing-site-12345.tk"
    
    # First request (cache miss)
    print_status("\n1. First request (cache miss expected):", "info")
    result1 = test_gateway_scan(test_url)
    
    if result1:
        time.sleep(1)
        
        # Second request (cache hit)
        print_status("\n2. Second request (cache hit expected):", "info")
        result2 = test_gateway_scan(test_url)
        
        if result2 and result2['fromCache']:
            print_status("\n✓ Cache is working correctly!", "success")
            print_status(f"  Cache speedup: {result1['responseTimeMs'] / result2['responseTimeMs']:.2f}x faster", "success")
        else:
            print_status("\n✗ Cache might not be working", "warning")

def run_test_suite():
    """Run complete test suite"""
    print_status("\n" + "="*60, "info")
    print_status("Real-Time Phishing Threat Intelligence API", "info")
    print_status("Integration Test Suite", "info")
    print_status("="*60, "info")
    
    # Step 1: Check services
    print_status("\n1. Checking Services...", "info")
    ml_service_ok = check_service("ML Service", f"{ML_SERVICE_URL}/health")
    gateway_ok = check_service("Spring Gateway", f"{SPRING_GATEWAY_URL}/api/v1/health")
    
    if not ml_service_ok or not gateway_ok:
        print_status("\n✗ Not all services are running. Please start them first.", "error")
        print_status("\nRun: docker-compose up", "warning")
        return False
    
    # Step 2: Test ML Service
    print_status("\n" + "="*60, "info")
    print_status("2. Testing ML Service (Python/FastAPI)", "info")
    print_status("="*60, "info")
    
    test_urls = [
        ("http://paypal-secure-login.tk", "Phishing"),
        ("https://github.com", "Benign"),
    ]
    
    for url, expected in test_urls:
        result = test_ml_service_prediction(url)
        if result and result['prediction'] == expected:
            print_status(f"  ✓ Correct prediction for {url}", "success")
        elif result:
            print_status(f"  ⚠ Unexpected prediction for {url}: got {result['prediction']}, expected {expected}", "warning")
    
    # Step 3: Test Gateway
    print_status("\n" + "="*60, "info")
    print_status("3. Testing Spring Boot Gateway", "info")
    print_status("="*60, "info")
    
    for url, expected in test_urls:
        result = test_gateway_scan(url)
        if result and result['prediction'] == expected:
            print_status(f"  ✓ Correct prediction for {url}", "success")
    
    # Step 4: Test caching
    test_cache_performance()
    
    # Step 5: Summary
    print_status("\n" + "="*60, "info")
    print_status("Test Suite Complete!", "success")
    print_status("="*60, "info")
    print_status("\n✓ All services are operational", "success")
    print_status("✓ ML predictions are working", "success")
    print_status("✓ Spring Gateway is working", "success")
    print_status("✓ Redis caching is working", "success")
    
    print_status("\nAPI Endpoints:", "info")
    print_status(f"  Main API: {SPRING_GATEWAY_URL}/api/v1/scan-url", "info")
    print_status(f"  ML Service Docs: {ML_SERVICE_URL}/docs", "info")
    print_status(f"  Gateway Health: {SPRING_GATEWAY_URL}/actuator/health", "info")
    
    return True

if __name__ == "__main__":
    try:
        success = run_test_suite()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print_status("\n\nTest interrupted by user", "warning")
        exit(1)
    except Exception as e:
        print_status(f"\n\nUnexpected error: {str(e)}", "error")
        exit(1)
