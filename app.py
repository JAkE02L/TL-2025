import os
import chainlit as cl
import google.generativeai as genai
from dotenv import load_dotenv
import secrets
from users import verify_password, get_user_data, register_user

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar la API de Google Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("No se encontró la clave API de Gemini. Asegúrate de configurar GEMINI_API_KEY en el archivo .env")

# Configurar la clave secreta para autenticación
auth_secret = os.getenv("CHAINLIT_AUTH_SECRET")
if not auth_secret:
    # Generar una clave secreta si no existe
    auth_secret = secrets.token_hex(16)
    print(f"AVISO: Se ha generado una clave CHAINLIT_AUTH_SECRET temporal: {auth_secret}")
    print("Para una configuración más segura, añádela a tu archivo .env")
    os.environ["CHAINLIT_AUTH_SECRET"] = auth_secret

# Imprimir información de depuración
print(f"API Key configurada: {api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}")

# Configurar el modelo Gemini
genai.configure(api_key=api_key)

# Lista de posibles modelos para probar
possible_models = [
    "gemini-pro",
    "gemini-1.0-pro",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "models/gemini-pro",
    "models/gemini-1.0-pro"
]

# Variable para almacenar el modelo que funcione
working_model = None
model = None

# Intentar listar modelos disponibles para diagnóstico
try:
    print("Modelos disponibles:")
    available_models = []
    for m in genai.list_models():
        model_name = m.name
        if "gemini" in model_name.lower():
            available_models.append(model_name)
            print(f"- {model_name}")
    
    # Si encontramos modelos disponibles, usarlos en lugar de nuestra lista estática
    if available_models:
        possible_models = available_models + possible_models
except Exception as e:
    print(f"Error al listar modelos: {e}")

# Probar cada modelo hasta encontrar uno que funcione
for model_name in possible_models:
    try:
        print(f"Probando modelo: {model_name}")
        test_model = genai.GenerativeModel(model_name)
        # Intentar una generación simple para verificar que funciona
        test_response = test_model.generate_content("Hola")
        print(f"¡Modelo {model_name} funciona! Respuesta: {test_response.text[:20]}...")
        working_model = model_name
        model = test_model
        break
    except Exception as e:
        print(f"Error con modelo {model_name}: {e}")

# Verificar si encontramos un modelo que funcione
if not working_model:
    print("No se pudo encontrar un modelo que funcione. Usando gemini-pro como último recurso.")
    working_model = "gemini-pro"
    model = genai.GenerativeModel(working_model)

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    """
    Función de autenticación para validar usuario y contraseña.
    Utiliza el sistema seguro de verificación de contraseñas.
    
    Args:
        username: Nombre de usuario
        password: Contraseña
    
    Returns:
        cl.User object si la autenticación es exitosa, None en caso contrario
    """
    if verify_password(username, password):
        user_data = get_user_data(username)
        return cl.User(
            identifier=username, 
            metadata={
                "role": user_data.get("role", "user"),
                "provider": "credentials"
            }
        )
    return None

@cl.on_message  # Este decorador indica que la función se ejecutará cuando el usuario envíe un mensaje
async def main(message: cl.Message):
    """
    Esta función procesa cada mensaje enviado por el usuario.
    Recibe el mensaje, lo envía a Gemini y devuelve la respuesta.
    
    Args:
        message: El mensaje enviado por el usuario
    """
    # Aquí procesamos el mensaje del usuario
    user_message = message.content
    
    # Si el mensaje es un comando para registrar un nuevo usuario
    if user_message.startswith("/register"):
        parts = user_message.split()
        if len(parts) >= 3:
            new_username = parts[1]
            new_password = parts[2]
            result = register_user(new_username, new_password)
            if result:
                await cl.Message(content=f"Usuario {new_username} registrado con éxito.").send()
            else:
                await cl.Message(content=f"Error: El usuario {new_username} ya existe.").send()
            return
        else:
            await cl.Message(content="Uso: /register [usuario] [contraseña]").send()
            return
    
    try:
        # Obtener información del usuario para personalizar la interacción
        app_user = cl.user_session.get("user")
        user_role = app_user.metadata.get("role", "user")
        
        # Para demostrar personalización basada en roles
        context = f"Estás hablando con {app_user.identifier} que tiene el rol de {user_role}. "
        
        # Enviamos el mensaje a Gemini y obtenemos la respuesta
        response = model.generate_content(context + user_message)
        
        # Enviamos la respuesta al usuario
        await cl.Message(content=response.text).send()
    except Exception as e:
        # En caso de error, mostramos información detallada para diagnóstico
        error_message = f"Error al procesar tu solicitud: {str(e)}\n\n"
        error_message += "Por favor, verifica:\n"
        error_message += "1. Que tu API key sea válida y esté activa\n"
        error_message += "2. Que tengas acceso a la API de Google Gemini\n"
        error_message += "3. Que tu plan de Google Gemini API permita el uso de esta funcionalidad\n"
        error_message += "4. Intenta obtener una nueva API key si el problema persiste"
        
        await cl.Message(content=error_message).send()

@cl.on_chat_start
async def start():
    """
    Esta función se ejecuta cuando se inicia el chat.
    """
    # Obtener información del usuario autenticado
    app_user = cl.user_session.get("user")
    
    # Mensaje de bienvenida
    welcome_message = f"¡Bienvenido {app_user.identifier} al Chatbot de TalentLand 2025 impulsado por Google Gemini!"
    welcome_message += f"\nEstoy usando el modelo {working_model}."
    
    # Agregar información específica según el rol del usuario
    if app_user.metadata.get("role") == "admin":
        welcome_message += "\n\nTienes acceso de administrador. Puedes usar el comando /register [usuario] [contraseña] para registrar nuevos usuarios."
    
    welcome_message += "\n\n¿En qué puedo ayudarte hoy?"
    
    await cl.Message(content=welcome_message).send() 