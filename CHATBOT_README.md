# Chatbot con Chainlit y Google Gemini para TalentLand 2025

Este proyecto es un chatbot creado con Chainlit y potenciado por Google Gemini para el workshop "Creando tu primera aplicación con IA" en TalentLand 2025.

## Requisitos

- Python 3.11 o superior
- Dependencias instaladas (chainlit, google-generativeai, python-dotenv)
- Una API Key de Google Gemini

## Configuración de la API Key de Gemini

1. Obtén una API Key de Google Gemini en [Google AI Studio](https://ai.google.dev/).
2. Copia tu API Key.
3. Actualiza el archivo `.env` en la raíz del proyecto:
   ```
   GEMINI_API_KEY=tu_api_key_aquí
   ```

## Cómo ejecutar el chatbot

Para ejecutar el chatbot, sigue estos pasos:

1. Asegúrate de tener todas las dependencias instaladas:
   ```
   uv sync
   ```

2. Asegúrate de haber configurado tu API Key de Gemini en el archivo `.env`.

3. Ejecuta la aplicación con Chainlit:
   ```
   chainlit run app.py -w
   ```
   
   El flag `-w` habilita el modo de desarrollo con recarga automática.

4. Abre tu navegador web en la dirección que aparece en la consola (generalmente `http://localhost:8000`).

## Estructura del proyecto

- `app.py`: Contiene la lógica principal del chatbot y la integración con Gemini.
- `chainlit.md`: Archivo de configuración para personalizar la interfaz de Chainlit.
- `pyproject.toml`: Archivo de configuración del proyecto y dependencias.
- `.env`: Archivo para almacenar las variables de entorno como la API key (no se incluye en el control de versión).

## Personalización

Puedes personalizar este chatbot de varias maneras:

1. Modifica las configuraciones del modelo Gemini en `app.py` para adaptar el comportamiento del bot.
2. Utiliza diferentes modelos de Gemini cambiando el valor del modelo en la lista `possible_models`.
3. Actualiza el archivo `chainlit.md` para cambiar la información mostrada en la interfaz.

## Solución de problemas comunes

### Error: models/gemini-pro is not found

Si encuentras un error como:
```
404 models/gemini-pro is not found for API version v1beta, or is not supported for generateContent
```

Esto puede ocurrir por varias razones:

1. **Versión de la API incorrecta:** La versión actual de la API puede tener un formato diferente para los nombres de modelos.
2. **Acceso limitado:** Tu API key puede no tener acceso a ciertos modelos.
3. **Región no soportada:** Algunas regiones pueden no tener acceso a todos los modelos.

Soluciones:

- El chatbot ahora intentará automáticamente diferentes nombres de modelos hasta encontrar uno que funcione.
- Puedes probar con otros modelos como "gemini-1.0-pro", "gemini-1.5-pro" o "gemini-1.5-flash".
- Verifica que tu API key tenga los permisos adecuados en la consola de Google AI Studio.
- Si continúa el problema, intenta obtener una nueva API key.

### Error: API key no válida

Si tu API key no funciona:

1. Asegúrate de que la API key está copiada correctamente en el archivo `.env`.
2. Verifica que la API key no haya expirado o haya sido revocada.
3. Crea una nueva API key en Google AI Studio si es necesario.

## Próximos pasos

Para hacer este chatbot más avanzado, considera:

1. Implementar memoria para mantener el contexto de la conversación.
2. Agregar una base de conocimiento utilizando RAG (Retrieval Augmented Generation).
3. Añadir elementos visuales como gráficos o imágenes usando las capacidades multimedia de Chainlit.
4. Explorar otros modelos de Google Gemini o integraciones con servicios adicionales. 