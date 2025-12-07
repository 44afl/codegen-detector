from flask import Flask, jsonify, request, Request, json
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


from models.adaboost import AdaBoostStrategy
from core.prediction_facade import PredictionFacade
from core.preprocessor import Preprocessor

# ====== MODEL LOAD ======
from models.adaboost import AdaBoostStrategy
from core.preprocessor import Preprocessor
from features.extractors.basic import BasicFeatureExtractor
from core.prediction_facade import PredictionFacade
from models.lstm import LSTMModel

model = AdaBoostStrategy().load("data/adaboost.pkl")
preprocessor = Preprocessor()
feature_extractor = BasicFeatureExtractor()

facade = PredictionFacade(
    model=model,
    preprocessor=preprocessor,
    feature_extractor=feature_extractor
)

#LSTM 
lstm_model = LSTMModel().load("data/lstm_model.pkl")
preprocessor = Preprocessor()        # dacă îl folosiți
# dacă LSTMModel lucrează direct pe text brut, probabil feature_extractor nu mai e necesar

lstm_facade = PredictionFacade(
    model=lstm_model,
    preprocessor=preprocessor,   # sau None, dacă nu preprocesați textul
    feature_extractor=None       # sau ceva dummy
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


@app.route("/predict/lstm", methods=["POST"])
def predict_lstm():
    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    code = file.read().decode("utf-8", errors="ignore")

    try:
        result = lstm_facade.analyze(code)
        return jsonify({
            "model": "LSTM",
            **result,
            "filename": file.filename
        })
    except Exception as e:
        print("LSTM error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
    






