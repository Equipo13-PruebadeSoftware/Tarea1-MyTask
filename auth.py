import bcrypt
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['task_manager']
users_collection = db['users']

def create_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({'username': username, 'password': hashed_password})

def authenticate_user(username, password):
    user = users_collection.find_one({'username': username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return True
    return False
