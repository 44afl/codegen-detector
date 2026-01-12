import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

from core.preprocessor import Preprocessor
from features.extractors.basic import BasicFeatureExtractor
from core.prediction_facade import PredictionFacade

from models.lstm import LSTMModel
from models.adaboost import AdaBoostStrategy
from models.svm import SVMModel

SAMPLE_PATH = "data/test_sample.parquet"

def make_X(df, pre, fx):
    feature_order = PredictionFacade(None, None, None).feature_order
    rows = []
    for code in df["code"]:
        cleaned = pre.clean(str(code))
        feats = fx.extract_features(cleaned)
        rows.append([float(feats.get(k, 0)) for k in feature_order])
    return np.asarray(rows, dtype="float32")

def main():
    df = pd.read_parquet(SAMPLE_PATH)
    y_true = df["label"].astype(int).values

    pre = Preprocessor()
    fx = BasicFeatureExtractor()
    X = make_X(df, pre, fx)

    lstm = LSTMModel().load("data/lstm_model.pkl")
    ada  = AdaBoostStrategy().load("data/adaboost.pkl")
    svm  = SVMModel().load("data/svm_model.pkl")

    p_lstm = np.asarray(lstm.predict(X), dtype="float32")
    p_ada  = np.asarray(ada.predict(X), dtype="float32")
    p_svm  = np.asarray(svm.predict(X), dtype="float32")

    thresholds = np.linspace(0.1, 0.95, 18)

    best = {"w": None, "t": None, "f1": -1.0}

    # grid mic de greutăți (sum=1)
    weights = []
    for w1 in [0.5, 0.6, 0.7, 0.8, 0.9]:
        for w2 in [0.0, 0.1, 0.2, 0.3, 0.4]:
            w3 = 1.0 - w1 - w2
            if w3 < 0 or w3 > 0.5:
                continue
            weights.append((w1, w2, w3))

    for (w1, w2, w3) in weights:
        p = w1 * p_lstm + w2 * p_ada + w3 * p_svm
        for t in thresholds:
            y_pred = (p >= t).astype(int)
            f1 = f1_score(y_true, y_pred, average="macro")
            if f1 > best["f1"]:
                best = {"w": (w1, w2, w3), "t": float(t), "f1": float(f1)}

    print("✅ BEST ENSEMBLE")
    print("weights (lstm, ada, svm) =", best["w"])
    print("threshold =", best["t"])
    print("macro-F1 =", best["f1"])

if __name__ == "__main__":
    main()
