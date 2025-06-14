from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer
from bson import ObjectId
from app.database import get_mongo_db

# Initialize Qdrant & embedding model
qdrant = QdrantClient("localhost", port=6333)  # Change if running remotely
model = SentenceTransformer("all-MiniLM-L6-v2")

COLLECTION = "skillmate_users"



def generate_embedding_from_user(user_profile):
    """
    Generates a 384D embedding from user profile.

    Args:
        user_profile (dict): Should contain 'year' and 'techstack'

    Returns:
        list[float]: The 384D embedding
    """
    year = str(user_profile.get("year", ""))
    techstack = user_profile.get("techstack", [])
    
    if not techstack:
        raise ValueError("Techstack missing from profile")

    text = f"{year} {' '.join(techstack)}"
    embedding = model.encode(text)

    return embedding.tolist()  # Return as list for JSON/db compatibility


def get_similar_users(user_id, top_k=30):
    """
    Searches Qdrant for users with similar embeddings.

    Args:
        user_id (str): MongoDB ObjectId of the user
        top_k (int): Number of similar users to return

    Returns:
        List of similar user_ids (excluding the original one)
    """
    db = get_mongo_db()
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

    return [hit.payload["user_id"] for hit in hits if hit.payload["user_id"] != str(user_id)]

