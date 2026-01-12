import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from core.preprocessor import Preprocessor
from features.extractors.basic import BasicFeatureExtractor
from core.prediction_facade import PredictionFacade

from models.adaboost import AdaBoostStrategy
from models.svm import SVMModel
from models.lstm import LSTMModel
from models.transformer import TransformerModel


def make_X(df: pd.DataFrame, pre: Preprocessor, fx: BasicFeatureExtractor) -> np.ndarray:
    """
    X numeric pentru modelele clasice: exact ca PredictionFacade
    """
    feature_order = PredictionFacade(None, None, None).feature_order
    rows = []
    for code in df["code"].astype(str).tolist():
        processed = pre.clean(code)
        feats = fx.extract_features(processed)
        rows.append([float(feats.get(f, 0.0)) for f in feature_order])
    return np.asarray(rows, dtype="float32")


def metrics_from_proba(y_true, proba, threshold=0.5):
    proba = np.asarray(proba, dtype="float32").reshape(-1)
    y_hat = (proba >= threshold).astype(int)

    out = {
        "accuracy": float(accuracy_score(y_true, y_hat)),
        "f1": float(f1_score(y_true, y_hat)),
    }
    try:
        out["auc"] = float(roc_auc_score(y_true, proba))
    except Exception:
        out["auc"] = None
    return out


def pick_probability_from_transformer_result(result: dict) -> float:

    for k in ("probability_machine", "probability", "proba", "score", "ai_probability"):
        if k in result:
            return float(result[k])
    # fallback: dacă întoarce direct float
    if isinstance(result, (float, int)):
        return float(result)
    raise KeyError(f"Transformer result has no known probability key. Got keys: {list(result.keys())}")


def evaluate_classic(name: str, model, X_val, y_val):
    proba = model.predict(X_val)
    m = metrics_from_proba(y_val, proba)
    print(f"{name}: {m}")
    return m


def evaluate_transformer(model: TransformerModel, df_val: pd.DataFrame, y_val: np.ndarray):
    probas = []
    for code in df_val["code"].astype(str).tolist():
        res = model.predict(code)  # text brut
        probas.append(pick_probability_from_transformer_result(res))

    m = metrics_from_proba(y_val, probas)
    print(f"transformer: {m}")
    return m


def main():
    val = pd.read_parquet("data/validation.parquet")
    y_val = val["label"].astype(int).values

    pre = Preprocessor()
    fx = BasicFeatureExtractor()
    X_val = make_X(val, pre, fx)

    results = {}

    try:
        adaboost = AdaBoostStrategy().load("data/adaboost.pkl")
        results["adaboost"] = evaluate_classic("adaboost", adaboost, X_val, y_val)
    except Exception as e:
        print("Could not evaluate adaboost:", e)

    try:
        svm = SVMModel().load("data/svm_model.pkl")
        results["svm"] = evaluate_classic("svm", svm, X_val, y_val)
    except Exception as e:
        print("Could not evaluate svm:", e)

    try:
        lstm = LSTMModel().load("data/lstm_model.pkl")
        results["lstm"] = evaluate_classic("lstm", lstm, X_val, y_val)
    except Exception as e:
        print("Could not evaluate lstm:", e)

    try:
        transformer = TransformerModel().load("data/transformer_model.pkl")

        # ⚠️ Dacă e lent, poți limita la primele N exemple:
        # N = 500
        # val_small = val.head(N)
        # y_small = y_val[:N]
        # results["transformer"] = evaluate_transformer(transformer, val_small, y_small)

        results["transformer"] = evaluate_transformer(transformer, val, y_val)
    except Exception as e:
        print("Could not evaluate transformer:", e)

    # 3) best by F1
    if results:
        best = max(results.items(), key=lambda kv: kv[1]["f1"])
        print("\nBEST by F1:", best[0], best[1])


if __name__ == "__main__":
    main()
