from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any

class FeatureExtractor(ABC):
    @abstractmethod
    def extract_features(self, code: str, lang: str | None = None) -> Dict[str, Any]:
        ...
