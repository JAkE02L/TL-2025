# TL-2025
## Creando tu primera aplicación con IA
Bienvenido al workshop para crear tu primera aplicación con IA.
Para este workshop recomendamos usar un IDE como Cursor o Visual Studio Code con Copilot instalado para aprovechar al máximo las herramientas que la IA nos proporciona al momento de crear aplicaciones.
A continuación encontrarás las instrucciones paso a paso que seguiremos durante este workshop para que puedas replicar tu proyecto.
## INSTRUCCIONES
### Configuración inicial
1. Empecemos por preguntarle a la IA qué es la librería de Python llamada uv.
2. Sigamos las instrucciones para instalar uv e iniciar un proyecto.
3. Preguntemos qué librerías de Python recomienda para crear un chatbot
4. Si no lo menciona en su respuesta, preguntémosle por chainlit.
5. Ahora pidámosle al agente que instale chainlit.
6. Pidámosle que cree un ejemplo básico de chatbot con chainlit.

### Agregando un LLM
Ahora que tenemos un diseño básico del chatbot, vamos a integrarlo con un LLM.
1. Preguntarle a la IA cómo obtener una clave de API de Gemini.
2. Sigue los pasos para obtener la API Key (no la compartas con nadie) y cópiala en el portapapeles.
3. Pidámosle al agente que usa la API Key de gemini para que nuestro chatbot nos responda.
4. Iniciemos la aplicación y hagamos una pregunta para revisar si funciona correctamente.
5. En caso de errores, copiemos el error y peguémoslo en el chat. Repetir hasta que el chatbot funcione.
6. Hazle una pregunta.
7. Preguntémosle a la IA cómo podemos agregar autenticación a la aplicación con usuario/contraseña.
8. Pidámosle a la IA que el usuario escoja a partir de los modelos disponibles desde una sección de ajustes
9. Prueba los distintos modelos del lenguaje.
## Funcionalidades implementadas

### Autenticación de usuarios
La aplicación cuenta con un sistema de autenticación basado en usuario y contraseña. Los usuarios predeterminados son:
- Usuario: `admin`, Contraseña: `talentland2025` (con rol de administrador)
- Usuario: `usuario`, Contraseña: `password123` (con rol de usuario estándar)

Los administradores pueden registrar nuevos usuarios usando el comando `/register [usuario] [contraseña]` dentro del chat.

### Selección de modelo de IA
La aplicación permite a cada usuario seleccionar el modelo de Google Gemini que desea utilizar para sus conversaciones:

1. Para acceder a la configuración, haz clic en el ícono de engranaje (⚙️) en la parte inferior de la pantalla de chat
2. En el panel de configuración, selecciona el modelo que deseas utilizar en el menú desplegable "Modelo Gemini"
3. Una vez seleccionado, la aplicación guardará esta preferencia para futuras sesiones

Los modelos disponibles dependen de tu API key de Google Gemini y pueden incluir:
- gemini-pro
- gemini-1.0-pro
- gemini-1.5-pro
- gemini-1.5-flash
- Y otros modelos disponibles a través de tu cuenta

La aplicación guardará las preferencias de modelo para cada usuario, manteniendo esa selección en futuras sesiones.

## Ejecutar la aplicación

Para ejecutar la aplicación, asegúrate de tener instaladas todas las dependencias y ejecuta:

```bash
chainlit run app.py
```

La aplicación estará disponible en http://localhost:8000 por defecto.