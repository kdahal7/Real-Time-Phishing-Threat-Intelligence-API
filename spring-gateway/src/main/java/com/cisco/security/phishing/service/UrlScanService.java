package com.cisco.security.phishing.service;

import com.cisco.security.phishing.model.MLPredictionResponse;
import com.cisco.security.phishing.model.ScanResult;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * Service layer for URL scanning operations
 * 
 * Implements the core business logic:
 * 1. Check Redis cache for existing results
 * 2. If cache miss, call ML inference service
 * 3. Cache the result with TTL
 * 4. Return result to controller
 */
@Service
@Slf4j
public class UrlScanService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${ml.service.url:http://localhost:8000}")
    private String mlServiceUrl;

    @Value("${cache.ttl.seconds:3600}")
    private long cacheTtlSeconds;

    private static final String CACHE_KEY_PREFIX = "phishing:url:";

    public UrlScanService(
            RedisTemplate<String, Object> redisTemplate,
            RestTemplate restTemplate,
            ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    /**
     * Scan a URL for phishing threats
     * 
     * @param url The URL to scan
     * @return ScanResult containing prediction and metadata
     */
    public ScanResult scanUrl(String url) {
        long startTime = System.currentTimeMillis();
        String requestId = UUID.randomUUID().toString().substring(0, 8);
        
        log.info("[{}] Scanning URL: {}", requestId, url);

        // Step 1: Check Redis cache
        String cacheKey = CACHE_KEY_PREFIX + url;
        ScanResult cachedResult = getCachedResult(cacheKey);

        if (cachedResult != null) {
            long responseTime = System.currentTimeMillis() - startTime;
            cachedResult.setResponseTimeMs(responseTime);
            cachedResult.setFromCache(true);
            cachedResult.setRequestId(requestId);
            
            log.info("[{}] Cache HIT - Response time: {}ms", requestId, responseTime);
            return cachedResult;
        }

        log.info("[{}] Cache MISS - Calling ML service", requestId);

        // Step 2: Call ML inference service
        ScanResult result = callMLService(url, requestId);

        // Step 3: Cache the result
        cacheResult(cacheKey, result);

        // Step 4: Calculate response time
        long responseTime = System.currentTimeMillis() - startTime;
        result.setResponseTimeMs(responseTime);
        result.setFromCache(false);
        result.setRequestId(requestId);
        result.setTimestamp(LocalDateTime.now());

        log.info("[{}] Scan complete - Prediction: {} - Response time: {}ms", 
                requestId, result.getPrediction(), responseTime);

        return result;
    }

    /**
     * Get cached result from Redis
     */
    private ScanResult getCachedResult(String cacheKey) {
        try {
            Object cached = redisTemplate.opsForValue().get(cacheKey);
            if (cached != null) {
                // Deserialize from JSON
                return objectMapper.convertValue(cached, ScanResult.class);
            }
        } catch (Exception e) {
            log.error("Error retrieving from cache: {}", e.getMessage());
        }
        return null;
    }

    /**
     * Cache the scan result in Redis
     */
    private void cacheResult(String cacheKey, ScanResult result) {
        try {
            redisTemplate.opsForValue().set(
                    cacheKey,
                    result,
                    cacheTtlSeconds,
                    TimeUnit.SECONDS
            );
            log.debug("Result cached with key: {} (TTL: {}s)", cacheKey, cacheTtlSeconds);
        } catch (Exception e) {
            log.error("Error caching result: {}", e.getMessage());
        }
    }

    /**
     * Call the ML inference service
     */
    private ScanResult callMLService(String url, String requestId) {
        try {
            String mlEndpoint = mlServiceUrl + "/predict";
            
            // Prepare request
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            Map<String, String> requestBody = new HashMap<>();
            requestBody.put("url", url);
            
            HttpEntity<Map<String, String>> request = new HttpEntity<>(requestBody, headers);
            
            // Call ML service
            log.debug("[{}] Calling ML service: {}", requestId, mlEndpoint);
            ResponseEntity<MLPredictionResponse> response = restTemplate.postForEntity(
                    mlEndpoint,
                    request,
                    MLPredictionResponse.class
            );
            
            MLPredictionResponse mlResponse = response.getBody();
            
            if (mlResponse == null) {
                throw new RuntimeException("ML service returned null response");
            }
            
            // Convert to ScanResult
            return ScanResult.builder()
                    .url(url)
                    .prediction(mlResponse.getPrediction())
                    .confidence(mlResponse.getConfidence())
                    .riskScore(mlResponse.getRiskScore())
                    .message(mlResponse.getMessage())
                    .timestamp(LocalDateTime.now())
                    .build();
            
        } catch (Exception e) {
            log.error("[{}] Error calling ML service: {}", requestId, e.getMessage());
            throw new RuntimeException("Failed to get prediction from ML service: " + e.getMessage());
        }
    }

    /**
     * Clear cache for a specific URL
     */
    public void clearCache(String url) {
        String cacheKey = CACHE_KEY_PREFIX + url;
        redisTemplate.delete(cacheKey);
        log.info("Cache cleared for URL: {}", url);
    }

    /**
     * Get cache statistics
     */
    public Map<String, Object> getCacheStats() {
        Map<String, Object> stats = new HashMap<>();
        // In production, you'd track cache hit/miss ratios
        stats.put("cacheTtlSeconds", cacheTtlSeconds);
        stats.put("mlServiceUrl", mlServiceUrl);
        return stats;
    }
}
