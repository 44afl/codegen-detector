from timeit import timeit
from typing import Any, Dict, Iterable, Optional
from aop.aspects import log_call, timeit

try:
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        roc_auc_score,
        confusion_matrix,
    )

    _HAVE_SKLEARN = True
except Exception:
    _HAVE_SKLEARN = False


# Template Method
class BaseEvaluator:
    @timeit
    @log_call
    def evaluate(
        self, model: Any, X: Iterable, y: Optional[Iterable] = None, **kwargs
    ) -> Dict:
        if X is None:
            raise ValueError("X required")
        y_pred, extras = self.predict(model, X, **kwargs)
        metrics = {}
        if y is not None:
            metrics = self.compute_metrics(y, y_pred, extras or {})
        return self.report(metrics, extras or {})

    def predict(self, model: Any, X: Iterable, **kwargs):
        raise NotImplementedError

    def compute_metrics(
        self, y_true: Iterable, y_pred: Iterable, extras: Optional[Dict] = None
    ) -> Dict:
        raise NotImplementedError

    def report(self, metrics: Dict, extras: Optional[Dict] = None) -> Dict:
        return metrics


class ClassificationEvaluator(BaseEvaluator):
    @timeit
    @log_call
    def predict(self, model: Any, X: Iterable, **kwargs):
        y_pred = None
        extras = {}
        try:
            if callable(model):
                res = model(X)
                if isinstance(res, tuple):
                    y_pred = res[0]
                    if len(res) > 1:
                        extras = res[1]
                else:
                    y_pred = res
        except Exception:
            y_pred = None
        if y_pred is None and hasattr(model, "predict"):
            try:
                y_pred = model.predict(X)
            except Exception:
                y_pred = [model.predict(x) for x in X]
        if hasattr(model, "predict_proba"):
            try:
                extras["probs"] = model.predict_proba(X)
            except Exception:
                extras.setdefault("probs", None)
        return y_pred, extras

    @timeit
    @log_call
    def compute_metrics(
        self, y_true: Iterable, y_pred: Iterable, extras: Optional[Dict] = None
    ) -> Dict:
        extras = extras or {}
        m: Dict = {}
        if _HAVE_SKLEARN:
            try:
                m["accuracy"] = float(accuracy_score(y_true, y_pred))
            except Exception:
                m["accuracy"] = _simple_accuracy(y_true, y_pred)
            try:
                m["f1"] = float(f1_score(y_true, y_pred, average="binary"))
            except Exception:
                m["f1"] = _simple_f1(y_true, y_pred)
            probs = extras.get("probs")
            if probs is not None:
                try:
                    if hasattr(probs[0], "__len__") and len(probs[0]) > 1:
                        scores = [p[1] for p in probs]
                    else:
                        scores = probs
                    m["auc"] = float(roc_auc_score(y_true, scores))
                except Exception:
                    pass
            try:
                m["confusion_matrix"] = confusion_matrix(y_true, y_pred).tolist()
            except Exception:
                pass
        else:
            m["accuracy"] = _simple_accuracy(y_true, y_pred)
            m["f1"] = _simple_f1(y_true, y_pred)
        return m


def _simple_accuracy(y_true: Iterable, y_pred: Iterable) -> float:
    yt = list(y_true)
    yp = list(y_pred)
    if not yt or len(yt) != len(yp):
        return 0.0
    return sum(1 for a, b in zip(yt, yp) if a == b) / len(yt)


def _simple_f1(y_true: Iterable, y_pred: Iterable) -> float:
    yt = list(y_true)
    yp = list(y_pred)
    if not yt or len(yt) != len(yp):
        return 0.0
    tp = sum(1 for a, b in zip(yt, yp) if a and b)
    fp = sum(1 for a, b in zip(yt, yp) if not a and b)
    fn = sum(1 for a, b in zip(yt, yp) if a and not b)
    if tp == 0:
        return 0.0
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)
