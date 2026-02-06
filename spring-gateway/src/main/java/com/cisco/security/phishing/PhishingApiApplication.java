package com.cisco.security.phishing;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * Main Application Class for Phishing Threat Intelligence API Gateway
 * 
 * This microservice acts as a high-performance gateway that:
 * 1. Receives URL scan requests from clients
 * 2. Checks Redis cache for recent results (sub-5ms latency)
 * 3. Forwards to ML inference service if cache miss
 * 4. Caches results with TTL for future requests
 * 
 * @author Security Engineering Team
 * @version 1.0.0
 */
@SpringBootApplication
@EnableCaching
@EnableAsync
public class PhishingApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(PhishingApiApplication.class, args);
        System.out.println("""
            
            ================================================================
            🔒 Phishing Threat Intelligence API Gateway - ONLINE
            ================================================================
            📍 API Endpoint: http://localhost:8080/api/v1/scan-url
            📊 Actuator:     http://localhost:8080/actuator/health
            📖 API Docs:     http://localhost:8080/swagger-ui.html
            ================================================================
            
            """);
    }
}
