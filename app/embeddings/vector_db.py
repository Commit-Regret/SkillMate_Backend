# app/embeddings/vector_db.py

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Distance, VectorParams, Filter, FieldCondition, MatchValue
from bson import ObjectId
import numpy as np

qdrant = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "skillmate_users"

def init_vector_collection(dim=384):  # 384 is dim for all-MiniLM-L6-v2
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
    )

def add_user_embedding(user_id, vector):
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(id=str(user_id), vector=vector, payload={"user_id": str(user_id)})
        ]
    )

def search_similar(user_id, vector, exclude_ids, limit=20):
    """
    Search top-N similar users (excluding already swiped)
    """
    filter_ = Filter(
        must_not=[
            FieldCondition(key="user_id", match=MatchValue(value=ex_id)) for ex_id in exclude_ids
        ]
    )

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=limit,
        query_filter=filter_
    )

    return [point.payload["user_id"] for point in results]
