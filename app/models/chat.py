from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.database import mongo

from app.database import mongo
from app.database import get_mongo_db

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/overview", methods=["POST"])
def chat_overview():
    db = get_mongo_db()
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    # Don't convert to ObjectId, because participants are strings
    conversations = db.conversations.find({"participants": user_id})
    overview = []

    for convo in conversations:
        convo_id = convo["_id"]
        participants = convo["participants"]

        other_user_id = next(pid for pid in participants if pid != user_id)
        other_user = db.users.find_one({"_id": ObjectId(other_user_id)})

        # Get latest message
        last_msg_cursor = db.messages.find({"conversation_id": convo_id}).sort("timestamp", -1).limit(1)
        last_msg = list(last_msg_cursor)
        last_msg = last_msg[0] if last_msg else None

        overview.append({
            "conversation_id": str(convo_id),
            "name": other_user["profile"]["name"],
            "photo_url": other_user["profile"].get("photo_url", ""),
            "last_message": last_msg["content"] if last_msg else "",
            "timestamp": last_msg["timestamp"].isoformat() if last_msg else ""
        })

    overview.sort(key=lambda x: x["timestamp"], reverse=True)

    return jsonify(overview)
