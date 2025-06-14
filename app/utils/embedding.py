from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.database import get_mongo_db
from sentence_transformers import SentenceTransformer

qdrant = QdrantClient("localhost", port=6333)  # Modify as needed
model = SentenceTransformer("all-MiniLM-L6-v2")
COLLECTION = "skillmate_users"

db = get_mongo_db()

def get_similar_users(user_id, top_k=30):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user or "embedding" not in user:
        raise Exception("Embedding not found for user")

    embedding = user["embedding"]

    hits = qdrant.search(
        collection_name=COLLECTION,
        query_vector=embedding,
        limit=top_k,
        with_payload=True
    )
    return [hit.payload["user_id"] for hit in hits if hit.payload["user_id"] != user_id]
