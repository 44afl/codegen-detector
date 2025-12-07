from .service import ModelService
import os
import numpy as np
import joblib
from sklearn.neural_network import MLPClassifier


class LSTMModel(ModelService):
    """
    'LSTMModel' în sens de model NN diferit de AdaBoost/SVM,
    implementat ca MLP (rețea neuronală feed-forward) peste
    aceleași features numerice folosite de AdaBoost.

    Se integrează în același pipeline Trainer -> prepareData -> X, y.
    """

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

    def train(self, X, y):
        """
        X: (n_samples, n_features) – poate fi și csr_matrix (sparse)
        y: vector etichete (0/1)
        """
        # Dacă e matrice sparse, o facem densă
        if hasattr(X, "toarray"):
            X = X.toarray()

        X = np.asarray(X, dtype="float32")
        y = np.asarray(y)

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if X.ndim != 2:
            raise ValueError(f"[MLP] X should be 2D, got shape {X.shape}")

        print("[MLP] Starting fit on", X.shape)
        self.model.fit(X, y)
        print("[MLP] Finished fit.")
        return self

    def predict(self, X):
        """
        Returnează probabilitățile clasei pozitive (AI-generated),
        la fel ca AdaBoost: vector de proba în [0,1].
        """
        if hasattr(X, "toarray"):
            X = X.toarray()

        X = np.asarray(X, dtype="float32")

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if X.ndim != 2:
            raise ValueError(f"[MLP] X should be 2D in predict, got shape {X.shape}")

        proba = self.model.predict_proba(X)[:, 1]
        return proba

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        return path

    def load(self, path: str):
        if not os.path.exists(path):
            print(f"[MLP] Warning: model file {path} not found. Using fresh untrained model.")
            return self

        self.model = joblib.load(path)
        print(f"[MLP] Loaded model from {path}")
        return self
