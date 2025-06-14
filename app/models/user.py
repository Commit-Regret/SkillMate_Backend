# app/models/user.py

from bson import ObjectId
from datetime import datetime
from app.database import get_mongo_db
from app.database import db


# print(db)

def create_user(email, password_hash, oauth_provider=None):
    db = get_mongo_db()
    user = {
        "email": email,
        "password": password_hash,
        "oauth_provider": oauth_provider,
        "profile": {
            "name": "",
            "year": "",
            "techstack": []
        },
        "created_at": datetime.utcnow()
    }
    result = db.users.insert_one(user)
    return str(result.inserted_id)



def get_user_by_email(email):
    db = get_mongo_db()
    return db.users.find_one({"email": email})

def get_user_by_id(user_id):
    db = get_mongo_db()
    return db.users.find_one({"_id": ObjectId(user_id)})

def update_user_profile(user_id, name, year, techstack):
    db = get_mongo_db()
    result = db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "profile.name": name,
                "profile.year": year,
                "profile.techstack": techstack
            }
        }
    )
    return result.modified_count > 0

def get_user_profile(user_id):
    db = get_mongo_db()
    user = db.users.find_one(
        {"_id": ObjectId(user_id)},
        {"profile": 1, "_id": 0}
    )
    return user.get("profile") if user else None
