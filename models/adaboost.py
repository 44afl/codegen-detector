# models/adaboost.py
import joblib
import json
import logging
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from sklearn.ensemble import AdaBoostClassifier
from .service import ModelService


@dataclass
class AdaBoostConfig:
    n_estimators: int = 50
    learning_rate: float = 1.0
    random_state: Optional[int] = 42
    algorithm: str = "SAMME"


class AdaBoostStrategy(ModelService):
    def __init__(self, config: AdaBoostConfig = None, logger: logging.Logger = None):
        self.config = config or AdaBoostConfig()
        self.logger = logger or logging.getLogger(__name__)
        self.model = AdaBoostClassifier(
            n_estimators=self.config.n_estimators,
            learning_rate=self.config.learning_rate,
            random_state=self.config.random_state,
            algorithm=self.config.algorithm
        )
        self._is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray) -> 'AdaBoostStrategy':
        self._validate_training_data(X, y)
        self.logger.info(f"Training AdaBoost with {len(X)} samples...")
        
        try:
            self.model.fit(X, y)
            self._is_trained = True
            self.logger.info("Training completed successfully")
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            raise
        
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self._is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        if X is None or len(X) == 0:
            raise ValueError("Input X cannot be empty")
        
        proba = self.model.predict_proba(X)[:, 1]
        return proba

    def save(self, path: str) -> str:
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, path_obj)
        
        metadata = {
            "model_type": "AdaBoost",
            "trained": self._is_trained,
            "saved_at": datetime.now().isoformat(),
            "config": self.config.__dict__
        }
        
        with open(path_obj.with_suffix('.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Model saved to {path_obj}")
        return str(path_obj)

    def load(self, path: str) -> 'AdaBoostStrategy':
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        self.model = joblib.load(path_obj)
        self._is_trained = True
        
        self.logger.info(f"Model loaded from {path_obj}")
        return self
    
    def _validate_training_data(self, X: np.ndarray, y: np.ndarray) -> None:
        if X is None or len(X) == 0:
            raise ValueError("Training data X cannot be empty")
        if y is None or len(y) == 0:
            raise ValueError("Training labels y cannot be empty")
        if len(X) != len(y):
            raise ValueError(f"X and y length mismatch: {len(X)} != {len(y)}")
    
    def is_trained(self) -> bool:
        return self._is_trained