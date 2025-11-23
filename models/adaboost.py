# models/adaboost.py
from sklearn.ensemble import AdaBoostClassifier
from .service import ModelService  

class AdaBoostStrategy(ModelService):
    def __init__(self, **kwargs):
       
        self.model = AdaBoostClassifier(
            n_estimators=50,
            learning_rate=1.0,
        #    algorithm="SAMME",
            **kwargs
        )

    def train(self, X, y):
        self.model.fit(X, y)
        return self

    def predict(self, X):
        """
        întoarce o probabilitate între 0 și 1 (clasa 1 = 'machine').
        """
        proba = self.model.predict_proba(X)[:, 1] 
        return proba
