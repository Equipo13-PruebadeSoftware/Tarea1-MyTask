import bcrypt
from pymongo import MongoClient
from logger import log_info, log_warning, log_error

# Conexión Base de datos
client = MongoClient('mongodb://localhost:27017/')
db = client['task_manager']
users_collection = db['users']

# Función para crear usuario, verifica que no se cree un nombre de usuario ya registrado
def create_user(username, password):
    try:
        # Verificar si el usuario ya existe
        if users_collection.find_one({'username': username}):
            print("El nombre de usuario ya está registrado.")
            log_warning(f'Intento de registrar un nombre de usuario ya existente: {username}')
            return

        # Hash del password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insertar nuevo usuario en la colección
        users_collection.insert_one({'username': username, 'password': hashed_password})
        print("Usuario registrado exitosamente.")
        log_info(f'Usuario registrado: {username}')
    except Exception as e:
        log_error(f'Error al registrar usuario: {e}')
        print("Ocurrió un error al registrar el usuario.")

# Función verificar datos de usuario iniciando sesión
def authenticate_user(username, password):
    try:
        # Buscar el usuario en la colección
        user = users_collection.find_one({'username': username})
        
        if user:
            # Verificar la contraseña
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                log_info(f'Autenticación exitosa para el usuario: {username}')
                return True
            else:
                log_info(f'Contraseña incorrecta para el usuario: {username}')
        else:
            log_info(f'Usuario no encontrado: {username}')
        
        return False
    except Exception as e:
        log_error(f'Error al autenticar el usuario: {e}')
        print("Ocurrió un error al autenticar el usuario.")
        return False

    
