from datetime import datetime
import os

from bson import ObjectId
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash

from user import User

mongodb_password = os.getenv("MONGODB_PASSWORD")

client = MongoClient(f"mongodb+srv://magdiel3:{mongodb_password}@keepit.jca02.mongodb.net/test?retryWrites=true&w=majority")

boxes_db = client.get_database("BoxesDB")
users_collection = boxes_db.get_collection("users")


def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id': username, 'email': email, 'password': password_hash})


def get_user(username):
    user_data = users_collection.find_one({'_id': username})
    return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None