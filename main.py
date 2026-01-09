from flask import Flask, jsonify, request, Request, json
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging
import traceback
import MOP.monitor1
from functools import wraps

from core.auth_db import AuthDB
from core.mail_service import MailService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_db = AuthDB()
mail_service = MailService()


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
from MOP.model_loaded_monitor import mop_model_load, mop_predict_only_if_loaded

AdaBoostStrategy.load = mop_model_load("adaboost")(AdaBoostStrategy.load)
AdaBoostStrategy.predict = mop_predict_only_if_loaded("adaboost")(AdaBoostStrategy.predict)

SVMModel.load = mop_model_load("svm")(SVMModel.load)
SVMModel.predict = mop_predict_only_if_loaded("svm")(SVMModel.predict)

LSTMModel.load = mop_model_load("lstm")(LSTMModel.load)
LSTMModel.predict = mop_predict_only_if_loaded("lstm")(LSTMModel.predict)

TransformerModel.load = mop_model_load("transformer")(TransformerModel.load)
TransformerModel.predict = mop_predict_only_if_loaded("transformer")(TransformerModel.predict)


import threading
import traceback

MODELS = {"adaboost": None, "lstm": None, "transformer": None, "svm": None}

FACADES = {"adaboost": None, "lstm": None, "transformer": None, "svm": None}


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
                feature_extractor=feature_extractor,
            )

            MODELS["adaboost"] = model
            print("AdaBoost Model has been loaded!")

        except Exception as e:
            print("Couldn't load AdaBoost:", e)
            traceback.print_exc()

        # ==== SVM ====

        try:
            svm_model = SVMModel().load("data/svm_model.pkl")
            preprocessor = Preprocessor()
            feature_extractor = BasicFeatureExtractor()

            FACADES["svm"] = PredictionFacade(
                model=svm_model,
                preprocessor=preprocessor,
                feature_extractor=feature_extractor,
            )

            MODELS["svm"] = svm_model
            print("SVM Model has been loaded!")

        except Exception as e:
            print("Couldn't load SVM:", e)
            traceback.print_exc()

        # ==== LSTM ====

        try:
            lstm_model = LSTMModel().load("data/lstm_model.pkl")
            preprocessor = Preprocessor()
            feature_extractor_lstm = BasicFeatureExtractor()

            FACADES["lstm"] = PredictionFacade(
                model=lstm_model,
                preprocessor=preprocessor,
                feature_extractor=feature_extractor_lstm,
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
                feature_extractor=feature_extractor_transformer,
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
        return jsonify({"model": "AdaBoost", **result})
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
        return jsonify({"model": "LSTM", **result})
    except Exception as e:
        print("LSTM error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/predict/svm", methods=["POST"])
def predict_svm():

    if FACADES["svm"] is None:
        return jsonify({"error": "SVM model not loaded"}), 503

    code, error, status = extract_code_from_request()
    if error:
        return error, status

    try:
        result = FACADES["svm"].analyze(code)
        
        print(f"[SVM] Raw probability: {result['probability_machine']}")

        prob = float(result['probability_machine'])
        if prob < 1e-10 or prob > (1 - 1e-10):
            print(f"[SVM WARNING] Extreme probability detected: {prob}")
            print("[SVM] Model might not be properly calibrated. Consider retraining.")
        
        return jsonify({"model": "SVM", **result})
    except Exception as e:
        print("SVM error:", e)
        return jsonify({"error": traceback.format_exc()}), 500


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
        return jsonify({"model": "Transformer", **result})
    except Exception as e:
        print("Transformer error:", e)
        return jsonify({"error": str(e)}), 500


threading.Thread(target=load_models_thread, daemon=True).start()

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No authorization token"}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        session = auth_db.get_session(token)
        if not session:
            return jsonify({"error": "Invalid or expired session"}), 401
        
        request.current_user = auth_db.get_user_by_id(session['user_id'])
        return f(*args, **kwargs)
    return decorated_function

@app.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    try:
        existing_user = auth_db.get_user_by_email(email)
        if existing_user:
            return jsonify({"error": "Email already registered"}), 409
        
        user_id = auth_db.create_user(email, password, full_name)
        session_token = auth_db.create_session(user_id)
        
        mail_service.send_welcome_email(email, full_name)
        
        return jsonify({
            "message": "User created successfully",
            "session_token": session_token,
            "user": {
                "id": user_id,
                "email": email,
                "full_name": full_name
            }
        }), 201
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({"error": "Failed to create user"}), 500

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    user = auth_db.get_user_by_email(email)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    if not auth_db.verify_password(password, user['password_hash']):
        return jsonify({"error": "Invalid credentials"}), 401
    
    if not user['is_active']:
        return jsonify({"error": "Account is disabled"}), 403
    
    session_token = auth_db.create_session(user['id'])
    
    return jsonify({
        "message": "Login successful",
        "session_token": session_token,
        "user": {
            "id": user['id'],
            "email": user['email'],
            "full_name": user['full_name']
        }
    }), 200

@app.route("/auth/logout", methods=["POST"])
@require_auth
def logout():
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token[7:]
        auth_db.delete_session(token)
    
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/auth/me", methods=["GET"])
@require_auth
def get_current_user():
    user = request.current_user
    subscription = auth_db.get_user_subscription(user['id'])
    
    return jsonify({
        "user": {
            "id": user['id'],
            "email": user['email'],
            "full_name": user['full_name'],
            "created_at": user['created_at']
        },
        "subscription": subscription
    }), 200

@app.route("/auth/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")
    
    if not email:
        return jsonify({"error": "Email required"}), 400
    
    user = auth_db.get_user_by_email(email)
    if not user:
        return jsonify({"message": "If the email exists, a reset link has been sent"}), 200
    
    token = auth_db.create_password_reset_token(user['id'])
    mail_service.send_password_reset(email, token)
    
    return jsonify({"message": "If the email exists, a reset link has been sent"}), 200

@app.route("/auth/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")
    
    if not token or not new_password:
        return jsonify({"error": "Token and new password required"}), 400
    
    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    reset_token = auth_db.get_password_reset_token(token)
    if not reset_token:
        return jsonify({"error": "Invalid or expired token"}), 400
    
    auth_db.update_password(reset_token['user_id'], new_password)
    auth_db.mark_token_used(token)
    
    return jsonify({"message": "Password reset successfully"}), 200

@app.route("/subscriptions/plans", methods=["GET"])
def get_subscription_plans():
    plans = [
        {"id": "free", "name": "Free", "price": 0, "duration_days": 365, "features": ["10 analyses per day", "Basic support"]},
        {"id": "pro", "name": "Pro", "price": 9.99, "duration_days": 30, "features": ["Unlimited analyses", "Priority support", "Advanced models"]},
        {"id": "enterprise", "name": "Enterprise", "price": 49.99, "duration_days": 30, "features": ["Unlimited analyses", "24/7 support", "Custom models", "API access"]}
    ]
    return jsonify({"plans": plans}), 200

@app.route("/subscriptions/subscribe", methods=["POST"])
@require_auth
def subscribe():
    data = request.get_json()
    plan_type = data.get("plan_type")
    
    if not plan_type:
        return jsonify({"error": "Plan type required"}), 400
    
    plan_durations = {"free": 365, "pro": 30, "enterprise": 30}
    duration = plan_durations.get(plan_type, 30)
    
    user = request.current_user
    subscription_id = auth_db.create_subscription(user['id'], plan_type, duration)
    subscription = auth_db.get_user_subscription(user['id'])
    
    mail_service.send_subscription_confirmation(user['email'], plan_type, subscription['end_date'])
    
    return jsonify({
        "message": "Subscription created successfully",
        "subscription": subscription
    }), 201

@app.route("/subscriptions/cancel", methods=["POST"])
@require_auth
def cancel_subscription():
    user = request.current_user
    subscription = auth_db.get_user_subscription(user['id'])
    
    if not subscription:
        return jsonify({"error": "No active subscription"}), 404
    
    auth_db.update_subscription_status(subscription['id'], 'canceled')
    
    return jsonify({"message": "Subscription canceled"}), 200

@app.route("/legal/terms", methods=["GET"])
def get_terms():
    terms = {
        "title": "Terms of Service",
        "last_updated": "2026-01-09",
        "content": "By using CodeGen Detector, you agree to these terms..."
    }
    return jsonify(terms), 200

@app.route("/legal/privacy", methods=["GET"])
def get_privacy():
    privacy = {
        "title": "Privacy Policy",
        "last_updated": "2026-01-09",
        "content": "We respect your privacy and are committed to protecting your personal data..."
    }
    return jsonify(privacy), 200



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
