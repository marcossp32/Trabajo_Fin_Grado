# AISERV

AISERV es un asistente inteligente que automatiza la gestión de correos electrónicos y eventos utilizando las APIs de Gmail y Google Calendar, junto con OpenAI para generar respuestas automáticas personalizadas. Ofrece una interfaz de configuración intuitiva y un sistema en tiempo real mediante WebSockets.

## Características principales

- Autenticación mediante OAuth2 de Google
- Lectura y clasificación automática de correos en Gmail
- Generación de respuestas personalizadas con OpenAI (GPT-4)
- Creación, modificación y cancelación de eventos en Google Calendar
- Análisis emocional de los mensajes recibidos
- Configuración personalizada de horarios, prioridades y reglas
- Notificaciones organizadas por niveles de prioridad
- Interfaz web construida en React
- Backend en Django con soporte ASGI usando Daphne y WebSockets
- Persistencia de datos en PostgreSQL

## Arquitectura

- Backend: Django + Django Rest Framework (ASGI, Daphne)
- Frontend: React (Vite)
- WebSockets: Django Channels
- Autenticación: Google OAuth2
- IA: OpenAI API con plantillas Jinja2
- Base de datos: PostgreSQL

## Estructura del proyecto

```
aiserv/
├── api/                        # Lógica principal del backend (views, models, serializers)
├── email_utils/               # Procesamiento de correos y clasificación automática
├── application_utils/         # Orquestación de flujos automatizados
├── templates/                 # Plantillas Jinja2 para prompts a OpenAI
├── frontend/                  # Aplicación React
├── static/                    # Recursos estáticos
└── ...
```

## Requisitos

- Python 3.10 o superior
- Node.js 18 o superior
- PostgreSQL
- Credenciales OAuth2 de Google
- Clave de API de OpenAI

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/marcossp32/TFG-Marcos
```

2. Crear y activar entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
cd frontend
npm install
```

4. Configurar variables de entorno:

Crear un archivo `.env` con el siguiente contenido:

```
GOOGLE_CLIENT_ID=tu_client_id
GOOGLE_CLIENT_SECRET=tu_client_secret
GOOGLE_CLIENT_SECRETS_FILE=./client_secret.json
OPENAI_API_KEY=tu_api_key
PROMPT_DATA=./templates/prompt_data.j2
PROMPT_RESPONSE=./templates/prompt_response.j2
DATABASE_URL=postgres://usuario:contraseña@localhost:5432/aiserv
```

5. Aplicar migraciones y cargar servidor:

```bash
python manage.py makemigrations
python manage.py migrate
daphne -p 8000 TFGweb.asgi:application
```

6. Iniciar frontend:

```bash
cd frontend
npm run dev
```

## Uso

1. Accede a la página principal e inicia sesión con tu cuenta de Google.
2. Configura tus horarios, prioridades y reglas desde el panel de configuración.
3. Activa la automatización y AISERV comenzará a procesar tus correos en segundo plano.
4. Recibirás notificaciones clasificadas en tiempo real.

## WebSockets

AISERV utiliza WebSockets para actualizar el estado de notificaciones y mensajes en tiempo real. Esta funcionalidad se habilita automáticamente en el entorno de producción mediante Channels y Daphne.

## Licencia

Este proyecto está bajo una licencia privada. Contacta con el autor para más información.
