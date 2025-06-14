from sentence_transformers import SentenceTransformer

# Load once globally
model = SentenceTransformer("all-MiniLM-L6-v2")

def encode_user_profile(profile):
    """
    Convert user profile into a single string embedding.
    Profile: dict with name, year, techstack
    """
    text = f"{profile.get('name', '')}, {profile.get('year', '')}, {' '.join(profile.get('techstack', []))}"
    return model.encode(text)
