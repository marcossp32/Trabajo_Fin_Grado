from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def check_existing_tokens(user):
    """
    Verifies and refreshes the access tokens if they are expired. Returns the credentials
    if valid or refreshes them if necessary.

    Args:
        user: Instance of the user model containing the authentication tokens.

    Returns:
        Credentials: Updated Google OAuth credentials if possible, or None if an error occurs.
    """

    if not user.auth_token_access or not user.auth_token_refresh:
        logger.error("No se encontraron tokens válidos en la base de datos.")
        return None

    credentials = Credentials(
        token=user.auth_token_access,
        refresh_token=user.auth_token_refresh,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET
    )

    logger.info("Verificando tokens para: %s", user.email)
    logger.info("Access Token actual: %s...", user.auth_token_access[:10])
    logger.info("Refresh Token actual: %s...", user.auth_token_refresh[:10])

    # Intentar refrescar si el token está expirado
    if credentials.expired and credentials.refresh_token:
        try:
            logger.info("Intentando refrescar el token...")
            credentials.refresh(Request())
            user.auth_token_access = credentials.token

            # Guardar nuevo refresh token solo si se ha recibido uno nuevo
            if credentials.refresh_token:
                user.auth_token_refresh = credentials.refresh_token

            user.save()
            logger.info("Token refrescado correctamente.")
            return credentials
        except Exception as e:
            logger.error("Error al refrescar el token: %s", str(e))
            return None

    return credentials


def initialize_services(credentials):
    """
    Initializes the Gmail, Google Calendar, and OAuth2 services using Google OAuth credentials.
    
    Args:
        credentials: OAuth credentials of the user.
        
    Returns:
        Tuple(gmail_service, calendar_service, oauth_service): The initialized Gmail, Google Calendar, and OAuth2 services.
    """
    gmail_service = None
    calendar_service = None
    oauth_service = None

    logger.info("Credenciales válidas: %s", credentials.valid)
    logger.info("Access Token: %s", credentials.token)
    logger.info("Refresh Token: %s", credentials.refresh_token)

    try:
        # Inicializar el servicio de Gmail
        gmail_service = build('gmail', 'v1', credentials=credentials)
        logger.info("Servicio de Gmail inicializado correctamente.")
    except Exception as e:
        # Manejar errores al inicializar Gmail
        logger.error("Error al inicializar Gmail: %s", str(e))

    try:
        # Inicializar el servicio de Google Calendar
        calendar_service = build('calendar', 'v3', credentials=credentials)
        logger.info("Servicio de Google Calendar inicializado correctamente.")
    except Exception as e:
        # Manejar errores al inicializar Google Calendar
        logger.error("Error al inicializar Google Calendar: %s", str(e))
    
    try:
        # Inicializar el servicio de OAuth2 para obtener información del usuario
        oauth_service = build('oauth2', 'v2', credentials=credentials)
        logger.info("Servicio de OAuth2 inicializado correctamente.")
    except Exception as e:
        # Manejar errores al inicializar OAuth2
        logger.error("Error al inicializar OAuth2: %s", str(e))

    # Asegurarse de devolver siempre tres valores, incluso si alguno es None
    return gmail_service, calendar_service, oauth_service


def get_authenticated_user_info(oauth_service):
    """
    Retrieves the authenticated user's information using the previously initialized OAuth2 service.
    
    Args:
        oauth_service: Initialized OAuth2 service with credentials.
        
    Returns:
        dict: Information about the user's profile (e.g., email address).
        None: If an error occurs or the information cannot be retrieved.
    """
    try:
        # Obtener la información del usuario a través del servicio OAuth2
        user_info = oauth_service.userinfo().get().execute()
        return user_info
    except Exception as error:
        # Manejar errores al obtener la información del usuario
        logger.error("Error al obtener la información del usuario autenticado: %s", error)
        return None  # Retornar None si ocurre un error
