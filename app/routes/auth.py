
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.user import create_user, get_user_by_email, get_user_by_id
from app.models.session import create_session, invalidate_session

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if get_user_by_email(email):
        return jsonify({"error": "User already exists"}), 409

    password_hash = generate_password_hash(password)
    user_id = create_user(email, password_hash)
    session_id = create_session(user_id)
    print(session_id)

    return jsonify({"session_id": session_id, "user_id": user_id})

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    session_id = create_session(str(user["_id"]))
    return jsonify({"session_id": session_id, "user_id": str(user["_id"])})

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        return jsonify({"error": "No session ID provided"}), 400

    invalidate_session(session_id)
    return jsonify({"message": "Logged out successfully"})

@auth_bp.route("/oauth/google", methods=["POST"])
def google_oauth():
    # Placeholder for now
    return jsonify({"message": "Google OAuth to be implemented"}), 501
