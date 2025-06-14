from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.database import mongo

from app.database import mongo
from app.database import get_mongo_db

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/overview", methods=["POST"])
def chat_overview():
    db = get_mongo_db()
    print(db)
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    user_obj_id = ObjectId(user_id)

    # Find conversations where this user is a participant
    conversations = mongo.db.conversations.find({"participants": user_obj_id})
    print("conaofwj")
    print(conversations)
    overview = []

    print("hi")
    for convo in conversations:
        convo_id = convo["_id"]
        participants = convo["participants"]

        # Get the "other user"
        other_user_id = next(pid for pid in participants if pid != user_obj_id)
        other_user = mongo.db.users.find_one({"_id": other_user_id})

        # Get latest message
        last_msg = mongo.db.messages.find({"conversation_id": convo_id}).sort("timestamp", -1).limit(1)
        last_msg = list(last_msg)[0] if last_msg.count() > 0 else None

        overview.append({
            "conversation_id": str(convo_id),
            "name": other_user["profile"]["name"],
            "photo_url": other_user["profile"].get("photo_url", ""),
            "last_message": last_msg["content"] if last_msg else "",
            "timestamp": last_msg["timestamp"].isoformat() if last_msg else ""
        })
        print("bye")

    # Sort by latest timestamp descending
    overview.sort(key=lambda x: x["timestamp"], reverse=True)

    return jsonify(overview)
