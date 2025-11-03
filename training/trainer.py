# Builder - Design Pattern
from models.transformer import TransformerModel, ModelStrategy
from data.dataset import Dataset

class Trainer:
    def __init__(self):
        self.model = None    
        self.dataset = None 
        self.results = {}
        
    def prepareData(self, dataset: Dataset):
        pass

    def setModel(self, model_strategy: ModelStrategy):
        self.model_strategy = model_strategy
        
    def initializeModel(self):
        pass

    def fitModel(self):
        pass

    def evaluateModel(self):
        pass

    def build(self):
        pass