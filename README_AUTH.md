# Autenticación en el Chatbot de TalentLand 2025

Este documento explica cómo utilizar y configurar la autenticación para el chatbot de TalentLand 2025 impulsado por Google Gemini.

## Características de la autenticación

- **Autenticación obligatoria**: Ahora el chatbot requiere autenticación para acceder.
- **Usuarios predeterminados**: El sistema viene con dos usuarios preconfigurados:
  - Usuario: `admin` / Contraseña: `talentland2025` (rol de administrador)
  - Usuario: `usuario` / Contraseña: `password123` (rol de usuario)
- **Sistema seguro**: Las contraseñas se almacenan con hash y salt para mayor seguridad.
- **Gestión de usuarios**: Los administradores pueden registrar nuevos usuarios.
- **Persistencia**: Los usuarios se guardan en un archivo JSON para mantener los datos entre reinicios.

## Configuración

1. Asegúrate de tener configuradas estas variables en tu archivo `.env`:
   ```
   GEMINI_API_KEY=tu_clave_api_de_gemini
   CHAINLIT_AUTH_SECRET=tu_clave_secreta_para_autenticacion
   ```

2. La variable `CHAINLIT_AUTH_SECRET` es esencial para la seguridad de los tokens de autenticación. Si no la proporcionas, se generará una automáticamente, pero se perderá al reiniciar la aplicación.

## Uso del sistema de autenticación

### Iniciar sesión

1. Al acceder al chatbot, se mostrará una pantalla de inicio de sesión.
2. Ingresa tu nombre de usuario y contraseña.
3. Si son correctos, accederás al chatbot.

### Registrar nuevos usuarios (solo administradores)

Los administradores pueden registrar nuevos usuarios usando el comando dentro del chat:

```
/register [usuario] [contraseña]
```

Por ejemplo:
```
/register nuevo_usuario contraseña123
```

### Seguridad

- Los datos de los usuarios se almacenan en el archivo `users.json`.
- Las contraseñas nunca se guardan en texto plano, sino que se utiliza un hash SHA-256 con un salt único para cada usuario.
- Cada sesión de usuario está protegida por un token JWT firmado con la clave secreta.

## Personalización adicional

El sistema personaliza la experiencia basándose en el rol del usuario:
- Los administradores ven mensajes adicionales y tienen acceso a comandos especiales.
- El chatbot sabe con quién está hablando y puede adaptar sus respuestas según el usuario.

## Solución de problemas

- **Error al iniciar sesión**: Verifica que estás usando las credenciales correctas.
- **Pérdida de acceso administrador**: Si pierdes acceso al usuario admin, puedes eliminar el archivo `users.json` para reiniciar la base de usuarios.
- **Tokens inválidos**: Si cambia la variable `CHAINLIT_AUTH_SECRET`, todos los usuarios tendrán que iniciar sesión nuevamente.

## Próximas mejoras

- Interfaz de administración para gestionar usuarios
- Recuperación de contraseñas
- Integración con servicios OAuth externos (Google, Microsoft, etc.)
- Roles de usuario más granulares 