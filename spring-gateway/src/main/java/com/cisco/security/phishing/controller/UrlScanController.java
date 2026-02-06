package com.cisco.security.phishing.controller;

import com.cisco.security.phishing.model.ScanRequest;
import com.cisco.security.phishing.model.ScanResult;
import com.cisco.security.phishing.service.UrlScanService;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * REST Controller for URL scanning endpoints
 * 
 * Main API Gateway for the Phishing Threat Intelligence System
 */
@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "*")
@Slf4j
public class UrlScanController {

    private final UrlScanService urlScanService;

    public UrlScanController(UrlScanService urlScanService) {
        this.urlScanService = urlScanService;
    }

    /**
     * Scan a URL for phishing threats
     * 
     * GET /api/v1/scan-url?url=https://example.com
     */
    @GetMapping("/scan-url")
    public ResponseEntity<ScanResult> scanUrlGet(@RequestParam String url) {
        log.info("GET request - Scanning URL: {}", url);
        
        try {
            ScanResult result = urlScanService.scanUrl(url);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("Error scanning URL: {}", e.getMessage());
            return ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ScanResult.builder()
                            .url(url)
                            .message("Error: " + e.getMessage())
                            .build());
        }
    }

    /**
     * Scan a URL for phishing threats (POST version)
     * 
     * POST /api/v1/scan-url
     * Body: { "url": "https://example.com" }
     */
    @PostMapping("/scan-url")
    public ResponseEntity<ScanResult> scanUrlPost(@Valid @RequestBody ScanRequest request) {
        log.info("POST request - Scanning URL: {}", request.getUrl());
        
        try {
            ScanResult result = urlScanService.scanUrl(request.getUrl());
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("Error scanning URL: {}", e.getMessage());
            return ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ScanResult.builder()
                            .url(request.getUrl())
                            .message("Error: " + e.getMessage())
                            .build());
        }
    }

    /**
     * Clear cache for a specific URL
     * 
     * DELETE /api/v1/cache?url=https://example.com
     */
    @DeleteMapping("/cache")
    public ResponseEntity<Map<String, String>> clearCache(@RequestParam String url) {
        log.info("Clearing cache for URL: {}", url);
        
        try {
            urlScanService.clearCache(url);
            Map<String, String> response = new HashMap<>();
            response.put("message", "Cache cleared successfully");
            response.put("url", url);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Error clearing cache: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Get cache statistics
     * 
     * GET /api/v1/stats
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        log.info("Fetching cache statistics");
        
        try {
            Map<String, Object> stats = urlScanService.getCacheStats();
            stats.put("status", "operational");
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            log.error("Error fetching stats: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Health check endpoint
     * 
     * GET /api/v1/health
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "UP");
        response.put("service", "Phishing API Gateway");
        response.put("version", "1.0.0");
        return ResponseEntity.ok(response);
    }
}
