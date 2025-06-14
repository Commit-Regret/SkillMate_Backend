
from uuid import uuid4
from datetime import datetime, timedelta
from app.database import get_mongo_db



def create_session(user_id):
    db = get_mongo_db()
    session_id = str(uuid4())
    now = datetime.utcnow()
    session = {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": now,
        "expires_at": now + timedelta(hours=24)
    }
    db.sessions.insert_one(session)
    return session_id

def invalidate_session(session_id):
    db = get_mongo_db()
    db.sessions.delete_one({"session_id": session_id})
