from typing import Any, Iterable, List

from aop.aspects import timeit, log_call

from .service import ModelService


# Adapter for OpenAI Detector
class OpenAIDetectorAdapter(ModelService):
    def __init__(self, wrapped: Any = None):
        self._wrapped = wrapped
        if self._wrapped is None:
            try:
                import openai_detector as _od

                self._wrapped = _od
            except Exception:
                self._wrapped = None

    def train(self, X, y):
        raise NotImplementedError("Training is not supported by OpenAIDetectorAdapter")

    def _normalize_inputs(self, X) -> List[str]:
        if isinstance(X, str):
            return [X]
        if isinstance(X, Iterable):
            return [str(x) for x in X]
        return [str(X)]

    @timeit
    @log_call
    def predict(self, X):
        if self._wrapped is None:
            raise RuntimeError(
                "No wrapped detector available. Install `openai_detector` or pass a detector instance."
            )

        texts = self._normalize_inputs(X)

        if hasattr(self._wrapped, "predict"):
            return self._wrapped.predict(texts)

        if hasattr(self._wrapped, "classify"):
            return self._wrapped.classify(texts)

        if callable(self._wrapped):
            return self._wrapped(texts)

        for name in ("detect", "analyze", "score"):
            fn = getattr(self._wrapped, name, None)
            if callable(fn):
                return fn(texts)

        raise AttributeError(
            "Wrapped detector has no known prediction method (predict/classify/callable)"
        )
