from flask_socketio import emit, join_room, leave_room
from flask import request

# Define your namespace or leave it default
NAMESPACE = "/chat"

# Dictionary to store messages temporarily (you'll likely store this in DB later)
chat_history = {}

def register_chat_events(socketio):
    @socketio.on("join_room", namespace=NAMESPACE)
    def handle_join(data):
        room = data["room"]
        join_room(room)
        emit("user_joined", {"room": room, "user": request.sid}, room=room)

    @socketio.on("leave_room", namespace=NAMESPACE)
    def handle_leave(data):
        room = data["room"]
        leave_room(room)
        emit("user_left", {"room": room, "user": request.sid}, room=room)

    @socketio.on("send_message", namespace=NAMESPACE)
    def handle_send_message(data):
        room = data["room"]
        message = data["message"]
        sender = data.get("sender", "anonymous")

        # Save to in-memory chat history (replace with DB later)
        if room not in chat_history:
            chat_history[room] = []
        chat_history[room].append({"sender": sender, "message": message})

        emit("receive_message", {
            "room": room,
            "sender": sender,
            "message": message
        }, room=room)

    @socketio.on("typing", namespace=NAMESPACE)
    def handle_typing(data):
        room = data["room"]
        user = data.get("user", "anonymous")
        emit("user_typing", {"room": room, "user": user}, room=room)
