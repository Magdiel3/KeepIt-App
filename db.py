from datetime import datetime
import os

from bson import ObjectId
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash

from user import User

import logging

log = logging.getLogger()

mongodb_password = os.getenv("MONGODB_PASSWORD")

client = MongoClient(f"mongodb+srv://magdiel3:{mongodb_password}@keepit.jca02.mongodb.net/test?retryWrites=true&w=majority")

boxes_db = client.get_database("BoxesDB")
users_collection = boxes_db.get_collection("users")
boxes_collection = boxes_db.get_collection("boxes")

# User adition
def save_user(username, email, password, box_name):
    password_hash = generate_password_hash(password)

    if username and email and password and box_name:
        box_used = boxes_collection.find_one({"_id": box_name})
        if not box_used:
            try:
                # save_box(box_name)
                users_collection.insert_one({'_id': username, 'email': email, 'password': password_hash, 'box_name': box_name})
                return get_user(username)
            except:
                print("User insertion failed")
    else:
        print("User creation without valid arguments") 
    return None

def get_user(username):
    user_data = users_collection.find_one({'_id': username})
    return User(user_data['_id'], user_data['email'], user_data['password'], user_data['box_name']) if user_data else None

# Box adition
def save_box(box_name):
    boxes_collection.insert_one({'_id': box_name})


def get_box(box_name):
    box_data = boxes_collection.find_one({'_id': box_name})
    return box_data if box_data else None

def get_user_box(username):
    user_data = get_user(username)
    box_name = user_data.get("box_name", None)
    box = None
    if box_id:
        box = boxes_collection.find_one({'_id': box_name})
    return box

# Validate Box
def is_box_owner(username,box_name):
    return users_collection.find_one({"_id":username}).get('box_name','') == box_name

if __name__ == "__main__":
    try:
        save_user("test2","test@test.com","test","TestBox")
    except:
        print("Already existed")

    try:
        save_box("TestBox")
    except:
        print(get_box("TestBox"))