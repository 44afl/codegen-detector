from models.service import ModelService
from data.dataset import Dataset

class Trainer:
    def _init_(self):
        self.model_strategy: ModelService | None = None
        self.dataset: Dataset | None = None
        self.trained_model = None
        self.results: dict = {}

    def prepareData(self, dataset: Dataset):
        self.dataset = dataset
        return self

    def setModel(self, model_strategy: ModelService):
        self.model_strategy = model_strategy
        return self

    def initializeModel(self):
        if not self.model_strategy:
            raise ValueError("Model strategy not set")
        self.trained_model = self.model_strategy
        return self

    def fitModel(self):
        if not self.trained_model or not self.dataset:
            raise ValueError("Missing model or dataset")
        self.trained_model.train(self.dataset.X, self.dataset.y)
        self.results["train_status"] = "ok"
        return self

    def evaluateModel(self):
        self.results["eval_status"] = "not_implemented"
        return self

    def build(self):
        return self.trained_model, self.results