from flask import Flask, jsonify, request, Request
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

from models.adaboost import AdaBoostStrategy
from core.prediction_facade import PredictionFacade
from core.preprocessor import Preprocessor

# ====== MODEL LOAD ======
from models.adaboost import AdaBoostStrategy
from core.preprocessor import Preprocessor
from features.extractors.basic import BasicFeatureExtractor
from core.prediction_facade import PredictionFacade

model = AdaBoostStrategy().load("data/adaboost.pkl")
preprocessor = Preprocessor()
feature_extractor = BasicFeatureExtractor()

facade = PredictionFacade(
    model=model,
    preprocessor=preprocessor,
    feature_extractor=feature_extractor
)


# ====== ENDPOINT ======
@app.route("/predict/adaboost", methods=["POST"])
def predict_adaboost():
    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    try:
        code = file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return jsonify({"error": f"Cannot read file: {e}"}), 500

    try:
        result = facade.analyze(code)
        return jsonify({
            "model": "AdaBoost",
            **result,
            "filename": file.filename
        })
    except Exception as e:
        print("AdaBoost error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
    






