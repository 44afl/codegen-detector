from flask import Flask, Request
from models import MockModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
models = [MockModel()]


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/predict")
def predict(request: Request):
    if request.method != "POST":
        return "<p>Method Not Allowed</p>", 405

    sample_input = request.json.get("input", "")
    predictions = [model.predict(sample_input) for model in models]
    logger.info(f"Predictions: {predictions}")
    avg_prediction = sum(predictions) / len(predictions)
    return f"<p>Average Prediction: {avg_prediction}</p>"


if __name__ == "__main__":
    app.run(debug=True)
