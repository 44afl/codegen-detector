# Builder - Design Pattern
from models.transformer import TransformerModel, ModelStrategy
from models.svm import SVMStrategy
from models.adaboost import AdaBoostStrategy
from models.lstm import LSTMStrategy
from data.dataset import Dataset

class Trainer:
    def __init__(self):
        self.model = None    
        self.dataset = None 
        self.model_strategy = None
        self.results = {}
        
    def prepareData(self, dataset: Dataset):
        self.dataset = dataset
        return self

    def setModel(self, model_strategy: ModelStrategy):
        self.model_strategy = model_strategy
        return self
        
    def initializeModel(self):
        if not self.model_strategy:
            raise ValueError("Undefined model strategy")
        self.model = self.model_strategy.build()
        return self

    def fitModel(self):
        if not self.model or not self.dataset:
            raise ValueError("Undefined model or dataset")

        self.results["train"] = f"{type(self.model).__name__} trained"
        return self

    def evaluateModel(self):
        if not self.model:
            raise ValueError("Undefined model")
        
        self.results["eval"] = f"{type(self.model).__name__} evaluated"
        return self

    def build(self):
        return self