import jwt
from functools import wraps
from flask import request, jsonify
from config import JWT_SECRET


def generate_token(user_id):
    """
    Create a JWT token containing the user_id.
    """
    payload = {
        "user_id": str(user_id)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


def decode_token(token):
    """
    Decode JWT token and return payload.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_required(f):
    """
    Flask decorator to protect routes.
    Expects JWT in Authorization header as:
    Authorization: Bearer <token>
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401

        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({"error": "Invalid Authorization header"}), 401

        payload = decode_token(token)

        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Attach user_id to request context
        request.user_id = payload["user_id"]

        return f(*args, **kwargs)

    return decorated
