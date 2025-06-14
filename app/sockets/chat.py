
from flask_socketio import emit, join_room
from flask import request, jsonify
from bson import ObjectId
from datetime import datetime
from app.database import mongo
from app.database import get_mongo_db

def register_chat_events(socketio):
    print("✅ register_chat_events CALLED")
    db = get_mongo_db()
    @socketio.on("join_chat")
    def on_join_chat(data):
        print("hello")
        user_id = data["user_id"]
        name = data["other_user_id"]
        print("hello2")
        other_user = mongo.db.users.find_one({"profile.name": name})
        if not other_user:
            emit("error", {"error": "User not found"})
            return
        print("hello3")
        other_user_id = str(other_user["_id"])

        # Ensure consistent participant order
        participants = sorted([user_id, other_user_id])

        # Search for existing conversation
        conversation = mongo.db.conversations.find_one({
            "participants": participants
        })

        # Create one if it doesn't exist
        if not conversation:
            conversation_id = mongo.db.conversations.insert_one({
                "participants": participants
            }).inserted_id
        else:
            conversation_id = conversation["_id"]

        room = str(conversation_id)
        join_room(room)
        emit("joined_chat", {"conversation_id": room})

    @socketio.on("send_message")
    def handle_send_message(data):
        conversation_id = data["conversation_id"]
        sender_id = data["sender_id"]
        content = data["content"]

        message_doc = {
            "conversation_id": ObjectId(conversation_id),
            "sender_id": sender_id,
            "content": content,
            "timestamp": datetime.utcnow()
        }

        mongo.db.messages.insert_one(message_doc)

        emit("receive_message", {
            "sender_id": sender_id,
            "content": content,
            "timestamp": message_doc["timestamp"].isoformat()
        }, room=conversation_id)

    @socketio.on("fetch_messages")
    def handle_fetch_messages(data):
        conversation_id = data["conversation_id"]
        messages = mongo.db.messages.find({
            "conversation_id": ObjectId(conversation_id)
        }).sort("timestamp", 1)

        messages_list = [{
            "sender_id": msg["sender_id"],
            "content": msg["content"],
            "timestamp": msg["timestamp"].isoformat()
        } for msg in messages]

        emit("chat_history", messages_list)
