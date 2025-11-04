from abc import ABC, abstractmethod


# Strategy Design Pattern
class ModelService(ABC):
    @abstractmethod
    def train(self, X, y):
        pass

    @abstractmethod
    def predict(self, X):
        pass
