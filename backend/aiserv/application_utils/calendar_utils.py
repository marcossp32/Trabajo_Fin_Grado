
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from tzlocal import get_localzone

from ..models import ( EventConfig,aiservUser)

class CalendarUtils:
    def __init__(self, calendar_service: Any,user: aiservUser) -> None:
        """
        Inicializa la utilidad de calendario con un servicio de Google Calendar.

        Args:
            calendar_service: Instancia inicializada del servicio de la API de Google Calendar.
        """
        self.calendar_service = calendar_service
        self.user = user

    def fetch_events(self, num_events: int = 50) -> List[Tuple[str, str, str]]:
        """
        Obtiene los próximos eventos del calendario del usuario.

        Args:
            num_events: Número máximo de eventos a obtener (por defecto 50).

        Returns:
            List[Tuple[str, str, str]]: Lista de tuplas con (fecha inicio, fecha fin, id del evento).
        """
        if not self.calendar_service:
            print("Google Calendar service unavailable.")
            return []

        now: str = datetime.now(timezone.utc).isoformat()

        try:
            result: Dict[str, Any] = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=num_events,
                singleEvents=True,
                orderBy='startTime',
                timeZone='Europe/Madrid'
            ).execute()

            events: List[Dict[str, Any]] = result.get('items', [])
            if not events:
                print("No upcoming events.")
                return []

            event_data: List[Tuple[str, str, str]] = []
            for event in events:
                start: str = event['start'].get('dateTime', event['start'].get('date'))
                end: str = event['end'].get('dateTime', event['end'].get('date'))
                event_id: str = event['id']
                event_data.append((start, end, event_id))
                print(f"{start} - {end} (ID: {event_id})")

            return event_data

        except Exception as e:
            print(f"Error fetching events: {e}")
            return []

    def generate_event(
        self,
        event_data: Dict[str, Any], 
        sender: str,  
        subject: str, 
        user: aiservUser,
    ) -> None:
        """
        Genera un evento nuevo en el calendario del usuario basándose en los datos extraídos.

        Args:
            event_data: Diccionario con los detalles del evento (fecha, participantes, lugar, etc.).
            sender: Dirección de correo del remitente.
            subject: Asunto del correo o descripción del evento.
            user: Objeto del usuario, se usa para obtener configuraciones por defecto.
        """
        try:
            place: Optional[str] = event_data.get('place')
            date_str: Optional[str] = event_data.get('date')
            participants: List[str] = event_data.get('participants', [])
            event_type: str = event_data.get('event_type', 'Meeting')
            priority: Optional[str] = event_data.get('priority')
            meeting_link: Optional[str] = event_data.get('meeting_link')
            attachments: List[str] = event_data.get('attachments', [])
            deadline: Optional[str] = event_data.get('deadline')
            details: Optional[str] = event_data.get('details')
            duration_in_email: Optional[str] = event_data.get('duration')

            if not date_str:
                raise ValueError("La fecha es obligatoria para crear un evento.")

            # Convertir la fecha y calcular la duración
            event_start: datetime = datetime.fromisoformat(date_str)
            duration: timedelta = self._parse_duration(duration_in_email, user.email)
            event_end: datetime = event_start + duration
            start: str = event_start.isoformat()
            end: str = event_end.isoformat()

            # Asegurar que el remitente esté en la lista de participantes
            if sender not in participants:
                participants.append(sender)

            event_body: Dict[str, Any] = {
                'summary': event_type,
                'description': details if details else subject,
                'start': {'dateTime': start, 'timeZone': 'UTC'},
                'end': {'dateTime': end, 'timeZone': 'UTC'},
                'attendees': [{'email': participant} for participant in participants],
                'sendUpdates': 'all'
            }

            if place:
                event_body['location'] = place

            if meeting_link:
                event_body['conferenceData'] = {
                    'createRequest': {
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                        'requestId': 'meeting'
                    }
                }

            if priority:
                event_body['description'] += f"\nPrioridad: {priority}"

            if attachments:
                event_body['attachments'] = [{'fileUrl': attachment} for attachment in attachments]

            if deadline:
                event_body['description'] += f"\nFecha límite: {deadline}"

            self._insert_event_in_calendar(event_body)

        except Exception as e:
            print(f"Error al generar el evento: {e}")

    def find_event_in_calendar(self, previous_event_date: str) -> Optional[str]:
        """
        Busca un evento en el calendario basándose en la fecha proporcionada en los datos extraídos.

        Args:
            extracted_data: Datos extraídos que contienen la fecha del evento previo.

        Returns:
            Optional[str]: El ID del evento encontrado o None si no se encuentra.
        """
        try:
            if not previous_event_date:
                print("No se proporcionó la fecha del evento anterior.")
                return None

            previous_event_datetime: str = datetime.fromisoformat(previous_event_date).isoformat()
            events: List[Tuple[str, str, str]] = self.fetch_events()

            for event_start, _, event_id in events:
                if previous_event_datetime in event_start:
                    return event_id

            return None

        except Exception as e:
            print(f"Error buscando el evento en el calendario: {e}")
            return None

    def change_event(self, new_event_date: str, duration: str, event_id: str, user: aiservUser) -> None:
        """
        Cambia la hora de un evento existente en el calendario del usuario.

        Args:
            extracted_data: Datos que contienen la nueva fecha y duración.
            event_id: ID del evento a modificar.
            user: Objeto del usuario, se usa para obtener configuraciones por defecto.
        """
        try:
            
            new_start: datetime = datetime.fromisoformat(new_event_date)
            duration: timedelta = self._parse_duration(duration, user.email)
            new_end: datetime = new_start + duration

            updated_event_body: Dict[str, Any] = {
                'start': {'dateTime': new_start.isoformat(), 'timeZone': 'UTC'},
                'end': {'dateTime': new_end.isoformat(), 'timeZone': 'UTC'},
            }

            updated_event: Dict[str, Any] = self.calendar_service.events().patch(
                calendarId='primary',
                eventId=event_id,
                body=updated_event_body,
                sendUpdates='all'
            ).execute()

            print(f"Hora del evento actualizada: {updated_event.get('htmlLink')}")

        except Exception as e:
            print(f"Error al cambiar la hora del evento: {e}")

    def cancel_event(self, event_id: str) -> None:
        """
        Cancela un evento en el calendario del usuario.

        Args:
            event_id: ID del evento a cancelar.
        """
        try:
            self.calendar_service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()

            print("Evento cancelado exitosamente.")

        except Exception as e:
            print(f"Error cancelando el evento: {e}")

    def _insert_event_in_calendar(self, event: Dict[str, Any]) -> None:
        """
        Inserta un evento en el calendario usando el servicio de Google Calendar.

        Args:
            event: Diccionario con los detalles del evento.
        """
        try:
            event_result: Dict[str, Any] = self.calendar_service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all',
                sendNotifications=True
            ).execute()

            print(f"Event created: {event_result.get('htmlLink')}")
        except Exception as e:
            print(f"Error inserting event: {e}")

    def _parse_duration(self, duration_str: Optional[str], user_email: str) -> timedelta:
        """
        Parsea la duración del evento a partir de un string.

        Args:
            duration_str: Cadena que indica la duración (por ejemplo, "1 hora", "30 minutos").
            user_email: Email del usuario para obtener la duración por defecto si no se especifica.

        Returns:
            timedelta: Duración del evento.
        """
        if duration_str:
            try:
                if 'hora' in duration_str:
                    hours: int = int(duration_str.split()[0])
                    return timedelta(hours=hours)
                elif 'minuto' in duration_str:
                    minutes: int = int(duration_str.split()[0])
                    return timedelta(minutes=minutes)
            except Exception:
                print("Error parsing duration, defaulting to 60 minutes.")
            return timedelta(minutes=60)
        else:
            return self._get_default_duration(user_email)

    def _get_default_duration(self, user_email: str) -> timedelta:
        """
        Obtiene la duración por defecto del evento desde la configuración del usuario.

        Args:
            user_email: Email del usuario.

        Returns:
            timedelta: Duración por defecto.
        """
        try:
            event_config = EventConfig.objects.get(gmail=user_email)
            default_minutes: int = event_config.meeting_duration if event_config.meeting_duration else 60
            return timedelta(minutes=default_minutes)
        except Exception as e:
            print(f"Error fetching default duration from EventConfig: {e}")
            return timedelta(minutes=60)
