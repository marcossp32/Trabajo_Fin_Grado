from datetime import datetime, timedelta, timezone
from tzlocal import get_localzone
from .config.event import EventConfig
import logging
import re

logger = logging.getLogger(__name__)

# Función para obtener los próximos eventos del calendario del usuario
def fetch_events(calendar_service, num_events=50):
    """
    Fetches the next upcoming events from the user's Google Calendar.

    Args:
        calendar_service: Initialized Google Calendar API service.
        num_events: The maximum number of events to fetch (default is 50).

    Returns:
        list: A list of upcoming events with start, end, event ID, creator, and attendees.
    """
    if not calendar_service:
        print("Google Calendar service unavailable.")
        return []

    now = datetime.now(timezone.utc).isoformat()

    try:
        result = calendar_service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=num_events,
            singleEvents=True,
            orderBy='startTime',
            timeZone='Europe/Madrid'
        ).execute()

        events = result.get('items', [])
        if not events:
            print('No upcoming events.')
            return []

        event_data = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            event_id = event['id']
            creator = event.get('creator', {}).get('email', 'Desconocido')
            attendees = [a['email'] for a in event.get('attendees', [])] if 'attendees' in event else []

            event_data.append({
                "start": start,
                "end": end,
                "event_id": event_id,
                "creator": creator,
                "attendees": attendees
            })

        return event_data

    except Exception as e:
        print(f"Error fetching events: {e}")
        return []




# Función para generar un evento en el calendario    
def generate_event(event_data, sender, subject, calendar_service,user,email_type):
    """
    Generates a new event in the user's Google Calendar based on extracted email data.

    Args:
        event_data: A dictionary containing event details (date, participants, place, etc.).
        sender: The email address of the person sending the event request.
        subject: The subject of the email or event description.
        calendar_service: Initialized Google Calendar API service.
    """

    try:
        place = event_data.get('place')
        date = event_data.get('date')
        participants = event_data.get('participants', []) 
        event_type = event_data.get('event_type', 'Meeting')
        priority = event_data.get('priority')
        meeting_method = event_data.get('meeting_method')
        meeting_link = event_data.get('meeting_link')
        attachments = event_data.get('attachments', [])
        deadline = event_data.get('deadline')
        details = event_data.get('details')
        duration_in_email = event_data.get('duration')


        # Manejar la duración del evento en diferentes formatos (e.g., "1 hora", "30 minutos")
        if duration_in_email:
            if 'hora' in duration_in_email:
                duration = timedelta(hours=int(duration_in_email.split()[0]))
            elif 'minuto' in duration_in_email:
                duration = timedelta(minutes=int(duration_in_email.split()[0]))
            else:
                duration = timedelta(minutes=60)  # Duración predeterminada de 60 minutos si el formato no es claro
        else:
            # Obtener configuración predeterminada si no se proporciona duración
            event_config = EventConfig.objects.get(gmail=user.email)
            default_duration_minutes = event_config.meeting_duration if event_config.meeting_duration else 60
            duration = timedelta(minutes=default_duration_minutes)

        # Verificar si hay una fecha válida en el evento
        if date:
            # local_timezone = get_localzone()
            # event_start_local = datetime.fromisoformat(date).replace(tzinfo=local_timezone)
            # event_start_utc = event_start_local.astimezone(timezone.utc)
            # event_end_utc = event_start_utc + duration
            
            # start = event_start_utc.isoformat()
            # end = event_end_utc.isoformat()
            
            # Convertir la fecha sin cambiar su zona horaria original
            event_start = datetime.fromisoformat(date)  # Ya incluye la zona horaria

            # Calcular la hora de finalización con la misma zona horaria
            event_end = event_start + duration

            # Convertir a formato ISO8601 sin tocar la zona horaria
            start = event_start.isoformat()
            end = event_end.isoformat()
        else:
            raise ValueError("La fecha es obligatoria para crear un evento.")

        # Agregar al remitente como participante si no está ya en la lista
        if sender not in participants:
            participants.append(sender)

        # Crear el cuerpo del evento para Google Calendar
        event_body = {
            'summary': f'{event_type}',
            'description': details if details else subject,
            'start': {'dateTime': start, 'timeZone': 'UTC'},
            'end': {'dateTime': end, 'timeZone': 'UTC'},
            'attendees': [{'email': participant} for participant in participants],
            'sendUpdates': 'all'
        }

        # Agregar la ubicación si se especifica
        if place:
            event_body['location'] = place

        # Agregar un enlace de videoconferencia si se proporciona
        if meeting_link:
            event_body['conferenceData'] = {
                'createRequest': {
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                    'requestId': 'meeting'
                }
            }

        # Incluir la prioridad en la descripción si está presente
        if priority:
            event_body['description'] += f"\nPrioridad: {priority}"

        # Incluir archivos adjuntos si se proporcionan
        if attachments:
            event_body['attachments'] = [{'fileUrl': attachment} for attachment in attachments]

        # Incluir la fecha límite en la descripción si está presente
        if deadline:
            event_body['description'] += f"\nFecha límite: {deadline}"

        # Insertar el evento en el calendario
        insert_event_in_calendar(event_body, calendar_service,email_type)

    except Exception as e:
        print(f"Error al generar el evento: {str(e)}")


