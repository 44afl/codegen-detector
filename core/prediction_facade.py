class PredictionFacade:
    def __init__(self, model, preprocessor, feature_extractor):
        self.model = model
        self.preprocessor = preprocessor
        self.feature_extractor = feature_extractor

        self.feature_order = [
            "n_lines",
            "avg_line_len",
            "n_chars",
            "n_tabs",
            "n_spaces",
            "n_keywords"
        ]

    def analyze(self, code: str):
        processed = self.preprocessor.clean(code)
        features = self.feature_extractor.extract_features(processed)

        row = [float(features.get(f, 0)) for f in self.feature_order]
        X = [row]

        proba = self.model.predict(X)

        return {
            "probability_machine": float(proba[0]),
            "label": "machine" if proba[0] > 0.5 else "human"
        }