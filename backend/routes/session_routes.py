from flask import Blueprint, request, jsonify, make_response
from utils.jwt_utils import decode_token
from sessions.session_manager import (
    get_active_session,
    create_new_session,
    reset_session
)

session_bp = Blueprint("session", __name__, url_prefix="/session")

# Simple OPTIONS handler
def _build_cors_preflight_response():
    return make_response(), 200

# -------------------------------------------------
# START SESSION
# -------------------------------------------------
@session_bp.route("/start", methods=["POST", "OPTIONS"])
def start_session():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    
    # Verify JWT manually
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Authorization header missing"}), 401
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get("user_id")
    
    # Check if active session exists
    active_session = get_active_session(user_id)
    
    if active_session:
        session_id = active_session.get("session_id")
    else:
        # Create new session
        _, session_id = create_new_session(user_id)

    return jsonify({"session_id": session_id}), 200


# -------------------------------------------------
# RESET SESSION
# -------------------------------------------------
@session_bp.route("/reset", methods=["POST", "OPTIONS"])
def reset_user_session():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    
    # Verify JWT manually
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Authorization header missing"}), 401
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get("user_id")
    
    success = reset_session(user_id)

    if not success:
        return jsonify({"message": "No active session to reset"}), 200

    return jsonify({"message": "Session reset successfully"}), 200