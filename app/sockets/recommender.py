import random
from flask import request
from flask_socketio import emit
from bson import ObjectId
from datetime import datetime

from app.database import get_mongo_db
from app.utils.auth import validate_session
from app.utils.embedding import get_similar_users
from app.embeddings.model import encode_user_profile
from app.embeddings.vector_db import search_similar


def register_recommender_events(socketio):
    db = get_mongo_db()

    @socketio.on("connect")
    def handle_connect():
        print("User connected to WebSocket.")

    @socketio.on("disconnect")
    def handle_disconnect():
        print("User disconnected from WebSocket.")

    @socketio.on("find_skillmate")
    def handle_find_skillmate(data):
        session_id = data.get("session_id")
        user_id = validate_session(session_id)
        if not user_id:
            emit("error", {"error": "Invalid session"})
            return

        user = db.users.find_one({"_id": ObjectId(user_id)})
        profile = user.get("profile")
        if not profile:
            emit("error", {"error": "Incomplete profile"})
            return

        # Step 1: Generate user vector
        vector = encode_user_profile(profile)

        # Step 2: Get already swiped users
        swiped = db.swipes.find({"swiper_id": ObjectId(user_id)})
        swiped_ids = [str(s["swipee_id"]) for s in swiped]

        # Step 3: Query Vector DB
        similar_user_ids = search_similar(user_id, vector, exclude_ids=swiped_ids, limit=20)

        # Step 4: Fetch similar users' profiles and assign random online image
        users = db.users.find({"_id": {"$in": [ObjectId(uid) for uid in similar_user_ids]}})
        response = []
        for u in users:
            # Use random Lorem Picsum image
            random_image_url = f"https://picsum.photos/seed/{random.randint(1, 9999)}/300/300"

            response.append({
                "user_id": str(u["_id"]),
                "profile": u.get("profile", {}) | {"photo_url": random_image_url}
            })

        # Step 5: Emit recommendations
        emit("recommendations", {"users": response})

    @socketio.on("swipe")
    def handle_swipe(data):
        session_id = data.get("session_id")
        target_user_id = data.get("target_user_id")
        liked = data.get("liked")

        user_id = validate_session(session_id)
        if not user_id:
            emit("error", {"error": "Invalid session"})
            return

        if not target_user_id or liked is None:
            emit("error", {"error": "Swipe data incomplete"})
            return

        db.swipes.insert_one({
            "swiper_id": ObjectId(user_id),
            "swipee_id": ObjectId(target_user_id),
            "liked": liked,
            "timestamp": datetime.utcnow()
        })

        # Check if mutual match
        mutual = db.swipes.find_one({
            "swiper_id": ObjectId(target_user_id),
            "swipee_id": ObjectId(user_id),
            "liked": True
        })

        if liked and mutual:
            print("Shaadi karlo")
            u1 = db.users.find_one({"_id": ObjectId(user_id)}, {"profile": 1})
            u2 = db.users.find_one({"_id": ObjectId(target_user_id)}, {"profile": 1})

            u1_profile = u1.get("profile", {}) | {"user_id": user_id}
            u2_profile = u2.get("profile", {}) | {"user_id": target_user_id}

            # Send match event to both
            emit("match", {"with": u2_profile}, to=request.sid)

            match_room = f"{min(user_id, target_user_id)}_{max(user_id, target_user_id)}"
            socketio.emit("match", {"with": u1_profile}, to=match_room)
