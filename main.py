from flask import Flask, jsonify, request, Request, json
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
# CORS(app)



from models.adaboost import AdaBoostStrategy
from core.prediction_facade import PredictionFacade
from core.preprocessor import Preprocessor

# ====== MODEL LOAD ======
from models.adaboost import AdaBoostStrategy
from core.preprocessor import Preprocessor
from features.extractors.basic import BasicFeatureExtractor
from core.prediction_facade import PredictionFacade
from models.lstm import LSTMModel
from models.svm import SVMModel
from models.transformer import TransformerModel

import threading
import traceback

MODELS = {
    "adaboost": None,
    "lstm": None,
    "transformer": None,
    "svm": None
}

FACADES = {
    "adaboost": None,
    "lstm": None,
    "transformer": None,
    "svm": None
}


def load_models_thread():
    global MODELS, FACADES

    print("Loading models...")

    try:
        # ==== AdaBoost ====
        try:
            model = AdaBoostStrategy().load("data/adaboost.pkl")
            preprocessor = Preprocessor()
            feature_extractor = BasicFeatureExtractor()

            FACADES["adaboost"] = PredictionFacade(
                model=model,
                preprocessor=preprocessor,
                feature_extractor=feature_extractor
            )

            MODELS["adaboost"] = model
            print("AdaBoost Model has been loaded!")

        except Exception as e:
            print("Couldn't load AdaBoost:", e)
            traceback.print_exc()

        # ==== SVM ====

        # try:
        #     svm_model = SVMModel().load("data/svm_model.pkl")
        #     preprocessor = Preprocessor()

        #     FACADES["svm"] = PredictionFacade(
        #         model=svm_model,
        #         preprocessor=preprocessor,
        #         feature_extractor=None
        #     )

        #     MODELS["svm"] = svm_model
        #     print("SVM Model has been loaded!")

        # except Exception as e:
        #     print("Couldn't load SVM:", e)
        #     traceback.print_exc()


        # ==== LSTM ====
               
        try:
            lstm_model = LSTMModel().load("data/lstm_model.pkl")
            preprocessor = Preprocessor()
            feature_extractor_lstm = BasicFeatureExtractor()  

            FACADES["lstm"] = PredictionFacade(
                model=lstm_model,
                preprocessor=preprocessor,
                feature_extractor=feature_extractor_lstm   
            )

            MODELS["lstm"] = lstm_model
            print("LSTM Model has been loaded!")

        except Exception as e:
            print("Couldn't load LSTM:", e)
            traceback.print_exc()


        # ==== Transformer ====
        try:
            transformer_model = TransformerModel().load("data/transformer_model.pkl")
            preprocessor = Preprocessor()
            feature_extractor_transformer = BasicFeatureExtractor()  

            FACADES["transformer"] = PredictionFacade(
                model=transformer_model,
                preprocessor=preprocessor,
                feature_extractor=feature_extractor_transformer
            )

            MODELS["transformer"] = transformer_model
            print("Transformer Model has been loaded!")
        except Exception as e:
            print("Couldn't load Transformer: ", e)
            traceback.print_exc()

    except Exception as e:
        print(e)
        traceback.print_exc()

# MISC
def extract_code_from_request():
    if "file" not in request.files:
        return None, jsonify({"error": "Missing file"}), 400

    file = request.files["file"]
    if not file.filename:
        return None, jsonify({"error": "Empty filename"}), 400

    try:
        code = file.read().decode("utf-8", errors="ignore")
        return code, None, None
    except Exception as e:
        return None, jsonify({"error": f"Cannot read file: {e}"}), 500

@app.route("/predict/adaboost", methods=["POST"])
def predict_adaboost():

    if FACADES["adaboost"] is None:
        return jsonify({"error": "AdaBoost model not loaded"}), 503

    code, error, status = extract_code_from_request()
    if error:
        return error, status

    try:
        result = FACADES["adaboost"].analyze(code)
        return jsonify({
            "model": "AdaBoost",
            **result
        })
    except Exception as e:
        print("AdaBoost error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/predict/lstm", methods=["POST"])
def predict_lstm():

    if FACADES["lstm"] is None:
        return jsonify({"error": "LSTM model not loaded"}), 503

    code, error, status = extract_code_from_request()
    if error:
        return error, status

    try:
        result = FACADES["lstm"].analyze(code)
        return jsonify({
            "model": "LSTM",
            **result
        })
    except Exception as e:
        print("LSTM error:", e)
        return jsonify({"error": str(e)}), 500

# @app.route("/predict/svm", methods=["POST"])
# def predict_svm():

#     if FACADES["svm"] is None:
#         return jsonify({"error": "SVM model not loaded"}), 503

#     code, error, status = extract_code_from_request()
#     if error:
#         return error, status

#     try:
#         result = FACADES["svm"].analyze(code)
#         return jsonify({
#             "model": "SVM",
#             **result
#         })
#     except Exception as e:
#         print("SVM error:", e)
#         return jsonify({"error": str(e)}), 500

@app.route("/predict/transformer", methods=["POST"])
def predict_transformer():
    # folosim direct MODELS, nu FACADES
    if MODELS["transformer"] is None:
        return jsonify({"error": "Transformer model not loaded"}), 503

    code, error, status = extract_code_from_request()
    if error:
        return error, status

    try:
        result = MODELS["transformer"].predict(code)  # 👈 trimit text brut
        return jsonify({
            "model": "Transformer",
            **result
        })
    except Exception as e:
        print("Transformer error:", e)
        return jsonify({"error": str(e)}), 500



threading.Thread(target=load_models_thread, daemon=True).start()
# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
