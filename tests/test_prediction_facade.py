import pytest
from core.prediction_facade import PredictionFacade


class DummyPreprocessor:
    def __init__(self):
        self.calls = []

    def clean(self, code: str):
        self.calls.append(("clean", code))
        return "CLEANED_CODE"


class DummyFeatureExtractor:
    def __init__(self, features):
        self.features = features
        self.calls = []

    def extract_features(self, processed: str):
        self.calls.append(("extract_features", processed))
        return self.features


class DummyModel:
    def __init__(self, prob):
        self.prob = prob
        self.calls = []

    def predict(self, X):
        self.calls.append(("predict", X))
        return [self.prob]


def test_analyze_calls_components_in_order_and_returns_machine_label():
    model = DummyModel(prob=0.8)
    pre = DummyPreprocessor()
    fx = DummyFeatureExtractor(features={
        "n_lines": 10,
        "avg_line_len": 12.5,
        "n_chars": 200,
        "n_tabs": 2,
        "n_spaces": 50,
        "n_keywords": 7,
    })

    facade = PredictionFacade(model=model, preprocessor=pre, feature_extractor=fx)
    out = facade.analyze("print('hi')")

    # calls
    assert pre.calls == [("clean", "print('hi')")]
    assert fx.calls == [("extract_features", "CLEANED_CODE")]
    assert model.calls, "Model.predict should be called"

    # output
    assert out["probability_machine"] == pytest.approx(0.8)
    assert out["label"] == "machine"


def test_analyze_returns_human_when_prob_is_equal_or_below_threshold():
    model = DummyModel(prob=0.5)
    pre = DummyPreprocessor()
    fx = DummyFeatureExtractor(features={})

    facade = PredictionFacade(model=model, preprocessor=pre, feature_extractor=fx)
    out = facade.analyze("x=1")

    assert out["probability_machine"] == pytest.approx(0.5)
    assert out["label"] == "human"


def test_feature_order_and_missing_features_default_to_zero():
    model = DummyModel(prob=0.9)
    pre = DummyPreprocessor()
    fx = DummyFeatureExtractor(features={
        "n_lines": 3,
        "n_chars": 120,
    })

    facade = PredictionFacade(model=model, preprocessor=pre, feature_extractor=fx)
    facade.analyze("code")

    _, X = model.calls[0]
    assert len(X) == 1
    row = X[0]
    assert row == [
        3.0,    # n_lines
        0.0,    # avg_line_len (missing)
        120.0,  # n_chars
        0.0,    # n_tabs (missing)
        0.0,    # n_spaces (missing)
        0.0,    # n_keywords (missing)
    ]


def test_non_numeric_feature_values_are_handled_as_float_if_possible():
    model = DummyModel(prob=0.6)
    pre = DummyPreprocessor()
    fx = DummyFeatureExtractor(features={
        "n_lines": "4",
        "avg_line_len": "10.2",
        "n_chars": 50,
        "n_tabs": 0,
        "n_spaces": 5,
        "n_keywords": 1,
    })

    facade = PredictionFacade(model=model, preprocessor=pre, feature_extractor=fx)
    facade.analyze("code")

    _, X = model.calls[0]
    assert X[0][0] == 4.0
    assert X[0][1] == pytest.approx(10.2)



"""

venv) admin@Mac codegen-detector % pytest tests/test_prediction_facade.py \
  --cov=core.prediction_facade \
  --cov-report=term-missing

================================================================================ test session starts ================================================================================
platform darwin -- Python 3.13.7, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/admin/Documents/Facultate/FII/Tehnici avansate de ingineria programarii/codegen-detector
configfile: pyproject.toml
plugins: cov-7.0.0
collected 4 items                                                                                                                                                                   

tests/test_prediction_facade.py ....                                                                                                                                          [100%]

================================================================================== tests coverage ===================================================================================
_________________________________________________________________ coverage: platform darwin, python 3.13.7-final-0 __________________________________________________________________

Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
core/prediction_facade.py      13      0   100%
---------------------------------------------------------
TOTAL                          13      0   100%
================================================================================= 4 passed in 0.04s =================================================================================
(venv) admin@Mac codegen-detector % 


"""