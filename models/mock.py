from .service import ModelService


class MockModel(ModelService):
    def train(self, X, y):
        pass

    def predict(self, X):
        return (sum([ord(c) for c in str(X)]) % 100) / 100.0
