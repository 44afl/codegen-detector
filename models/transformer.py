from .service import ModelService

class TransformerModel(ModelService):
    def train(self, batch: str):
        pass

    def predict(self, seq: str) -> str:
        pass