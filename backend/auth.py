from flask import Blueprint, request, jsonify, make_response
from database import users_col
from utils.jwt_utils import generate_token
import bcrypt
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

def _build_cors_preflight_response():
    return make_response(), 200

# ------------------------
# REGISTER
# ------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    data = request.json

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check if username already exists
    if users_col.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 409

    # Hash password
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    user = {
        "username": username,
        "password_hash": password_hash,
        "created_at": datetime.utcnow()
    }

    result = users_col.insert_one(user)

    return jsonify({
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }), 201


# ------------------------
# LOGIN
# ------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    data = request.json

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = users_col.find_one({"username": username})

    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"]):
        return jsonify({"error": "Invalid username or password"}), 401

    token = generate_token(user["_id"])

    return jsonify({
        "message": "Login successful",
        "token": token
    }), 200
