import os
import uuid
import random
import shutil
import numpy as np
import matplotlib.pyplot as plt
from bson import ObjectId
from dotenv import load_dotenv
from faker import Faker
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from qdrant_client.http.exceptions import UnexpectedResponse
import hdbscan
import umap
from datetime import datetime
from werkzeug.security import generate_password_hash
# -----------------------------
# 📦 INIT: Connections
# -----------------------------
load_dotenv()
fake = Faker()
model = SentenceTransformer("all-MiniLM-L6-v2")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
users_col = db["users"]

qdrant = QdrantClient(host="localhost", port=6333)
collection_name = "skillmate_users"

# -----------------------------
# 🔄 Refresh Qdrant collection
# -----------------------------
try:
    if qdrant.collection_exists(collection_name=collection_name):
        qdrant.delete_collection(collection_name=collection_name)
        print(f"[INFO] Deleted old collection '{collection_name}'")
except UnexpectedResponse as e:
    print(f"[WARNING] Couldn't delete collection: {e}")

qdrant.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
print(f"[INFO] Qdrant collection '{collection_name}' created.")

# -----------------------------
# 🔨 Generate dummy users
# -----------------------------
ASSET_PHOTO_DIR = "../assets/photos"
STATIC_PHOTO_DIR = "../static/photos"
os.makedirs(STATIC_PHOTO_DIR, exist_ok=True)

dummy_photos = [f for f in os.listdir(ASSET_PHOTO_DIR) if f.endswith(('.jpg', '.png'))]

# techstacks = [
#     ["Python", "Flask", "MongoDB"], ["React", "Node.js", "Express"],
#     ["Machine Learning", "PyTorch", "Pandas"], ["Data Science", "SQL", "PowerBI"],
#     ["Android", "Java", "Firebase"], ["iOS", "Swift", "Xcode"],
#     ["DevOps", "Docker", "Kubernetes"], ["Cybersecurity", "Linux", "Wireshark"],
#     ["Web Dev", "HTML", "CSS", "JavaScript"], ["Game Dev", "Unity", "C#", "Blender"],
#     ["Blockchain", "Solidity", "Ethereum"], ["Embedded Systems", "C", "Arduino"],
#     ["Computer Vision", "OpenCV", "YOLOv9"], ["NLP", "Transformers", "HuggingFace"],
#     ["Cloud", "AWS", "GCP", "Azure"], ["Big Data", "Hadoop", "Spark"],
#     ["Automation", "Selenium", "Python"], ["AI", "TensorFlow", "Scikit-learn"],
#     ["Product", "PNC", "Figma"], ["UI/UX", "Figma", "Adobe XD"],
#     ["Robotics", "ROS", "Gazebo", "C++"], ["VR/AR", "Three.js", "A-Frame"],
#     ["Security", "Burp Suite", "Metasploit"], ["Quant", "Python", "NumPy", "Finance"],
#     ["Bioinformatics", "Biopython", "R"], ["Hardware", "VHDL", "Verilog"],
#     ["Systems", "OSDev", "Rust", "C"], ["Analytics", "Excel", "Looker", "PowerBI"],
#     ["SaaS", "Stripe API", "Next.js", "Prisma"], ["DevRel", "Content", "GitHub", "Docs"],
#     ["No-Code", "Bubble", "Airtable"]
# ]

techstacks = [
    ["Python", "Flask", "MongoDB"],
    ["React", "Node.js", "Express"],
    ["Machine Learning", "PyTorch", "Pandas"],
    ["Data Science", "SQL", "PowerBI"],
    ["Android", "Java", "Firebase"],
    ["iOS", "Swift", "Xcode"],
    ["DevOps", "Docker", "Kubernetes"],
    ["Cybersecurity", "Linux", "Wireshark"]
]


def generate_user():
    chosen_photo = random.choice(dummy_photos)
    new_filename = f"{uuid.uuid4()}.jpg"
    shutil.copy(os.path.join(ASSET_PHOTO_DIR, chosen_photo), os.path.join(STATIC_PHOTO_DIR, new_filename))
    
    profile = {
        "name": fake.first_name(),
        "year": random.choice(["1st", "2nd", "3rd", "4th"]),
        "techstack": random.choice(techstacks),
        "photo_url": f"/static/photos/{new_filename}"
    }

    user = {
        "email": fake.email(),
        "password": generate_password_hash("password123"),  # You can randomize if needed
        "oauth_provider": None,
        "profile": profile,
        "created_at": datetime.now()
    }

    return user

users = [generate_user() for _ in range(1000)]

vectors = []
user_ids = []

for user in users:
    result = users_col.insert_one(user)
    uid = result.inserted_id
    profile = user["profile"]

    embed_text = f"{profile['year']} {' '.join(profile['techstack'])}"
    vec = model.encode(embed_text)

    vectors.append(vec)
    user_ids.append(uid)

    qdrant_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uid)))  # deterministic UUID

    try:
        qdrant.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=qdrant_id,
                    vector=vec,
                    payload={
                        "user_id": str(uid),
                        "name": profile["name"],
                        "year": profile["year"],
                        "techstack": profile["techstack"],
                        "photo_url": profile["photo_url"]
                    }
                )
            ]
        )
        print(f"[OK] Inserted user {uid} into Qdrant")
    except Exception as e:
        print(f"[ERROR] Failed to insert user {uid}: {e}")


# -----------------------------
# 📊 Improved Clustering + UMAP
# -----------------------------
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from sklearn.decomposition import PCA

print("Running PCA for denoising...")
pca = PCA(n_components=50)
vectors_np = np.array(vectors)

vectors_pca = pca.fit_transform(vectors_np)

print("Running HDBSCAN clustering...")
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=10,
    min_samples=5,
    cluster_selection_method='eom',
    prediction_data=True
)
clusters = clusterer.fit_predict(vectors_pca)

print(f"[INFO] Found {len(set(clusters)) - (1 if -1 in clusters else 0)} clusters")

for uid, cluster_id in zip(user_ids, clusters):
    users_col.update_one({"_id": uid}, {"$set": {"cluster_id": int(cluster_id)}})

# -----------------------------
# 📉 Improved UMAP
# -----------------------------
print("Running UMAP for 2D projection...")
umap_embedder = umap.UMAP(
    n_neighbors=15,
    min_dist=0.3,
    metric='cosine',
    random_state=42
)
umap_proj = umap_embedder.fit_transform(vectors_pca)

# -----------------------------
# 📈 Plotting
# -----------------------------
print("Plotting results...")
plt.figure(figsize=(10, 6))
plt.scatter(
    umap_proj[:, 0],
    umap_proj[:, 1],
    c=clusters,
    cmap='Spectral',
    s=50
)
plt.title("Improved HDBSCAN Clustering of SkillMate Users")
plt.xlabel("UMAP 1")
plt.ylabel("UMAP 2")
plt.colorbar(label="Cluster ID")
plt.grid(True)
plt.tight_layout()
plt.show()
