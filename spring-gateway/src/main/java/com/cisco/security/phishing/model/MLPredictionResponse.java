package com.cisco.security.phishing.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Response model from ML inference service
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MLPredictionResponse {
    
    private String url;
    private String prediction;
    private Double confidence;
    private Double riskScore;
    private String message;
}
