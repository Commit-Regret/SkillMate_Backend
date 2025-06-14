from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from .database import init_mongo
from .routes.auth import auth_bp
# from .routes.genai import genai_bp
from .routes.profile import profile_bp
from .routes.auth import auth_bp
from app.routes.user_routes import user_routes





# def create_app():
#     # Load environment variables
#     load_dotenv()

#     app = Flask(__name__)

#     # Config
#     app.config["MONGO_URI"] = os.getenv("MONGO_URI")
#     app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecret")

#     # CORS for Netlify frontend (wildcard for dev)
#     CORS(app, supports_credentials=True)

#     # Initialize MongoDB
#     init_mongo(app)

#     # Register blueprints (routes)
#     app.register_blueprint(auth_bp, url_prefix="/auth")
#     # app.register_blueprint(genai_bp, url_prefix="/genai")
#     app.register_blueprint(profile_bp, url_prefix="/profile")
#     # app.register_blueprint(auth_bp, url_prefix="/auth")
#     app.register_blueprint(user_routes)

#     return app

import time

def create_app():
    load_dotenv()
    print(f"[{time.time()}] Loading Flask app...")

    app = Flask(__name__)
    # app.config["DEBUG"] = True
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecret")

    print(f"[{time.time()}] Setting up CORS...")
    CORS(app, supports_credentials=True)

    print(f"[{time.time()}] Initializing Mongo...")
    init_mongo(app)  # <--- likely slow

    print(f"[{time.time()}] Registering Blueprints...")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(user_routes)

    print(f"[{time.time()}] App ready.")
    return app
