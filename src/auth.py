import bcrypt
import json
import os
from logger import log_info, log_warning, log_error

USERS_FILE = 'data/users.json'

# Función para leer archivo JSON
def _read_users():
    try:
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    except Exception as e:
        log_error(f'Error al leer el archivo de usuarios: {e}')
        return []

# Función para escribir en archivo JSON
def _write_users(users):
    try:
        with open(USERS_FILE, 'w') as file:
            json.dump(users, file, indent=4)
    except Exception as e:
        log_error(f'Error al escribir en el archivo de usuarios: {e}')

# Función para crear usuario, verifica que no se cree un nombre de usuario ya registrado
def create_user(username, password):
    try:
        users = _read_users()  # Leer usuarios desde el archivo JSON

        # Verificar si el usuario ya existe
        if any(user['username'] == username for user in users):
            print("El nombre de usuario ya está registrado.")
            return

        # Hash del password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Agregar nuevo usuario a la lista
        users.append({
            'username': username,
            'password': hashed_password.decode('utf-8')  # Decodificar el hashed_password para almacenar en JSON
        })

        _write_users(users)  # Escribir usuarios en el archivo JSON
        print("Usuario registrado exitosamente.")
        log_info(f'Usuario registrado: {username}')
    except Exception as e:
        log_error(f'Error al registrar usuario: {e}')
        print("Ocurrió un error al registrar el usuario.")

# Función verificar datos de usuario iniciando sesion
def authenticate_user(username, password):
    try:
        users = _read_users()  # Leer usuarios desde el archivo JSON

        # Buscar el usuario en la lista
        user = next((u for u in users if u['username'] == username), None)
        
        if user:
            # Verificar la contraseña
            hashed_password = user['password'].encode('utf-8')  # Convertir el hashed_password a bytes
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
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