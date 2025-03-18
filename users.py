"""
Módulo de gestión de usuarios para el chatbot de TalentLand 2025.
Proporciona funciones para registrar, autenticar y gestionar usuarios.
"""

import os
import json
import hashlib
import secrets
from typing import Dict, Optional, Any, List
import time

# Ruta al archivo de usuarios
USERS_FILE = "users.json"

def hash_password(password: str, salt: Optional[str] = None) -> tuple:
    """
    Hashea una contraseña con un salt para almacenarla de forma segura.
    
    Args:
        password: La contraseña a hashear
        salt: Salt opcional, si no se proporciona se genera uno nuevo
        
    Returns:
        Tupla (hash, salt)
    """
    if not salt:
        salt = secrets.token_hex(16)  # Generar un salt aleatorio
    
    # Combinar la contraseña y el salt, y crear un hash SHA-256
    hash_obj = hashlib.sha256(f"{password}{salt}".encode())
    password_hash = hash_obj.hexdigest()
    
    return password_hash, salt

def load_users() -> Dict[str, Any]:
    """
    Carga la lista de usuarios desde el archivo JSON.
    
    Returns:
        Diccionario con los usuarios registrados
    """
    if not os.path.exists(USERS_FILE):
        # Si el archivo no existe, crear uno con usuarios por defecto
        default_users = {
            "admin": {
                "password_hash": None,
                "salt": None,
                "role": "admin",
                "created_at": time.time()
            },
            "usuario": {
                "password_hash": None,
                "salt": None,
                "role": "user",
                "created_at": time.time()
            }
        }
        
        # Establecer contraseñas hasheadas para los usuarios por defecto
        admin_hash, admin_salt = hash_password("talentland2025")
        default_users["admin"]["password_hash"] = admin_hash
        default_users["admin"]["salt"] = admin_salt
        
        user_hash, user_salt = hash_password("password123")
        default_users["usuario"]["password_hash"] = user_hash
        default_users["usuario"]["salt"] = user_salt
        
        # Guardar usuarios por defecto
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, indent=2)
        
        return default_users
    
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error al cargar usuarios: {e}")
        return {}

def save_users(users: Dict[str, Any]) -> None:
    """
    Guarda la lista de usuarios en el archivo JSON.
    
    Args:
        users: Diccionario con los usuarios a guardar
    """
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

def verify_password(username: str, password: str) -> bool:
    """
    Verifica si la contraseña proporcionada es correcta para el usuario dado.
    
    Args:
        username: Nombre de usuario
        password: Contraseña a verificar
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    users = load_users()
    
    if username not in users:
        return False
    
    user_data = users[username]
    stored_hash = user_data.get("password_hash")
    salt = user_data.get("salt")
    
    if not stored_hash or not salt:
        return False
    
    # Calcular el hash con la contraseña proporcionada y el salt almacenado
    calculated_hash, _ = hash_password(password, salt)
    
    # Comparar los hashes
    return calculated_hash == stored_hash

def register_user(username: str, password: str, role: str = "user") -> bool:
    """
    Registra un nuevo usuario en el sistema.
    
    Args:
        username: Nombre de usuario
        password: Contraseña
        role: Rol del usuario (por defecto, "user")
        
    Returns:
        True si el registro fue exitoso, False si el usuario ya existe
    """
    users = load_users()
    
    # Verificar si el usuario ya existe
    if username in users:
        return False
    
    # Hashear la contraseña
    password_hash, salt = hash_password(password)
    
    # Agregar el nuevo usuario
    users[username] = {
        "password_hash": password_hash,
        "salt": salt,
        "role": role,
        "created_at": time.time()
    }
    
    # Guardar los usuarios actualizados
    save_users(users)
    return True

def change_password(username: str, old_password: str, new_password: str) -> bool:
    """
    Cambia la contraseña de un usuario.
    
    Args:
        username: Nombre de usuario
        old_password: Contraseña actual
        new_password: Nueva contraseña
        
    Returns:
        True si el cambio fue exitoso, False si la contraseña actual es incorrecta
    """
    # Verificar la contraseña actual
    if not verify_password(username, old_password):
        return False
    
    users = load_users()
    
    # Hashear la nueva contraseña
    password_hash, salt = hash_password(new_password)
    
    # Actualizar el usuario
    users[username]["password_hash"] = password_hash
    users[username]["salt"] = salt
    
    # Guardar los usuarios actualizados
    save_users(users)
    return True

def get_user_data(username: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos de un usuario.
    
    Args:
        username: Nombre de usuario
        
    Returns:
        Diccionario con los datos del usuario, o None si no existe
    """
    users = load_users()
    return users.get(username)

def save_user_settings(username: str, settings: Dict[str, Any]) -> bool:
    """
    Guarda las configuraciones personalizadas de un usuario.
    
    Args:
        username: Nombre de usuario
        settings: Diccionario con las configuraciones a guardar
        
    Returns:
        True si la operación fue exitosa, False en caso contrario
    """
    users = load_users()
    
    if username not in users:
        return False
    
    # Crear o actualizar la sección de configuraciones
    if "settings" not in users[username]:
        users[username]["settings"] = {}
    
    # Actualizar las configuraciones con los nuevos valores
    users[username]["settings"].update(settings)
    
    # Guardar los cambios
    save_users(users)
    return True

def get_user_settings(username: str) -> Dict[str, Any]:
    """
    Obtiene las configuraciones personalizadas de un usuario.
    
    Args:
        username: Nombre de usuario
        
    Returns:
        Diccionario con las configuraciones del usuario, o un diccionario vacío si no existen
    """
    users = load_users()
    
    if username not in users:
        return {}
    
    # Obtener la sección de configuraciones o un diccionario vacío si no existe
    return users[username].get("settings", {})

def list_users() -> List[str]:
    """
    Lista todos los usuarios registrados.
    
    Returns:
        Lista con los nombres de usuario
    """
    users = load_users()
    return list(users.keys())

def delete_user(username: str) -> bool:
    """
    Elimina un usuario del sistema.
    
    Args:
        username: Nombre de usuario a eliminar
        
    Returns:
        True si el usuario fue eliminado, False si no existe
    """
    users = load_users()
    
    if username not in users:
        return False
    
    del users[username]
    save_users(users)
    return True

# Inicializar los usuarios la primera vez que se importa el módulo
if not os.path.exists(USERS_FILE):
    load_users() 