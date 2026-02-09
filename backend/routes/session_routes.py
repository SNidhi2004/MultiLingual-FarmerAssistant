from flask import Blueprint, jsonify
from utils.jwt_utils import jwt_required
from flask import request

from sessions.session_manager import (
    get_active_session,
    create_or_get_session,
    reset_session
)

session_bp = Blueprint("session", __name__, url_prefix="/session")


# -------------------------------------------------
# START / GET SESSION
# -------------------------------------------------
@session_bp.route("/start", methods=["POST"])
@jwt_required
def start_session():
    """
    Returns the active session for the user.
    If none exists, creates one.    
    """
    session_id = create_or_get_session(request.user_id)

    return jsonify({
        "session_id": str(session_id)
    }), 200


# -------------------------------------------------
# RESET SESSION (CLEAR IMAGES & CONTEXT)
# -------------------------------------------------
@session_bp.route("/reset", methods=["POST"])
@jwt_required
def reset_user_session():
    """
    Ends current session and deletes all related images.
    A new session will be created automatically on next image upload.
    """
    success = reset_session(request.user_id)

    if not success:
        return jsonify({"message": "No active session to reset"}), 200

    return jsonify({"message": "Session reset successfully"}), 200
