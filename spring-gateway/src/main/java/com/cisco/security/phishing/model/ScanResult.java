package com.cisco.security.phishing.model;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * Response model for URL scan results
 * 
 * Contains the prediction result, confidence score, and metadata
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ScanResult implements Serializable {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * The URL that was scanned
     */
    private String url;
    
    /**
     * Prediction result: "Benign" or "Phishing"
     */
    private String prediction;
    
    /**
     * Confidence score (0.0 to 1.0)
     */
    private Double confidence;
    
    /**
     * Risk score (0 to 100)
     */
    private Double riskScore;
    
    /**
     * Human-readable message
     */
    private String message;
    
    /**
     * Response time in milliseconds
     */
    private Long responseTimeMs;
    
    /**
     * Whether the result was served from cache
     */
    private Boolean fromCache;
    
    /**
     * Timestamp of the scan
     */
    private LocalDateTime timestamp;
    
    /**
     * Request ID for tracing
     */
    private String requestId;
}
