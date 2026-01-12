import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

from core.preprocessor import Preprocessor
from features.extractors.basic import BasicFeatureExtractor
from core.prediction_facade import PredictionFacade
from models.lstm import LSTMModel   # sau modelul ales

MODEL_PATH = "data/lstm_model.pkl"
DATA_PATH = "data/test_sample.parquet"

def main():
    print("[CALIBRATION] Loading data...")
    df = pd.read_parquet(DATA_PATH)

    pre = Preprocessor()
    fx = BasicFeatureExtractor()

    model = LSTMModel().load(MODEL_PATH)

    feature_order = PredictionFacade(None, None, None).feature_order

    X = []
    y_true = df["label"].astype(int).values

    for code in df["code"]:
        cleaned = pre.clean(str(code))
        feats = fx.extract_features(cleaned)
        X.append([float(feats.get(k, 0)) for k in feature_order])

    X = np.array(X, dtype="float32")

    print("[CALIBRATION] Predicting probabilities...")
    proba = model.predict(X)

    thresholds = np.linspace(0.1, 0.9, 17)

    best_t = None
    best_f1 = -1

    for t in thresholds:
        y_pred = (proba >= t).astype(int)
        f1 = f1_score(y_true, y_pred, average="macro")
        print(f"threshold={t:.2f} -> macro-F1={f1:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_t = t

    print("\n✅ BEST THRESHOLD")
    print(f"threshold = {best_t}")
    print(f"macro-F1  = {best_f1}")

if __name__ == "__main__":
    main()
