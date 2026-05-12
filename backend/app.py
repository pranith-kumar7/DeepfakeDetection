from datetime import datetime
import os
import tempfile

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash

from detection import detect_deepfake
from video_detection import predict_video

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "deepfake_detection")

mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = mongo_client[MONGO_DB_NAME]
users_collection = db["users"]

try:
    users_collection.create_index("email", unique=True)
except PyMongoError:
    pass


def get_db_error_message(error):
    return {
        "error": "MongoDB connection failed. Make sure MongoDB is running and MONGO_URI is correct.",
        "details": str(error),
    }


def serialize_user(user):
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "created_at": user.get("created_at"),
    }


def normalize_prediction_response(result):
    response = dict(result)
    response["result"] = str(response["result"]).upper()

    fake_score = response.get("fake_score")
    real_score = response.get("real_score")
    raw_probability = response.get("raw_probability")

    if fake_score is None or real_score is None:
        if raw_probability is not None:
            raw_score = float(raw_probability) * 100
            if response["result"] == "REAL":
                real_score = raw_score
                fake_score = 100 - raw_score
            else:
                fake_score = raw_score
                real_score = 100 - raw_score
        else:
            confidence = float(response.get("confidence", 0))
            if response["result"] == "REAL":
                real_score = confidence
                fake_score = 100 - confidence
            else:
                fake_score = confidence
                real_score = 100 - confidence

    response["fake_score"] = round(float(fake_score), 2)
    response["real_score"] = round(float(real_score), 2)
    response["confidence"] = round(max(response["fake_score"], response["real_score"]), 2)
    return response


@app.get("/health")
def health():
    try:
        mongo_client.admin.command("ping")
        db_status = "connected"
    except PyMongoError:
        db_status = "disconnected"

    return jsonify({"status": "ok", "database": db_status})


@app.post("/auth/signup")
def signup():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long."}), 400

    try:
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return jsonify({"error": "An account with this email already exists."}), 409

        user = {
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "created_at": datetime.utcnow().isoformat(),
        }
        insert_result = users_collection.insert_one(user)
        user["_id"] = insert_result.inserted_id

        return jsonify({
            "message": "Account created successfully.",
            "user": serialize_user(user),
        }), 201
    except PyMongoError as error:
        return jsonify(get_db_error_message(error)), 500


@app.post("/auth/signin")
def signin():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    try:
        user = users_collection.find_one({"email": email})
    except PyMongoError as error:
        return jsonify(get_db_error_message(error)), 500

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    return jsonify({
        "message": "Signed in successfully.",
        "user": serialize_user(user),
    })


@app.route("/predict", methods=["POST"])
def predict_image():
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        result = detect_deepfake(file)
        if "error" in result:
            return jsonify(result), 500

        return jsonify(normalize_prediction_response(result))
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/predict-video", methods=["POST"])
def predict_video_route():
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No video uploaded"}), 400

    video_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
            file.save(temp.name)
            video_path = temp.name

        result = predict_video(video_path)
        if "error" in result:
            return jsonify(result), 500

        response = normalize_prediction_response(result)
        response["frames_processed"] = response.get("frames_analyzed", 0)
        return jsonify(response)
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
