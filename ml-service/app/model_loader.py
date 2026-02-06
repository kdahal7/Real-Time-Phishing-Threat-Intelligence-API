"""
Model Loader for Phishing Detection
Handles loading and caching of the trained ML model
"""

import pickle
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton class to load and cache the ML model"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def load_model(self, model_path: str = None):
        """
        Load the trained model from disk
        
        Args:
            model_path: Path to the .pkl model file
        """
        if self._model is not None:
            logger.info("Model already loaded, returning cached instance")
            return self._model
        
        if model_path is None:
            # Default path
            base_dir = Path(__file__).parent.parent
            model_path = base_dir / "models" / "phishing_model.pkl"
        
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        try:
            with open(model_path, 'rb') as f:
                self._model = pickle.load(f)
            logger.info(f"Model successfully loaded from {model_path}")
            return self._model
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def get_model(self):
        """Get the loaded model instance"""
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self._model
    
    def predict(self, features):
        """
        Make prediction using the loaded model
        
        Args:
            features: Feature array or dict for prediction
            
        Returns:
            Prediction result
        """
        model = self.get_model()
        return model.predict(features)
    
    def predict_proba(self, features):
        """
        Get prediction probabilities
        
        Args:
            features: Feature array or dict for prediction
            
        Returns:
            Probability array
        """
        model = self.get_model()
        return model.predict_proba(features)
