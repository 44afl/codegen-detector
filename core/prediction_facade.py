# Facade Design Pattern
class PredictionFacade:
    def __init__(self, model, preprocessor, feature_extractor):
        self.model = model
        self.preprocessor = preprocessor
        self.feature_extractor = feature_extractor

    def analyze(self, code: str):
        processed = self.preprocessor.clean(code)
        features = self.feature_extractor.extract_features(processed)
        return self.model.predict(features)