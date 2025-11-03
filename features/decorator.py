# features/decorator.py
from __future__ import annotations
from abc import ABC, abstractmethod
from features.feature_extractor import FeatureExtractor

# Abstract Decorator
class FeatureDecorator(FeatureExtractor):
    def __init__(self, extractor: FeatureExtractor) -> None:
        self._extractor = extractor

    def extract_features(self, code: str) -> dict:
        return self._extractor.extract_features(code)

# Concrete Decorators
class CommentRemovalDecorator(FeatureDecorator):
    def extract_features(self, code: str) -> dict:
        pass

class PerplexityDecorator(FeatureDecorator):
    def extract_features(self, code: str) -> dict:
        pass

class BurstinessDecorator(FeatureDecorator):
    def extract_features(self, code: str) -> dict:
        pass
