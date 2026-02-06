"""
Train XGBoost Model for Phishing Detection
Trains a high-performance classifier on URL features
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.feature_extractor import URLFeatureExtractor

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score, roc_auc_score
)
import xgboost as xgb
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns


class PhishingModelTrainer:
    """Train and evaluate phishing detection model"""
    
    def __init__(self):
        self.feature_extractor = URLFeatureExtractor()
        self.model = None
        self.feature_names = None
        
    def load_data(self, csv_path: str) -> pd.DataFrame:
        """Load dataset from CSV"""
        print(f"Loading dataset from {csv_path}...")
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} URLs")
        print(f"Class distribution:\n{df['label'].value_counts()}")
        return df
    
    def extract_features_from_dataset(self, df: pd.DataFrame) -> tuple:
        """Extract features from all URLs in dataset"""
        print("\nExtracting features from URLs...")
        
        X_list = []
        y_list = []
        
        for idx, row in df.iterrows():
            if idx % 1000 == 0:
                print(f"Processing {idx}/{len(df)}...")
            
            try:
                features = self.feature_extractor.extract_features(row['url'])
                feature_values = [features[name] for name in self.feature_extractor.get_feature_names()]
                X_list.append(feature_values)
                y_list.append(row['label'])
            except Exception as e:
                print(f"Error processing URL {row['url']}: {str(e)}")
                continue
        
        X = np.array(X_list)
        y = np.array(y_list)
        self.feature_names = self.feature_extractor.get_feature_names()
        
        print(f"\nFeature extraction complete!")
        print(f"Feature matrix shape: {X.shape}")
        print(f"Number of features: {len(self.feature_names)}")
        
        return X, y
    
    def train_model(self, X_train, y_train, use_smote=True):
        """Train XGBoost classifier"""
        print("\n" + "="*60)
        print("Training XGBoost Model")
        print("="*60)
        
        # Handle class imbalance with SMOTE if needed
        if use_smote:
            print("\nApplying SMOTE for class balancing...")
            smote = SMOTE(random_state=42)
            X_train, y_train = smote.fit_resample(X_train, y_train)
            print(f"After SMOTE - Training samples: {len(X_train)}")
        
        # XGBoost parameters optimized for phishing detection
        params = {
            'max_depth': 8,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'objective': 'binary:logistic',
            'booster': 'gbtree',
            'n_jobs': -1,
            'gamma': 0.2,
            'min_child_weight': 1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'reg_alpha': 0.1,
            'reg_lambda': 1,
            'random_state': 42,
            'eval_metric': 'logloss'
        }
        
        print("\nTraining XGBoost classifier...")
        print(f"Parameters: {params}")
        
        self.model = xgb.XGBClassifier(**params)
        self.model.fit(
            X_train, y_train,
            verbose=True
        )
        
        print("\nModel training complete!")
        
        # Cross-validation
        print("\nPerforming 5-fold cross-validation...")
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5, scoring='f1')
        print(f"Cross-validation F1 scores: {cv_scores}")
        print(f"Mean F1 Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        return self.model
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        print("\n" + "="*60)
        print("Model Evaluation")
        print("="*60)
        
        # Predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        print(f"\nAccuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1 Score:  {f1:.4f}")
        print(f"ROC AUC:   {roc_auc:.4f}")
        
        print("\n" + "="*60)
        print("Classification Report")
        print("="*60)
        print(classification_report(y_test, y_pred, target_names=['Benign', 'Phishing']))
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print("\n" + "="*60)
        print("Confusion Matrix")
        print("="*60)
        print(cm)
        print(f"\nTrue Negatives:  {cm[0][0]}")
        print(f"False Positives: {cm[0][1]}")
        print(f"False Negatives: {cm[1][0]}")
        print(f"True Positives:  {cm[1][1]}")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'roc_auc': roc_auc
        }
    
    def analyze_feature_importance(self, top_n=15):
        """Analyze and display feature importance"""
        print("\n" + "="*60)
        print("Feature Importance Analysis")
        print("="*60)
        
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        print(f"\nTop {top_n} Most Important Features:")
        for i in range(min(top_n, len(indices))):
            idx = indices[i]
            print(f"{i+1}. {self.feature_names[idx]}: {importances[idx]:.4f}")
    
    def save_model(self, output_path: str = None):
        """Save trained model to disk"""
        if output_path is None:
            base_dir = Path(__file__).parent.parent
            models_dir = base_dir / "models"
            models_dir.mkdir(exist_ok=True)
            output_path = models_dir / "phishing_model.pkl"
        
        print(f"\nSaving model to {output_path}...")
        with open(output_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"Model saved successfully!")
        return output_path


def main():
    """Main training pipeline"""
    print("="*60)
    print("Phishing Detection Model Training Pipeline")
    print("="*60)
    
    # Initialize trainer
    trainer = PhishingModelTrainer()
    
    # Load data
    base_dir = Path(__file__).parent.parent
    data_path = base_dir / "data" / "phishing_dataset.csv"
    
    if not data_path.exists():
        print(f"\nERROR: Dataset not found at {data_path}")
        print("Please run 'python scripts/generate_dataset.py' first!")
        return
    
    df = trainer.load_data(str(data_path))
    
    # Extract features
    X, y = trainer.extract_features_from_dataset(df)
    
    # Split data
    print("\nSplitting data into train/test sets (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train model
    trainer.train_model(X_train, y_train, use_smote=True)
    
    # Evaluate model
    metrics = trainer.evaluate_model(X_test, y_test)
    
    # Analyze feature importance
    trainer.analyze_feature_importance(top_n=15)
    
    # Save model
    model_path = trainer.save_model()
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"\nModel Performance Summary:")
    print(f"  Accuracy:  {metrics['accuracy']*100:.2f}%")
    print(f"  Precision: {metrics['precision']*100:.2f}%")
    print(f"  Recall:    {metrics['recall']*100:.2f}%")
    print(f"  F1 Score:  {metrics['f1']*100:.2f}%")
    print(f"\nModel saved to: {model_path}")
    print("\nYou can now start the FastAPI service with:")
    print("  cd ml-service")
    print("  uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
