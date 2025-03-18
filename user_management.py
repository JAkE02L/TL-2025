"""
Herramienta de gestión de usuarios para el Chatbot de TalentLand 2025.
Este script permite administrar usuarios desde la línea de comandos.
"""

import argparse
import sys
from users import (
    register_user, 
    delete_user, 
    list_users, 
    change_password, 
    get_user_data
)

def main():
    """Punto de entrada principal para la herramienta de gestión de usuarios."""
    
    parser = argparse.ArgumentParser(description='Herramienta de gestión de usuarios del chatbot de TalentLand 2025')
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando para listar usuarios
    list_parser = subparsers.add_parser('list', help='Listar todos los usuarios')
    
    # Comando para agregar usuario
    add_parser = subparsers.add_parser('add', help='Agregar un nuevo usuario')
    add_parser.add_argument('username', help='Nombre de usuario')
    add_parser.add_argument('password', help='Contraseña')
    add_parser.add_argument('--role', default='user', choices=['user', 'admin'], help='Rol del usuario (default: user)')
    
    # Comando para eliminar usuario
    delete_parser = subparsers.add_parser('delete', help='Eliminar un usuario')
    delete_parser.add_argument('username', help='Nombre de usuario a eliminar')
    
    # Comando para cambiar contraseña
    passwd_parser = subparsers.add_parser('passwd', help='Cambiar contraseña de un usuario')
    passwd_parser.add_argument('username', help='Nombre de usuario')
    passwd_parser.add_argument('old_password', help='Contraseña actual')
    passwd_parser.add_argument('new_password', help='Nueva contraseña')
    
    # Comando para ver detalles de un usuario
    info_parser = subparsers.add_parser('info', help='Ver detalles de un usuario')
    info_parser.add_argument('username', help='Nombre de usuario')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Ejecutar el comando correspondiente
    if args.command == 'list':
        print_user_list()
    elif args.command == 'add':
        add_user(args.username, args.password, args.role)
    elif args.command == 'delete':
        remove_user(args.username)
    elif args.command == 'passwd':
        update_password(args.username, args.old_password, args.new_password)
    elif args.command == 'info':
        show_user_info(args.username)
    else:
        parser.print_help()
        sys.exit(1)

def print_user_list():
    """Muestra la lista de usuarios registrados."""
    users = list_users()
    if not users:
        print("No hay usuarios registrados.")
        return
    
    print("\nUsuarios registrados:")
    print("-" * 40)
    for user in users:
        user_data = get_user_data(user)
        role = user_data.get('role', 'user')
        created_at = user_data.get('created_at', 'desconocido')
        print(f"- {user} (rol: {role})")
    print("-" * 40)
    print(f"Total: {len(users)} usuario(s)")

def add_user(username, password, role):
    """Registra un nuevo usuario."""
    if register_user(username, password, role):
        print(f"Usuario '{username}' con rol '{role}' creado exitosamente.")
    else:
        print(f"ERROR: El usuario '{username}' ya existe.")
        sys.exit(1)

def remove_user(username):
    """Elimina un usuario."""
    if delete_user(username):
        print(f"Usuario '{username}' eliminado exitosamente.")
    else:
        print(f"ERROR: El usuario '{username}' no existe.")
        sys.exit(1)

def update_password(username, old_password, new_password):
    """Cambia la contraseña de un usuario."""
    if change_password(username, old_password, new_password):
        print(f"Contraseña del usuario '{username}' actualizada exitosamente.")
    else:
        print(f"ERROR: No se pudo actualizar la contraseña. Verifica que el usuario exista y que la contraseña actual sea correcta.")
        sys.exit(1)

def show_user_info(username):
    """Muestra información detallada de un usuario."""
    user_data = get_user_data(username)
    if not user_data:
        print(f"ERROR: El usuario '{username}' no existe.")
        sys.exit(1)
    
    import time
    from datetime import datetime
    
    print(f"\nInformación del usuario: {username}")
    print("-" * 40)
    print(f"Rol: {user_data.get('role', 'user')}")
    
    if 'created_at' in user_data:
        creation_date = datetime.fromtimestamp(user_data['created_at'])
        print(f"Fecha de creación: {creation_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("-" * 40)

if __name__ == "__main__":
    main() 