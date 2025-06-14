# app/database.py

from flask_pymongo import PyMongo

mongo = PyMongo()

def init_mongo(app):
    mongo.init_app(app)

def get_mongo_db():
    return mongo.db
