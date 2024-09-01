import bcrypt
from pymongo import MongoClient

# Conexión Base de datos
client = MongoClient('mongodb://localhost:27017/')
db = client['task_manager']
users_collection = db['users']

# Registra usuario
def create_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({'username': username, 'password': hashed_password})

# Verificar usuario
def authenticate_user(username, password):
    user = users_collection.find_one({'username': username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return True
    return False