def find_event_in_calendar(extracted_data, calendar_service):
    """
    Searches for an event in the calendar based on the extracted email data.
    Args:
        extracted_data: The event data being searched for.
        calendar_service: Google Calendar API service.
    Returns:
        str: The ID of the found event, or None if not found.
    """

    try:
        # Obtener la fecha y hora del evento previo
        logger.info(f"EXTRACTED DATAAAAAAAA:     {extracted_data}")
        previous_event_date = extracted_data.get('previous_event_date',"")
        logger.info(f"EVENTOS PREVIOS: {previous_event_date}")
        if not previous_event_date:
            print("No se proporcionó la fecha del evento anterior.")
            return None

        # Convertir la fecha a formato compatible con ISO
        previous_event_datetime = datetime.fromisoformat(previous_event_date).isoformat()

        # Obtener los eventos del calendario
        events = fetch_events(calendar_service)

        logger.info(f"EVENTS: {events}")
        
        # Buscar el evento en el calendario que coincida con la fecha anterior
        for event in events:
            event_start = event["start"] or None  # Desglosar la lista de fechas e ID
            logger.info(f"EVENT START: {event_start}")
            event_id = event["event_id"] or None

            # Si la fecha del evento coincide con la fecha del evento anterior
            if previous_event_datetime in event_start or previous_event_date == event_start:
                # Devolver el ID del evento
                logger.info(f"EVENT ID: {event_id}")
                return event_id

        # Si no se encuentra ningún evento que coincida
        return None

    except Exception as e:
        print(f"Error buscando el evento en el calendario: {e}")
        return None


import json, logging, pytz
from datetime import datetime
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)
TZ = pytz.timezone("Europe/Madrid")

def to_rfc3339(dt: datetime) -> str:
    """ Devuelve la fecha en RFC 3339 y UTC. """
    if dt.tzinfo is None:
        dt = TZ.localize(dt)      
    return dt.astimezone(pytz.UTC).isoformat()

def handle_http_error(err: HttpError) -> None:
    """Registra la respuesta completa de Google Calendar."""
    status = getattr(err.resp, "status", "sin status")
    try:
        detalle = json.loads(err.content.decode())["error"]["message"]
    except Exception:
        detalle = err.content.decode() if err.content else "sin cuerpo"
    logger.error("Google Calendar API error %s: %s", status, detalle)
    # opcionalmente: raise


def change_event(extracted_data, calendar_service, event_id, user):
    try:
        new_start = datetime.fromisoformat(extracted_data["new_date"])

        # duración: “1 hora”, “30 minutos”, “90”…
        dur_raw = extracted_data.get("duration", "").lower()
        if "hora" in dur_raw:
            dur = timedelta(hours=int(re.findall(r"\d+", dur_raw)[0]))
        elif "minuto" in dur_raw:
            dur = timedelta(minutes=int(re.findall(r"\d+", dur_raw)[0]))
        elif dur_raw.isdigit():
            dur = timedelta(minutes=int(dur_raw))
        else:
            dur = timedelta(minutes=60)

        new_end = new_start + dur

        event_body = {
            "start": {"dateTime": to_rfc3339(new_start), "timeZone": "UTC"},
            "end":   {"dateTime": to_rfc3339(new_end),   "timeZone": "UTC"},
        }

        logging.debug("PATCH que se envía: %s", event_body)

        updated = (calendar_service.events()
                   .patch(calendarId="primary",
                          eventId=event_id,
                          body=event_body,
                          sendUpdates="all")
                   .execute())

        logging.info("Evento %s actualizado.", updated["id"])
        return updated

    except HttpError as err:
        handle_http_error(err)     
    except Exception as e:
        logging.exception(f"Fallo inesperado en change_event {e}")



def cancel_event(calendar_service, event_id):
    """
    Cancels an event in the user's calendar based on the extracted email data.
    Args:
        calendar_service: Google Calendar API service.
        event_id: The ID of the event to be canceled.
    """

    try:

        # Eliminar el evento en el calendario
        calendar_service.events().delete(
            calendarId='primary',
            eventId=event_id,
            sendUpdates='all'
        ).execute()

        print("Evento cancelado exitosamente.")

    except Exception as e:
        print(f"Error cancelando el evento: {e}")




# Función para insertar un evento en el calendario de Google
def insert_event_in_calendar(event, calendar_service,email_type):
    """
    Inserts a new event into the user's Google Calendar.

    Args:
        event: The event details in dictionary format to be added to the calendar.
        calendar_service: Initialized Google Calendar API service.
    """
    try:
        if email_type == 'new_event':
            # Insertar el evento en el calendario
            event = calendar_service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all',
                sendNotifications=True
            ).execute()

            print(f"Event created: {event.get('htmlLink')}")  # Mostrar el enlace del evento creado
        elif email_type == 'meeting_notification':
            # Insertar el evento en el calendario
            event = calendar_service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='none',
            ).execute()

            print(f"Event created: {event.get('htmlLink')}")
    except Exception as e:
        # Manejar cualquier error que ocurra al insertar el evento
        print(f"Error inserting event: {e}")
