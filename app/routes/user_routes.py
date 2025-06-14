# app/routes/user_routes.py

import os
import uuid
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

user_routes = Blueprint("user_routes", __name__)

# Initialize DBs
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
users_col = db["users"]

model = SentenceTransformer("all-MiniLM-L6-v2")

qdrant = QdrantClient(host="localhost", port=6333)
collection_name = "skillmate_users"

STATIC_DIR = "static/photos"
os.makedirs(STATIC_DIR, exist_ok=True)


@user_routes.route("/create_user", methods=["POST"])
def create_user():
    try:
        name = request.form["name"]
        year = request.form["year"]
        techstack = request.form.getlist("techstack")  # frontend must send as array
        photo = request.files["photo"]

        # Save photo
        ext = os.path.splitext(photo.filename)[1]
        new_filename = f"{uuid.uuid4()}{ext}"
        photo_path = os.path.join(STATIC_DIR, secure_filename(new_filename))
        photo.save(photo_path)
        photo_url = f"/static/photos/{new_filename}"

        # Save to Mongo
        profile = {
            "name": name,
            "year": year,
            "techstack": techstack,
            "photo_url": photo_url,
        }

        result = users_col.insert_one({"profile": profile})
        user_id = result.inserted_id

        # Embed text
        embed_text = f"{name} {year} {' '.join(techstack)}"
        vector = model.encode(embed_text).tolist()

        # Insert to Qdrant
        response = qdrant.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=str(user_id),
                    vector=vector,
                    payload={"user_id": str(user_id)}
                )
            ]
        )

        assert response.status == "ok", f"Qdrant insert failed: {response}"

        return jsonify({"message": "User created successfully", "id": str(user_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
