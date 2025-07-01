import os
import threading
import google_auth_oauthlib.flow
import logging
import pytz


from googleapiclient.discovery import build
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta, timezone
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from urllib.parse import urlencode


from .auth_utils import initialize_services, check_existing_tokens
from .models import aiservUser
from .models import StartConfig, ScheduleConfig, PriorityConfig, EventConfig,HistoryConfig,NotificationConfig
from .email_utils import main
from .serializers import (
    StartConfigSerializer,
    ScheduleConfigSerializer,
    PriorityConfigSerializer,
    EventConfigSerializer,
    HistoryConfigSerializer,
    NotificationConfigSerializer,
    PriorityNotificationOnlySerializer
)
from .application_utils.automatization_manager import EmailAutomationManager

logger = logging.getLogger(__name__)

# Configuración de OAuth y variables globales
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
]

GOOGLE_CLIENT_SECRETS_FILE = os.getenv('GOOGLE_CLIENT_SECRETS_FILE')
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Solo para entorno de desarrollo

# Función auxiliar para manejar el callback de Google OAuth
def handle_oauth2_callback(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
    )
    # flow.redirect_uri = request.build_absolute_uri('/api/connect/callback/')
    flow.redirect_uri = 'https://www.aiserv.es/api/connect/callback/'

    authorization_response = request.build_absolute_uri()

    try:
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as e:
        logger.error(f"Error al recuperar el token: {str(e)}", exc_info=True)
        return {"error": f"Error al recuperar el token: {str(e)}"}

    credentials = flow.credentials

    logger.debug(f"Access Token recibido: {credentials.token[:10]}...")
    logger.debug(f"Refresh Token recibido: {credentials.refresh_token[:10]}...")
    logger.debug(f"Token Expiry: {credentials.expiry}")

    # Obtener información del usuario autenticado
    try:
        oauth2_service = build('oauth2', 'v2', credentials=credentials)
        user_info = oauth2_service.userinfo().get().execute()
    except Exception as e:
        logger.error(f"Error al obtener la información del usuario: {str(e)}", exc_info=True)
        return {"error": f"Error al obtener la información del usuario: {str(e)}"}

    email = user_info.get('email')
    username = user_info.get('name', email.split('@')[0])

    # Guardar tokens correctamente en la base de datos
    user, created = aiservUser.objects.update_or_create(
        email=email,
        defaults={
            'username': username,
            'auth_token_access': credentials.token,
            'auth_token_refresh': credentials.refresh_token if credentials.refresh_token else user.auth_token_refresh,
            'is_active_auto': True
        }
    )

    if created:
        logger.info("Nuevo usuario creado y tokens almacenados correctamente.")
    else:
        logger.info("Usuario existente, tokens actualizados correctamente.")

    return {
        "email": user.email,
        "username": user.username,
        "is_active_auto": user.is_active_auto
    }



# Vista para iniciar el flujo de Google OAuth
class ConnectAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            GOOGLE_CLIENT_SECRETS_FILE,
            scopes=SCOPES
        )
        # flow.redirect_uri = request.build_absolute_uri('/api/connect/callback/')
        flow.redirect_uri = 'https://www.aiserv.es/api/connect/callback/'


        # Generar URL de autorización y estado
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        # Guardar el estado en la sesión
        logger.debug(f"Sesión antes de almacenar estado: {dict(request.session.items())}")
        request.session['oauth_state'] = state
        request.session.modified = True
        request.session.save()     
        logger.debug(f"Sesión después de almacenar estado: {dict(request.session.items())}")


        logger.debug(f"session_key en ConnectAPIView: {request.session.session_key}")


        return Response({"authorization_url": authorization_url}, status=status.HTTP_200_OK)


class OAuthCallbackAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        logger.debug(f"Sesión completa al llegar al callback: {dict(request.session.items())}")
        logger.debug(f"ID de sesión en callback: {request.session.session_key}")

        state_in_session = request.session.get('oauth_state')
        state_received = request.GET.get('state')

        logger.debug(f"Estado almacenado: {state_in_session}")
        logger.debug(f"Estado recibido: {state_received}")

        if not state_in_session or state_received != state_in_session:
            return Response({"error": "Estado inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # Manejo del callback y obtención de datos del usuario
        user_data = handle_oauth2_callback(request)
        if "error" in user_data:
            return Response({"error": user_data["error"]}, status=status.HTTP_400_BAD_REQUEST)

        # Guardar datos del usuario en la sesión
        request.session['user_data'] = user_data
        request.session.modified = True

        user = aiservUser.objects.get(email=user_data['email'])

        # Verificar y refrescar tokens correctamente
        credentials = check_existing_tokens(user)
        if not credentials:
            return Response({"error": "Error al obtener credenciales"}, status=status.HTTP_401_UNAUTHORIZED)

        # Inicializar servicios de Google
        gmail_service, calendar_service, oauth_service = initialize_services(credentials)

        request.session['services_initialized'] = {
            'email': user_data['email'],
            'calendar_service': True  # Solo guardamos la referencia
        }

        logger.debug(f"session_key en callback: {request.session.session_key}")


        # return redirect("http://localhost:5173")  # Cambiar en producción
        return redirect("https://www.aiserv.es")  # Meterle la s a https


class GetUserDataAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.session.get('user_data')
        if not user_data:
            return Response({"error": "No hay datos de usuario disponibles."}, status=status.HTTP_404_NOT_FOUND)

        # Confirmar que los datos están actualizados
        email = user_data.get('email')
        if not email:
            return Response({"error": "Datos del usuario incompletos."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = aiservUser.objects.get(email=user_data.get('email'))
        first_login = user.is_first_login

        user_data["is_first_login"] = user.is_first_login

        return Response(user_data, status=status.HTTP_200_OK)
    


class CompleteOnboardingAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.session.get("user_data")
        if not user_data:
            return Response({"error": "Usuario no autenticado."}, status=401)

        try:
            user = aiservUser.objects.get(email=user_data["email"])
            user.is_first_login = False
            user.save()
            return Response({"message": "Onboarding completado."}, status=200)
        except aiservUser.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=404)


class LogoutAPIView(APIView):
    """
    API para manejar el logout del usuario.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Obtener los datos del usuario antes de limpiar la sesión
        user_data = request.session.get('user_data')

        if user_data:
            try:
                user = aiservUser.objects.get(email=user_data.get('email'))
                user.auth_token_access = None
                user.auth_token_refresh = None
                user.save()
                logger.info(f"Tokens eliminados para el usuario: {user.email}")

            except aiservUser.DoesNotExist:
                logger.warning("Usuario no encontrado al intentar cerrar sesión.")

        # Eliminar la sesión del usuario
        request.session.flush()

        if user_data:
            return Response({"message": "Sesión cerrada exitosamente."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Sesión cerrada, pero no había datos de usuario."}, status=status.HTTP_200_OK)


class GetCalendarEventsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_data = request.session.get('user_data')

        if not user_data:
            return Response(
                {"error": "Usuario no autenticado. Inicia sesión nuevamente."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            email = user_data.get('email')
            user = aiservUser.objects.get(email=email)

            credentials = check_existing_tokens(user)
            if not credentials:
                return Response(
                    {"error": "No se encontraron credenciales válidas."},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            logger.info("Inicializando Google Calendar con las credenciales obtenidas...")
            service = build('calendar', 'v3', credentials=credentials)
            logger.info("Servicio de Google Calendar inicializado correctamente.")

            # Rango de tiempo del día actual en UTC
            local_tz = pytz.timezone("Europe/Madrid")
            now = datetime.now(local_tz)

            start_of_day = local_tz.localize(datetime(now.year, now.month, now.day, 0, 0, 0))
            end_of_day = start_of_day + timedelta(days=1)

            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_of_day.isoformat(),
                timeMax=end_of_day.isoformat(),
                maxResults=50,  # o el número que prefieras
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            logger.info(f"{len(events)} eventos obtenidos para el día actual.")

            return Response({"events": events}, status=status.HTTP_200_OK)

        except aiservUser.DoesNotExist:
            return Response(
                {"error": "El usuario no existe en la base de datos."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f"Error al obtener eventos de Google Calendar: {str(e)}", exc_info=True)
            return Response(
                {"error": "Ocurrió un error interno al obtener los eventos."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




# Guardar los datos en la base de datos

class SaveStartConfigAPIView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        logger.info(f"Datos recibidos en el backend: {request.data}") 
        
        email = request.data.get("email")
        if not email:
            return Response({"error": "El campo 'email' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        start_config, created = StartConfig.objects.get_or_create(gmail=email)

        data_to_update = {
            "full_name": request.data.get("fullname"),
            "charge": request.data.get("position"),  
            "language": request.data.get("language"),
            "details": request.data.get("details"),
        }

        logger.info(f"Datos a actualizar: {data_to_update}")

        serializer = StartConfigSerializer(start_config, data=data_to_update, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(f"Errores en el serializador: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SaveScheduleConfigAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"Datos recibidos en el backend (Schedule): {request.data}")  
        
        email = request.data.get("email")
        if not email:
            return Response({"error": "El campo 'email' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        schedule_config, created = ScheduleConfig.objects.get_or_create(gmail=email)

        raw_data = {
            "work_hours_from": request.data.get("init_schedule"),
            "work_hours_to": request.data.get("end_schedule"),
            "no_meetings_hours_from": request.data.get("init_schedule_no_meeting"),
            "no_meetings_hours_to": request.data.get("end_schedule_no_meeting"),
            "no_meetings_days": request.data.get("days_blocked"), 
            "tolerance": request.data.get("margin_event"),
        }

        data_to_update = {
            k: v for k, v in raw_data.items()
            if not (isinstance(v, str) and v.strip() == "")
        }

        logger.info(f"Datos a actualizar (Schedule): {data_to_update}")

        serializer = ScheduleConfigSerializer(schedule_config, data=data_to_update, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(f"Errores en el serializador (Schedule): {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavePriorityConfigAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"Datos recibidos en el backend (Priority): {request.data}")  
        
        email = request.data.get("email")
        if not email:
            return Response({"error": "El campo 'email' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        priority_config, created = PriorityConfig.objects.get_or_create(gmail=email)

        data_to_update = {
            "priority_issues": request.data.get("priority_subject"),
            "priority_people": request.data.get("priority_people"),
            "priority_hours_from": request.data.get("init_priority_schedule"),
            "priority_hours_to": request.data.get("end_priority_schedule"),
            "priority_days": request.data.get("priority_days"),  
        }

        logger.info(f"Datos a actualizar (Priority): {data_to_update}")

        serializer = PriorityConfigSerializer(priority_config, data=data_to_update, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(f"Errores en el serializador (Priority): {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SaveEventConfigAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"Datos recibidos en el backend (Event): {request.data}")  
        
        email = request.data.get("email")
        if not email:
            return Response({"error": "El campo 'email' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        event_config, created = EventConfig.objects.get_or_create(gmail=email)

        data_to_update = {
            "meeting_duration": request.data.get("meeting_duration"),
            "meeting_limit": request.data.get("meeting_limit"),
            "notify_meeting": request.data.get("notify_meeting"),
            "propose_meeting": request.data.get("meeting_porpose"),
            "free_days": request.data.get("free_days", []) 
        }

        logger.info(f"Datos a actualizar (Event): {data_to_update}")  

        serializer = EventConfigSerializer(event_config, data=data_to_update, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(f"Errores en el serializador (Event): {serializer.errors}")  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StartFlowRequestAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "El campo 'email' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        missing_fields = []

        try:
            start_config = StartConfig.objects.get(gmail=email)
        except StartConfig.DoesNotExist:
            missing_fields.extend(["full_name", "language"])
        else:
            if not start_config.full_name:
                missing_fields.append("full_name")
            if not start_config.language:
                missing_fields.append("language")

        try:
            schedule_config = ScheduleConfig.objects.get(gmail=email)
        except ScheduleConfig.DoesNotExist:
            missing_fields.extend(["work_hours_from", "work_hours_to"])
        else:
            if not schedule_config.work_hours_from:
                missing_fields.append("work_hours_from")
            if not schedule_config.work_hours_to:
                missing_fields.append("work_hours_to")

        if missing_fields:
            missing_fields = list(set(missing_fields))
            return Response(
                {
                    "error": "Faltan datos obligatorios",
                    "missing_fields": missing_fields
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Todos los campos obligatorios están completos. Puedes iniciar el flujo."},
            status=status.HTTP_200_OK
        )


active_flows = {}

class StartFlowAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        action = request.data.get("action", "start").lower()

        if not email:
            return Response(
                {"error": "El campo 'email' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = aiservUser.objects.get(email=email)
        except aiservUser.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        if action == "start":
            user.is_active_auto = True
            user.save()

            if email in active_flows and active_flows[email].is_alive():
                return Response(
                    {"message": "El flujo ya está en ejecución."},
                    status=status.HTTP_200_OK
                )
            else:
                t = threading.Thread(target=main, args=(user.id,))
                # Alternativa con LangChain:
                # manager = EmailAutomationManager(user_id=user.id)
                # t = threading.Thread(target=manager.run)

                t.daemon = True
                t.start()
                active_flows[email] = t
                logger.info(f"Flujo iniciado para el usuario {email}")
                return Response(
                    {"message": "Flujo iniciado."},
                    status=status.HTTP_200_OK
                )

        elif action == "stop":
            user.is_active_auto = False
            user.save()

            if email in active_flows:
                del active_flows[email]
                logger.info(f"Flujo detenido para el usuario {email}")
                return Response(
                    {"message": "Flujo detenido."},
                    status=status.HTTP_200_OK
                )
            else:
                logger.info(f"No había flujo activo para detener: {email}")
                return Response(
                    {"message": "No hay un flujo en ejecución para detener."},
                    status=status.HTTP_200_OK
                )
        else:
            return Response(
                {"error": "Acción no reconocida. Use 'start' o 'stop'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        

class GetUserHistoryAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.session.get('user_data')
        if not user_data:
            return Response({"error": "No hay datos de usuario disponibles."}, status=status.HTTP_404_NOT_FOUND)

        email = user_data.get('email')
        if not email:
            return Response({"error": "Datos del usuario incompletos."}, status=status.HTTP_400_BAD_REQUEST)

        history_messages = HistoryConfig.objects.filter(gmail=email).order_by('-sent_date')

        if not history_messages.exists():
            return Response({"message": "No hay mensajes en el historial para este usuario."}, status=status.HTTP_200_OK)

        serialized_data = HistoryConfigSerializer(history_messages, many=True).data 

        return Response(serialized_data, status=status.HTTP_200_OK)


class NotificationPagination(PageNumberPagination):
    page_size = 8  # Número de notificaciones por página
    page_size_query_param = 'page_size'
    max_page_size = 20


class GetNotificationsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_data = request.session.get('user_data')
        if not user_data:
            return Response({"error": "Usuario no autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

        email = user_data.get("email")
        if not email:
            return Response({"error": "No se pudo obtener el email del usuario."}, status=status.HTTP_400_BAD_REQUEST)

        notifications = NotificationConfig.objects.filter(gmail=email).order_by('-sent_date')

        paginator = NotificationPagination()
        result_page = paginator.paginate_queryset(notifications, request)
        serializer = NotificationConfigSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class GetOnlyNotificationLevelsAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        user_data = request.session.get('user_data')
        if not user_data:
            return Response({"error": "Usuario no autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

        email = user_data.get("email")
        if not email:
            return Response({"error": "No se pudo obtener el email del usuario."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            config = PriorityConfig.objects.get(gmail=email)
        except PriorityConfig.DoesNotExist:
            return Response({"error": "No se encontró configuración para ese email."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PriorityNotificationOnlySerializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdatePriorityNotificationsAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.session.get("user_data")
        if not user_data:
            return Response({"error": "Usuario no autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

        email = user_data.get("email")
        if not email:
            return Response({"error": "No se pudo obtener el email del usuario."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            config = PriorityConfig.objects.get(gmail=email)
        except PriorityConfig.DoesNotExist:
            return Response({"error": "No se encontró configuración para ese email."}, status=status.HTTP_404_NOT_FOUND)

        config.notification_low = request.data.get("notification_low", config.notification_low)
        config.notification_moderate = request.data.get("notification_moderate", config.notification_moderate)
        config.notification_high = request.data.get("notification_high", config.notification_high)
        config.notification_urgent = request.data.get("notification_urgent", config.notification_urgent)
        config.save()

        logger.info(f"Notificaciones actualizadas correctamente para {email}")

        return Response({"success": "Configuración de notificaciones actualizada correctamente."}, status=status.HTTP_200_OK)
