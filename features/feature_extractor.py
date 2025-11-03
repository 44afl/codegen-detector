from abc import ABC, abstractmethod

# Template Method
class FeatureExtractor(ABC):
    def extract_features(self, code: str):
        cleaned = self._clean(code)
        tokens = self._tokenize(cleaned)
        return self._extract(tokens)

    @abstractmethod
    def _clean(self, code: str):
        pass

    @abstractmethod
    def _tokenize(self, code: str):
        pass

    @abstractmethod
    def _extract(self, tokens):
        pass