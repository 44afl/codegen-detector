from flask import Flask, Request
from models import MockModel
import logging
from data.dataset import Dataset
from models.adaboost import AdaBoostStrategy
from training.trainer import Trainer

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
    
    if not request.is_json:
        return "<p>Missing input</p>", 400

    sample_input = request.json.get("input", "")

    if not sample_input:
        return "<p>Missing input</p>", 400
    
    predictions = [model.predict(sample_input) for model in models]
    logger.info(f"Predictions: {predictions}")
    avg_prediction = sum(predictions) / len(predictions)
    return f"<p>Average Prediction: {avg_prediction}</p>"


if __name__ == "__main__":
    app.run(debug=True)
    dataset = Dataset.from_parquet("data/task_a/task_a_training_set.parquet")
    trainer = (
        Trainer()
        .prepareData(dataset)
        .setModel(AdaBoostStrategy())
        .initializeModel()
        .fitModel()
        .evaluateModel()
    )

    model, results = trainer.build()
    print(results)






