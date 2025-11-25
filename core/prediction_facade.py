# core/prediction_facade.py
class PredictionFacade:
    def __init__(self, model, preprocessor, feature_extractor):
        self.model = model  
        self.preprocessor = preprocessor 
        self.feature_extractor = feature_extractor  

    def analyze(self, code: str):
        processed = self.preprocessor.clean(code)

        features = self.feature_extractor.extract_features(processed)

        X = [features]

        proba = self.model.predict(X)

        return {
            "probability_machine": float(proba[0]),
            "label": "machine" if proba[0] > 0.5 else "human"
        }