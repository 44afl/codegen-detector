from .service import ModelService
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from typing import Union, Iterable


class SVMModel(ModelService):
    """SVM-based model for detecting AI-generated text.

    Uses a TF-IDF vectorizer and a LinearSVC wrapped in a
    CalibratedClassifierCV so we can return probabilities.
    """

    def __init__(self, **kwargs):
        # kwargs forwarded to the LinearSVC constructor
        self.model = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(max_features=20000, ngram_range=(1, 2), stop_words="english"),
                ),
                (
                    "clf",
                    CalibratedClassifierCV(LinearSVC(max_iter=10000, **kwargs), cv=5),
                ),
            ]
        )

    def train(self, X: Iterable[str], y: Iterable[float]):
        """Train the pipeline on raw text inputs and labels.

        Returns self for chaining.
        """
        self.model.fit(X, y)
        return self

    def predict(self, X: Union[str, Iterable[str]]):
        """Return probability (or probabilities) that input(s) are AI-generated.

        If a single string is provided, returns a float in [0,1]. If an iterable
        (list/array) is provided, returns a numpy array of probabilities.
        """
        single = False
        if isinstance(X, str):
            single = True
            X = [X]

        proba = self.model.predict_proba(X)[:, 1]

        return float(proba[0]) if single else proba

    def save(self, path: str):
        joblib.dump(self.model, path)
        return path

    def load(self, path: str):
        self.model = joblib.load(path)
        return self