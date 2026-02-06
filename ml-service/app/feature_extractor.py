"""
Feature Extractor for URL Analysis
Extracts key features from URLs to detect phishing attempts
"""

import re
from urllib.parse import urlparse
import tldextract


class URLFeatureExtractor:
    """Extract features from URLs for phishing detection"""
    
    @staticmethod
    def extract_features(url: str) -> dict:
        """
        Extract comprehensive features from a URL
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dictionary containing extracted features
        """
        features = {}
        
        # Basic URL properties
        features['url_length'] = len(url)
        features['domain_length'] = len(urlparse(url).netloc)
        
        # Protocol analysis
        features['has_https'] = 1 if url.startswith('https://') else 0
        features['has_http'] = 1 if url.startswith('http://') else 0
        
        # Character analysis
        features['num_dots'] = url.count('.')
        features['num_hyphens'] = url.count('-')
        features['num_underscores'] = url.count('_')
        features['num_slashes'] = url.count('/')
        features['num_question_marks'] = url.count('?')
        features['num_equal_signs'] = url.count('=')
        features['num_at_symbols'] = url.count('@')
        features['num_ampersands'] = url.count('&')
        features['num_percent_signs'] = url.count('%')
        
        # Suspicious character presence
        features['has_at_symbol'] = 1 if '@' in url else 0
        features['has_double_slash_redirect'] = 1 if url.count('//') > 1 else 0
        
        # Digit analysis
        features['num_digits'] = sum(c.isdigit() for c in url)
        features['digit_ratio'] = features['num_digits'] / len(url) if len(url) > 0 else 0
        
        # Parse domain information
        try:
            parsed = urlparse(url)
            extracted = tldextract.extract(url)
            
            # Domain analysis
            features['subdomain_length'] = len(extracted.subdomain)
            features['has_subdomain'] = 1 if extracted.subdomain else 0
            features['num_subdomains'] = len(extracted.subdomain.split('.')) if extracted.subdomain else 0
            
            # Path analysis
            path = parsed.path
            features['path_length'] = len(path)
            features['num_path_tokens'] = len(path.split('/'))
            
            # Query parameters
            query = parsed.query
            features['has_query_params'] = 1 if query else 0
            features['num_query_params'] = len(query.split('&')) if query else 0
            
            # Check for IP address as domain
            ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            features['is_ip_address'] = 1 if re.match(ip_pattern, parsed.netloc.split(':')[0]) else 0
            
            # Port analysis
            features['has_port'] = 1 if ':' in parsed.netloc and not features['is_ip_address'] else 0
            
            # TLD analysis
            features['tld_length'] = len(extracted.suffix)
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top']
            features['has_suspicious_tld'] = 1 if any(url.endswith(tld) for tld in suspicious_tlds) else 0
            
        except Exception as e:
            # If parsing fails, set default values
            features['subdomain_length'] = 0
            features['has_subdomain'] = 0
            features['num_subdomains'] = 0
            features['path_length'] = 0
            features['num_path_tokens'] = 0
            features['has_query_params'] = 0
            features['num_query_params'] = 0
            features['is_ip_address'] = 0
            features['has_port'] = 0
            features['tld_length'] = 0
            features['has_suspicious_tld'] = 0
        
        # Suspicious keywords in URL
        phishing_keywords = [
            'login', 'signin', 'account', 'update', 'confirm', 'verify',
            'secure', 'ebay', 'paypal', 'amazon', 'bank', 'apple'
        ]
        features['has_phishing_keyword'] = 1 if any(keyword in url.lower() for keyword in phishing_keywords) else 0
        
        # Entropy calculation (complexity measure)
        features['url_entropy'] = URLFeatureExtractor.calculate_entropy(url)
        
        return features
    
    @staticmethod
    def calculate_entropy(string: str) -> float:
        """Calculate Shannon entropy of a string"""
        from collections import Counter
        import math
        
        if not string:
            return 0.0
        
        # Calculate frequency of each character
        freq = Counter(string)
        length = len(string)
        
        # Calculate entropy
        entropy = 0.0
        for count in freq.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    @staticmethod
    def get_feature_names() -> list:
        """Return list of all feature names in order"""
        return [
            'url_length', 'domain_length', 'has_https', 'has_http',
            'num_dots', 'num_hyphens', 'num_underscores', 'num_slashes',
            'num_question_marks', 'num_equal_signs', 'num_at_symbols',
            'num_ampersands', 'num_percent_signs', 'has_at_symbol',
            'has_double_slash_redirect', 'num_digits', 'digit_ratio',
            'subdomain_length', 'has_subdomain', 'num_subdomains',
            'path_length', 'num_path_tokens', 'has_query_params',
            'num_query_params', 'is_ip_address', 'has_port',
            'tld_length', 'has_suspicious_tld', 'has_phishing_keyword',
            'url_entropy'
        ]
