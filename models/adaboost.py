# models/adaboost.py
import joblib
from sklearn.ensemble import AdaBoostClassifier
from .service import ModelService  


class AdaBoostStrategy(ModelService):
    def __init__(self, **kwargs):
        self.model = AdaBoostClassifier(
            n_estimators=50,
            learning_rate=1.0,
            # algorithm="SAMME",
            **kwargs
        )

    def train(self, X, y):
        self.model.fit(X, y)
        return self

    def predict(self, X):
        proba = self.model.predict_proba(X)[:, 1]
        return proba

    # ------------------------------------------------------------
    # SAVE MODEL
    # ------------------------------------------------------------
    def save(self, path: str):
        joblib.dump(self.model, path)
        return path

    # ------------------------------------------------------------
    # LOAD MODEL
    # ------------------------------------------------------------
    def load(self, path: str):
        self.model = joblib.load(path)
        return self
