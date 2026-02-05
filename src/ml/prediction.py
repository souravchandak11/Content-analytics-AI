"""
Content Analytics Platform - Viral Content Prediction
=====================================================
ML model for predicting viral content potential.
"""

import os
import pickle
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import joblib
from loguru import logger


class ViralPredictor:
    """
    Predict viral potential of content using ML.
    
    Features used:
    - Title length and word count
    - Description length
    - Number of tags
    - Publishing hour and day
    - Video duration
    - Channel subscriber count
    - Historical channel performance
    """
    
    MODEL_VERSION = '1.0.0'
    
    def __init__(self, model_path: str = None):
        """
        Initialize predictor.
        
        Args:
            model_path: Path to saved model (optional)
        """
        self.model_path = model_path or os.path.join(
            os.getenv('MODEL_PATH', './data/models'),
            'viral_predictor.joblib'
        )
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self._load_model()
    
    def _load_model(self) -> None:
        """Load saved model if exists."""
        if os.path.exists(self.model_path):
            try:
                data = joblib.load(self.model_path)
                self.model = data['model']
                self.scaler = data['scaler']
                self.feature_names = data['features']
                logger.info(f"Loaded viral predictor model v{data.get('version', 'unknown')}")
            except Exception as e:
                logger.warning(f"Could not load model: {e}")
    
    def extract_features(self, video_data: Dict) -> np.ndarray:
        """
        Extract features from video data.
        
        Args:
            video_data: Video metadata dictionary
            
        Returns:
            Feature array
        """
        title = video_data.get('title', '')
        description = video_data.get('description', '')
        tags = video_data.get('tags', [])
        published_at = video_data.get('published_at')
        
        features = {
            'title_length': len(title),
            'title_word_count': len(title.split()),
            'description_length': len(description),
            'description_word_count': len(description.split()),
            'tag_count': len(tags) if isinstance(tags, list) else 0,
            'has_emoji_title': 1 if self._has_emoji(title) else 0,
            'has_question_title': 1 if '?' in title else 0,
            'has_number_title': 1 if any(c.isdigit() for c in title) else 0,
            'duration_seconds': video_data.get('duration_seconds', 0),
            'is_short': 1 if video_data.get('duration_seconds', 0) < 60 else 0,
            'channel_subscribers': video_data.get('channel_subscribers', 0),
            'channel_avg_views': video_data.get('channel_avg_views', 0),
        }
        
        # Time-based features
        if published_at:
            if isinstance(published_at, str):
                published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            features['publish_hour'] = published_at.hour
            features['publish_day'] = published_at.weekday()
            features['is_weekend'] = 1 if published_at.weekday() >= 5 else 0
        else:
            features['publish_hour'] = 12
            features['publish_day'] = 0
            features['is_weekend'] = 0
        
        self.feature_names = list(features.keys())
        return np.array(list(features.values())).reshape(1, -1)
    
    def _has_emoji(self, text: str) -> bool:
        """Check if text contains emoji."""
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "]+", 
            flags=re.UNICODE
        )
        return bool(emoji_pattern.search(text))
    
    def train(
        self,
        videos_data: List[Dict],
        viral_threshold: float = 2.0
    ) -> Dict[str, Any]:
        """
        Train the viral prediction model.
        
        Args:
            videos_data: List of video data with view counts
            viral_threshold: Multiplier of avg views to consider viral
            
        Returns:
            Training metrics
        """
        if len(videos_data) < 50:
            return {'error': 'Need at least 50 videos for training'}
        
        logger.info(f"Training viral predictor with {len(videos_data)} videos")
        
        # Prepare training data
        X = []
        y = []
        
        avg_views = np.mean([v.get('views', 0) for v in videos_data])
        threshold = avg_views * viral_threshold
        
        for video in videos_data:
            features = self.extract_features(video)
            X.append(features.flatten())
            y.append(1 if video.get('views', 0) > threshold else 0)
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        
        metrics = {
            'accuracy': round(accuracy_score(y_test, y_pred), 4),
            'precision': round(precision_score(y_test, y_pred, zero_division=0), 4),
            'recall': round(recall_score(y_test, y_pred, zero_division=0), 4),
            'f1_score': round(f1_score(y_test, y_pred, zero_division=0), 4),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'viral_count': int(sum(y)),
            'threshold_views': int(threshold),
            'version': self.MODEL_VERSION
        }
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            importance = dict(zip(
                self.feature_names,
                [round(float(x), 4) for x in self.model.feature_importances_]
            ))
            metrics['feature_importance'] = dict(sorted(
                importance.items(), key=lambda x: x[1], reverse=True
            )[:10])
        
        # Save model
        self._save_model()
        
        logger.info(f"Model trained: accuracy={metrics['accuracy']}, f1={metrics['f1_score']}")
        return metrics
    
    def predict(self, video_data: Dict) -> Dict[str, Any]:
        """
        Predict viral potential.
        
        Args:
            video_data: Video metadata
            
        Returns:
            Prediction results
        """
        if self.model is None:
            return {'error': 'Model not trained', 'viral_probability': 0.5}
        
        features = self.extract_features(video_data)
        features_scaled = self.scaler.transform(features)
        
        # Get prediction and probability
        prediction = self.model.predict(features_scaled)[0]
        proba = self.model.predict_proba(features_scaled)[0]
        
        viral_prob = float(proba[1]) if len(proba) > 1 else float(prediction)
        
        return {
            'is_viral': bool(prediction),
            'viral_probability': round(viral_prob, 4),
            'viral_score': round(viral_prob * 100, 1),
            'confidence': 'high' if abs(viral_prob - 0.5) > 0.3 else 'medium' if abs(viral_prob - 0.5) > 0.15 else 'low',
            'model_version': self.MODEL_VERSION
        }
    
    def _save_model(self) -> None:
        """Save model to disk."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'features': self.feature_names,
            'version': self.MODEL_VERSION,
            'trained_at': datetime.utcnow().isoformat()
        }, self.model_path)
        
        logger.info(f"Model saved to {self.model_path}")
