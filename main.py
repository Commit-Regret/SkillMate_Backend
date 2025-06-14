import os
import time
from flask_socketio import SocketIO
from dotenv import load_dotenv
from app import create_app

load_dotenv()

print("[BOOT] Starting app...")
t1 = time.time()
app = create_app()
print(f"[BOOT] App created in {time.time() - t1:.2f}s")

print("[BOOT] Initializing SocketIO...")
t2 = time.time()
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet",  # Async server
    logger=True,
    engineio_logger=True
)
print(f"[BOOT] SocketIO initialized in {time.time() - t2:.2f}s")

print("[BOOT] Registering sockets...")
from app.sockets.recommender import register_recommender_events
from app.sockets.chat import register_chat_events
register_recommender_events(socketio)
register_chat_events(socketio)
print("[BOOT] Sockets registered.")

@app.route("/running", methods=["GET", "POST"])
def running():
    return {"message": "Server is up and running"}, 200
    
print("[BOOT] Starting server...")
socketio.run(app, host="127.0.1.0", port=int(os.getenv("PORT", 5000)), debug=True)
