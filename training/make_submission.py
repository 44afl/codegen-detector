import numpy as np
import pandas as pd

from core.preprocessor import Preprocessor
from features.extractors.basic import BasicFeatureExtractor
from core.prediction_facade import PredictionFacade

from models.lstm import LSTMModel
from models.svm import SVMModel

TEST_PATH = "data/test.parquet"
OUT_PATH = "submission.csv"

W_LSTM = 0.8
W_SVM = 0.2
THRESHOLD = 0.95

def make_X(df, pre, fx):
    feature_order = PredictionFacade(None, None, None).feature_order
    rows = []
    for code in df["code"]:
        cleaned = pre.clean(str(code))
        feats = fx.extract_features(cleaned)
        rows.append([float(feats.get(k, 0)) for k in feature_order])
    return np.asarray(rows, dtype="float32")

def main():
    df = pd.read_parquet(TEST_PATH)

    # Kaggle de obicei are "ID" (exact ca sample_submission.csv)
    id_col = "ID" if "ID" in df.columns else ("id" if "id" in df.columns else None)
    if id_col is None:
        raise ValueError(f"Nu găsesc coloană ID/id în test.parquet. Columns: {list(df.columns)}")

    pre = Preprocessor()
    fx = BasicFeatureExtractor()
    X = make_X(df, pre, fx)

    lstm = LSTMModel().load("data/lstm_model.pkl")
    svm  = SVMModel().load("data/svm_model.pkl")

    p_lstm = np.asarray(lstm.predict(X), dtype="float32")
    p_svm  = np.asarray(svm.predict(X), dtype="float32")

    p = W_LSTM * p_lstm + W_SVM * p_svm
    y = (p >= THRESHOLD).astype(int)

    sub = pd.DataFrame({
        "ID": df[id_col].astype(int).values,
        "label": y.astype(int)
    })

    sub.to_csv(OUT_PATH, index=False)
    print(f"✅ Saved {OUT_PATH} with {len(sub)} rows")
    print("label distribution:", sub["label"].value_counts().to_dict())

if __name__ == "__main__":
    main()
