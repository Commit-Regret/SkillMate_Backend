
from flask import Blueprint, request, jsonify
from app.models.user import update_user_profile, get_user_profile
from app.utils.auth import validate_session

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/update", methods=["POST"])
def update_profile():
    session_id = request.headers.get("X-Session-ID")
    user_id = validate_session(session_id)
    if not user_id:
        return jsonify({"error": "Invalid or expired session"}), 401

    data = request.get_json()
    name = data.get("name")
    year = data.get("year")
    techstack = data.get("techstack", [])

    if not name or not year:
        return jsonify({"error": "Name and year are required"}), 400

    success = update_user_profile(user_id, name, year, techstack)
    updated_user = db.users.find_one({"_id": ObjectId(user_id)})
    embedding = generate_embedding_from_user(updated_user)
    
    # Push to Qdrant
    qdrant_client.upsert(
        collection_name="users",
        points=[{
            "id": user_id,
            "vector": embedding,
            "payload": {"user_id": user_id}
        }]
    )
    if success:
        return jsonify({"message": "Profile updated successfully"}), 200
    return jsonify({"error": "Update failed"}), 500

@profile_bp.route("/me", methods=["GET"])
def get_profile():
    session_id = request.headers.get("X-Session-ID")
    user_id = validate_session(session_id)
    if not user_id:
        return jsonify({"error": "Invalid or expired session"}), 401

    profile = get_user_profile(user_id)
    if profile:
        return jsonify(profile)
    return jsonify({"error": "Profile not found"}), 404
