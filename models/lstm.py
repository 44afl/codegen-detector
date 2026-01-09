from .service import ModelService
import os
import logging
import numpy as np
import joblib
from sklearn.neural_network import MLPClassifier

logger = logging.getLogger(__name__)

"""
method for refactoring: Extract Method
duplicate code ( _prepare_X ) extracted from train and predict methods

"""
class LSTMModel(ModelService):


    def __init__(
        self,
        hidden_layer_sizes=(32, 16),
        learning_rate_init=1e-3,
        max_iter=200,
        random_state=42,
        **kwargs
    ):
        self.hidden_layer_sizes = hidden_layer_sizes
        self.learning_rate_init = learning_rate_init
        self.max_iter = max_iter
        self.random_state = random_state

        self.model = MLPClassifier(
            hidden_layer_sizes=self.hidden_layer_sizes,
            learning_rate_init=self.learning_rate_init,
            max_iter=self.max_iter,
            random_state=self.random_state,
            **kwargs
        )

    # -------------------------
    # Extract Method (refactoring)
    # -------------------------
    def _prepare_X(self, X, *, context: str) -> np.ndarray:

        if hasattr(X, "toarray"):
            X = X.toarray()

        X = np.asarray(X, dtype="float32")

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if X.ndim != 2:
            raise ValueError(f"[MLP] X should be 2D in {context}, got shape {X.shape}")

        return X

    def train(self, X, y):
        """
        X: (n_samples, n_features) – poate fi și csr_matrix (sparse)
        y: vector etichete (0/1)
        """
        X = self._prepare_X(X, context="train")
        y = np.asarray(y)

        logger.info("[MLP] Starting fit on %s", X.shape)
        self.model.fit(X, y)
        logger.info("[MLP] Finished fit.")
        return self

    def predict(self, X):
        X = self._prepare_X(X, context="predict")
        proba = self.model.predict_proba(X)[:, 1]
        return proba

    def save(self, path: str):
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        joblib.dump(self.model, path)
        return path

    def load(self, path: str):
        if not os.path.exists(path):
            logger.warning("[MLP] Warning: model file %s not found. Using fresh untrained model.", path)
            return self

        self.model = joblib.load(path)
        logger.info("[MLP] Loaded model from %s", path)
        return self
