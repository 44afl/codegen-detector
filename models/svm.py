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

        proba = self.model.predict_proba(X)[:, 1]
        return proba

    def save(self, path: str):
        joblib.dump(self.model, path)
        return path

    def load(self, path: str):
        self.model = joblib.load(path)
        return self
