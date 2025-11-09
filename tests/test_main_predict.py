import flask
import pytest

#import main

# ---- Dynamically import main.py ----
import os, sys, importlib.util, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  

MAIN_PATH = ROOT / "main.py"
spec = importlib.util.spec_from_file_location("main", MAIN_PATH)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
# ---------------------------------------------------
 
from models import MockModel



def _wrap_predict(original_predict):
    def view_func():
        return original_predict(flask.request)

    return view_func


def test_predict_post_returns_average():
    main.models = [MockModel(), MockModel()]
    original = main.predict
    sample = "abc"
    with main.app.test_request_context(
        "/predict", method="POST", json={"input": sample}
    ):
        resp = original(flask.request)

    assert isinstance(resp, str)
    text = resp

    expected_single = (sum([ord(c) for c in str(sample)]) % 100) / 100.0
    assert f"Average Prediction: {expected_single}" in text


def test_predict_get_returns_405():
    main.models = [MockModel()]
    original = main.predict
    with main.app.test_request_context("/predict", method="GET"):
        resp = original(flask.request)

    assert isinstance(resp, tuple)
    body, status = resp
    assert status == 405
    assert "Method Not Allowed" in body


def test_predict_missing_input_returns_400():
    with main.app.test_request_context("/predict", method="POST", json={}):
        resp = main.predict(flask.request)

    assert isinstance(resp, tuple)
    body, status = resp
    assert status == 400
    assert "Missing input" in body

