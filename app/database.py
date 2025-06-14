from flask_pymongo import PyMongo

mongo = PyMongo()
db = None  # Global variable to hold the DB
def init_mongo(app):
    global db
    mongo.init_app(app)
    db = mongo.db  # assign the db object

def get_mongo_db():
    global db
    if db is None:
        raise RuntimeError("MongoDB not initialized. Call init_mongo(app) first.")
    return db

