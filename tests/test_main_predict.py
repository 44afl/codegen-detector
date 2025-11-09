import flask
import pytest

import main
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
