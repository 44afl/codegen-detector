import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

class Dataset:
    def __init__(self, X, y, vectorizer=None):
        self.X = X
        self.y = y
        self.vectorizer = vectorizer

    @classmethod
    def from_parquet(cls, path: str):
        df = pd.read_parquet(path)
        df = df.dropna(subset=["code", "label"])

        texts = df["code"].astype(str).tolist()
        y = df["label"].astype(int).values

        vectorizer = TfidfVectorizer(max_features=6)
        X = vectorizer.fit_transform(texts)

        return cls(X, y, vectorizer)
