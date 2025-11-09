from abc import ABC, abstractmethod


# Strategy Design Pattern
class ModelService(ABC):
    @abstractmethod
    def train(self, X, y):
        pass

    # Returns a float between 0 and 1 indicating the prediction
    @abstractmethod
    def predict(self, X) -> float:
        pass
