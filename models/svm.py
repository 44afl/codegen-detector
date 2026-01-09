from .service import ModelService
import joblib
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from typing import Union, Iterable


class SVMModel(ModelService):
    """SVM-based model for detecting AI-generated text.

    Works with pre-vectorized features from the Dataset class.
    Uses LinearSVC wrapped in CalibratedClassifierCV for probabilities.
    """

    def __init__(self, **kwargs):
        # kwargs forwarded to the LinearSVC constructor
        self.model = CalibratedClassifierCV(LinearSVC(max_iter=10000, **kwargs), cv=5)

    def train(self, X, y):
        """Train the model on pre-vectorized features and labels.

        X: (n_samples, n_features) – can be sparse matrix (csr_matrix)
        y: label vector (0/1)

        Returns self for chaining.
        """
        # Convert sparse matrix to dense if needed
        if hasattr(X, "toarray"):
            X = X.toarray()

        X = np.asarray(X, dtype="float32")
        y = np.asarray(y)

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if X.ndim != 2:
            raise ValueError(f"[SVM] X should be 2D, got shape {X.shape}")

        print("[SVM] Starting fit on", X.shape)
        self.model.fit(X, y)
        print("[SVM] Finished fit.")
        return self

    def predict(self, X):
        """Return probability (or probabilities) that input(s) are AI-generated.

        X: pre-vectorized features, shape (n_samples, n_features)
        Returns numpy array of probabilities in [0,1].
        """
        # Convert sparse matrix to dense if needed
        if hasattr(X, "toarray"):
            X = X.toarray()

        X = np.asarray(X, dtype="float32")

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if X.ndim != 2:
            raise ValueError(f"[SVM] X should be 2D in predict, got shape {X.shape}")

        try:
            proba = self.model.predict_proba(X)[:, 1]
        except AttributeError:
            # Fallback: model might not be calibrated, use decision_function
            print("[SVM WARNING] predict_proba not available, using decision_function")
            decision = self.model.decision_function(X)
            # Normalize decision function to [0,1] using sigmoid
            proba = 1 / (1 + np.exp(-decision))
        
        # Safety check: clip to [0,1] range
        proba = np.clip(proba, 0.0, 1.0)
        
        # Debug: check for invalid values
        if np.any(proba < 0) or np.any(proba > 1):
            print(f"[SVM WARNING] Invalid probabilities detected: min={proba.min()}, max={proba.max()}")
            proba = np.clip(proba, 0.0, 1.0)
        
        return proba

    def save(self, path: str):
        joblib.dump(self.model, path)
        return path

    def load(self, path: str):
        self.model = joblib.load(path)
        return self
