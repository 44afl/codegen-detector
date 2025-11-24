from typing import Dict, Any
from data.dataset import Dataset
from models.service import ModelService
from events.observer import ProgressSubject, ProgressObserver
from aop.aspects import log_call, timeit, debug

class Trainer(ProgressSubject):
    def __init__(self):
        self.model_strategy: ModelService | None = None
        self.dataset: Dataset | None = None
        self.trained_model: ModelService | None = None
        self.results: dict = {}
        self._observers: list[ProgressObserver] = []

    # Observer methods 
    def attach(self, observer: ProgressObserver) -> None:
        self._observers.append(observer)

    def detach(self, observer: ProgressObserver) -> None:
        self._observers.remove(observer)

    def notify(self, payload: Dict[str, Any]) -> None:
        for o in self._observers:
            o.update(self, payload)

    # Builder steps
    @timeit 
    @log_call      
    def prepareData(self, dataset: Dataset):
        self.dataset = dataset
        self.notify({"step": "load_data", "progress": 10})
        return self

    @timeit 
    @log_call      
    def setModel(self, model_strategy: ModelService):
        self.model_strategy = model_strategy
        self.notify({"step": "set_model", "progress": 20})
        return self

    @timeit 
    @log_call     
    def initializeModel(self):
        if not self.model_strategy:
            raise ValueError("Model strategy not set")
        self.trained_model = self.model_strategy
        self.notify({"step": "init_model", "progress": 40})
        return self

    @timeit 
    @log_call      
    def fitModel(self):
        if not self.trained_model or not self.dataset:
            raise ValueError("Missing model or dataset")
        self.trained_model.train(self.dataset.X, self.dataset.y)
        self.results["train_status"] = "ok"
        self.notify({"step": "fit", "progress": 80})
        return self

    @timeit 
    @log_call      
    def evaluateModel(self):
        # aici mai târziu puneți Accuracy, F1 etc.
        self.results["eval_status"] = "not_implemented"
        self.notify({"step": "eval", "progress": 100})
        return self

    @timeit 
    @log_call
    def build(self):
        return self.trained_model, self.results
