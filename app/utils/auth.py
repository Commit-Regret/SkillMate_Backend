from bson import ObjectId
from datetime import datetime
from app.database import get_mongo_db



def validate_session(session_id):
    db = get_mongo_db()
    session = db.sessions.find_one({"session_id": session_id})
    if not session:
        return None
    if session.get("expires_at") < datetime.utcnow():
        return None
    return str(session["user_id"])
