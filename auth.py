"""
JWT Authentication helper functions and access control decorators.
"""

import os
import datetime
import jwt
from functools import wraps
from flask import request, jsonify

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "ollama-chatbot-super-secret-jwt-key-2026")


def generate_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24),
        "iat": datetime.datetime.now(datetime.timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        if not token:
            token = request.cookies.get("jwt_token")

        if not token:
            return jsonify({"status": "error", "message": "Authentication token is missing"}), 401

        decoded = decode_token(token)
        if "error" in decoded:
            return jsonify({"status": "error", "message": decoded["error"]}), 401

        request.current_user = decoded
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        if not token:
            token = request.cookies.get("jwt_token")

        if not token:
            return jsonify({"status": "error", "message": "Authentication token is missing"}), 401

        decoded = decode_token(token)
        if "error" in decoded:
            return jsonify({"status": "error", "message": decoded["error"]}), 401

        if decoded.get("role") != "admin":
            return jsonify({"status": "error", "message": "Admin privileges required"}), 403

        request.current_user = decoded
        return f(*args, **kwargs)

    return decorated
