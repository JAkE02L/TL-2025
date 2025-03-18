import os
import chainlit as cl
import google.generativeai as genai
from dotenv import load_dotenv
import secrets
from users import verify_password, get_user_data, register_user, save_user_settings, get_user_settings
from chainlit.input_widget import Select

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
available_models = []

# Intentar listar modelos disponibles para diagnóstico
try:
    print("Modelos disponibles:")
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

@cl.on_settings_update
async def handle_settings_update(settings):
    """
    Maneja las actualizaciones de configuración del chat.
    Se ejecuta cuando el usuario cambia alguna configuración.
    
    Args:
        settings: Diccionario con las configuraciones actualizadas
    """
    global model
    
    # Obtener el usuario actual
    app_user = cl.user_session.get("user")
    username = app_user.identifier
    
    # Obtener el modelo seleccionado
    selected_model = settings.get("Modelo", working_model)
    
    try:
        # Actualizar el modelo para este usuario
        new_model = genai.GenerativeModel(selected_model)
        
        # Guardar el modelo en la sesión del usuario
        cl.user_session.set("model", new_model)
        cl.user_session.set("model_name", selected_model)
        
        # Guardar la preferencia del modelo en los ajustes del usuario
        save_user_settings(username, {"preferred_model": selected_model})
        
        # Notificar al usuario
        await cl.Message(
            content=f"✅ Modelo actualizado a: {selected_model}"
        ).send()
    except Exception as e:
        # Si hay un error, notificar al usuario y mantener el modelo anterior
        await cl.Message(
            content=f"❌ Error al cambiar al modelo {selected_model}: {str(e)}\nSe mantendrá el modelo actual."
        ).send()

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
        
        # Usar el modelo específico de la sesión del usuario si existe
        current_model = cl.user_session.get("model")
        if not current_model:
            current_model = model
        
        # Para demostrar personalización basada en roles
        context = f"Estás hablando con {app_user.identifier} que tiene el rol de {user_role}. "
        
        # Enviamos el mensaje a Gemini y obtenemos la respuesta
        response = current_model.generate_content(context + user_message)
        
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
    username = app_user.identifier
    
    # Verificar si el usuario tiene un modelo preferido guardado
    user_settings = get_user_settings(username)
    preferred_model = user_settings.get("preferred_model", working_model)
    
    # Intentar usar el modelo preferido del usuario
    try:
        user_model = genai.GenerativeModel(preferred_model)
        cl.user_session.set("model", user_model)
        cl.user_session.set("model_name", preferred_model)
    except Exception:
        # Si hay error, usar el modelo por defecto
        cl.user_session.set("model", model)
        cl.user_session.set("model_name", working_model)
        preferred_model = working_model
    
    # Configurar las opciones del chat
    # Crea una lista de modelos disponibles para el selector de configuración
    model_options = available_models if available_models else possible_models
    
    # Encuentra el índice del modelo preferido del usuario en la lista de opciones
    try:
        initial_index = model_options.index(preferred_model)
    except ValueError:
        initial_index = 0  # Si no encuentra el modelo, usa el primero
    
    # Crea y envía la configuración del chat
    settings = await cl.ChatSettings(
        [
            Select(
                id="Modelo",
                label="Modelo Gemini",
                values=model_options,
                initial_index=initial_index,
                description="Selecciona el modelo de Gemini que quieres usar para esta conversación",
            )
        ]
    ).send()
    
    # Mensaje de bienvenida
    welcome_message = f"¡Bienvenido {username} al Chatbot de TalentLand 2025 impulsado por Google Gemini!"
    welcome_message += f"\nEstoy usando el modelo {preferred_model}."
    welcome_message += "\n\nPuedes cambiar el modelo en cualquier momento usando el ícono de configuración ⚙️ en la parte inferior de la pantalla."
    
    # Agregar información específica según el rol del usuario
    if app_user.metadata.get("role") == "admin":
        welcome_message += "\n\nTienes acceso de administrador. Puedes usar el comando /register [usuario] [contraseña] para registrar nuevos usuarios."
    
    welcome_message += "\n\n¿En qué puedo ayudarte hoy?"
    
    await cl.Message(content=welcome_message).send() 