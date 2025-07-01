import os
import time
import json
import base64
import re
import pytz
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from django.utils.timezone import timedelta
from jinja2 import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from ..models import (
    StartConfig, ScheduleConfig, PriorityConfig, EventConfig, 
    PromptData, PromptResponse, aiservUser
)
from .calendar_utils import CalendarUtils
from openai import OpenAI

# Inicialización del cliente OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class EmailProcessor:
    """
    Clase que agrupa la lógica de procesamiento de correos:
    lectura, extracción de datos, clasificación, generación de respuesta y envío.
    """

    def __init__(self, user: aiservUser, gmail_service: Any) -> None:
        """
        Inicializa el procesador con el usuario y los servicios de Gmail y Calendar.

        Args:
            user (aiservUser): Usuario.
            gmail_service (Any): Servicio de Gmail.
            calendar_service (Any): Servicio de Google Calendar.
        """
        self.user = user
        self.gmail_service = gmail_service


    def get_label_ids(self) -> Dict[str, str]:
        """
        Recupera los IDs de las etiquetas disponibles en Gmail.

        Returns:
            Dict[str, str]: Diccionario con nombres e IDs de etiquetas.
        """
        try:
            labels = self.gmail_service.users().labels().list(userId='me').execute()
            label_ids = {label['name']: label['id'] for label in labels['labels']}
            print(f"Etiquetas disponibles: {label_ids}")
            return label_ids
        except Exception as e:
            print(f"Error al obtener etiquetas: {e}")
            return {}

    def read_emails_with_label(self, label_id: str, label_name: Optional[str] = None, num_messages: int = 100) -> List[Dict[str, Any]]:
        """
        Lee los correos no leídos que tienen una etiqueta específica.

        Args:
            label_id (str): ID de la etiqueta.
            label_name (Optional[str]): Nombre de la etiqueta.
            num_messages (int): Número máximo de mensajes.

        Returns:
            List[Dict[str, Any]]: Lista de mensajes con la etiqueta.
        """
        try:
            query = 'is:unread'
            result = self.gmail_service.users().messages().list(
                userId='me', q=query, labelIds=[label_id], maxResults=num_messages
            ).execute()
            messages = result.get("messages", [])
            return [{"message": msg, "label": label_name} for msg in messages]
        except Exception as e:
            print(f"Error al leer correos con etiqueta {label_name or label_id}: {e}")
            return []

    def read_emails_without_label(self, num_messages: int = 100) -> List[Dict[str, Any]]:
        """
        Lee los correos no leídos sin etiqueta (bandeja de entrada).

        Returns:
            List[Dict[str, Any]]: Lista de mensajes sin etiqueta.
        """
        try:
            print("Buscando correos sin etiqueta en la bandeja de entrada")
            query = 'is:unread in:inbox'
            result = self.gmail_service.users().messages().list(
                userId='me', q=query, maxResults=num_messages
            ).execute()
            messages = result.get("messages", [])
            return [{"message": msg} for msg in messages]
        except Exception as e:
            print(f"Error al leer correos sin etiqueta: {e}")
            return []
        
    def process_email(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Procesa un correo extrayendo headers, cuerpo, fechas y demás información.

        Args:
            message (Dict[str, Any]): Mensaje de Gmail.

        Returns:
            Optional[Dict[str, Any]]: Diccionario con datos del correo o None en error.
        """
        try:
            email_data = self.gmail_service.users().messages().get(
                userId='me', id=message['id'], format='full'
            ).execute()
            headers = email_data.get('payload', {}).get('headers', [])
            subject = "Sin asunto"
            sender = "Desconocido"
            body = "Sin contenido"
            previous_messages = ""
            message_id = None
            thread_id = email_data.get('threadId')
            sent_dates: List[str] = []

            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value'].strip() if header['value'] else 'Sin asunto'
                if header['name'] == 'From':
                    sender = header['value']
                if header['name'] == 'Message-ID':
                    message_id = header['value']
                if header['name'] == 'Date':
                    date_val = header.get('value')
                    if date_val:
                        sent_dates.append(date_val)

            if thread_id:
                thread = self.gmail_service.users().threads().get(userId='me', id=thread_id).execute()
                for msg in thread.get('messages', []):
                    for header in msg.get('payload', {}).get('headers', []):
                        if header['name'] == 'Date':
                            date_val = header.get('value')
                            if date_val:
                                sent_dates.append(date_val)

            if sent_dates:
                date_format = "%a, %d %b %Y %H:%M:%S %z"
                sorted_dates = sorted([datetime.strptime(date, date_format) for date in sent_dates])
                sent_dates = [date.strftime(date_format) for date in sorted_dates]

            # Extraer cuerpo del mensaje
            if 'parts' in email_data['payload']:
                for part in email_data['payload']['parts']:
                    if part['mimeType'] in ['text/plain', 'text/html']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            elif 'data' in email_data['payload']['body']:
                body = base64.urlsafe_b64decode(email_data['payload']['body']['data']).decode('utf-8')

            if not body.strip():
                print(f"El correo de {sender} no tiene cuerpo.")
                return None

            # Extraer mensajes previos si existen
            if 'parts' in email_data['payload']:
                for part in email_data['payload']['parts']:
                    if part['mimeType'] == 'text/html':
                        previous_messages += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

            return {
                "Sender": sender,
                "Subject": subject,
                "Body": body,
                "previous_messages": previous_messages,
                "id": message['id'],
                "threadId": thread_id,
                "Message-ID": message_id,
                "sent_dates": sent_dates
            }
        except Exception as e:
            print(f"Error procesando el correo: {e}")
            return None
        
    def mark_as_read(self,message_id):
        """
        Marks an email as read.
        Args:
            message_id: ID of the message.
        """

        try:
            self.gmail_service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
        except Exception as e:
            print(f"Error al marcar como leído: {e}")
        
    def _extract_email(self, cadena: str) -> str:
        """
        Extrae la dirección de correo de una cadena en formato "Nombre <correo@example.com>".

        Args:
            cadena (str): Cadena de entrada.

        Returns:
            str: Correo extraído.
        """
        patron_correo = r"<(.*?)>"
        resultado = re.search(patron_correo, cadena)
        return resultado.group(1) if resultado else cadena


class EmailTools:

    def __init__(self, user: aiservUser, gmail_service: Any, calendar_service: Any) -> None:
        """
        Inicializa el procesador con el usuario y los servicios de Gmail y Calendar.

        """
        self.user = user
        self.gmail_service = gmail_service
        self.calendar_service = calendar_service
        self.calendar_utils = CalendarUtils(self.calendar_service,self.user)
    
    def _check_availability(self, date: str) -> bool:
        """
        Verifica la disponibilidad del usuario comparando el evento propuesto con eventos existentes.

        Args:
            date: Fecha del evento en formato rfc3339

        Returns:
            bool: True si hay disponibilidad, False en caso contrario.
        """
        try:
            # Quitar comillas simples o dobles si las trae
            date = date.strip("'").strip('"')

            tolerance = ScheduleConfig.objects.get(gmail=self.user.email).tolerance or 0
            events = self.calendar_utils.fetch_events()
            proposed_start = datetime.fromisoformat(date)
            proposed_duration = timedelta(minutes=30)
            proposed_end = proposed_start + proposed_duration
            for event in events:
                event_start = datetime.fromisoformat(event[0])
                event_end = datetime.fromisoformat(event[1])
                if proposed_start < (event_end + timedelta(minutes=tolerance)) and proposed_end > event_start:
                    return False
            return True
        except Exception as e:
            print(f"Error verificando disponibilidad: {e}")
            return False


        
    
    def send_email_response(self, email_data: Dict[str, Any], response: str) -> None:
        """
        Envía una respuesta por correo electrónico siguiendo el hilo original.

        Args:
            email_data (Dict[str, Any]): Datos del correo original.
            response (str): Contenido de la respuesta.
        """
        to = self._extract_email(email_data.get("Sender", ""))
        from_email = self.user.email
        original_subject = email_data.get("Subject", "Sin asunto")
        if not self._validate_email(to):
            print(f"Error: Dirección de correo inválida '{to}'")
            return
        subject = f"Re: {original_subject}" if not original_subject.lower().startswith("re:") else original_subject

        mime_message = MIMEMultipart('alternative')
        mime_message['Subject'] = subject
        mime_message['From'] = from_email
        mime_message['To'] = to

        message_id = email_data.get("Message-ID")
        thread_id = email_data.get("threadId")
        if message_id:
            mime_message['In-Reply-To'] = message_id
            mime_message['References'] = message_id
        mime_message['Message-ID'] = f"<{int(time.time())}@{self.user.email.split('@')[1]}>"
        html_body = self._html_response_format(response)
        mime_message.attach(MIMEText(response, 'plain'))
        mime_message.attach(MIMEText(html_body, 'html'))
        raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode('utf-8')
        if not thread_id:
            print("Error: No se encontró threadId para este correo.")
            return
        message_response = {'raw': raw_message, 'threadId': thread_id}
        try:
            self.gmail_service.users().messages().send(userId='me', body=message_response).execute()
            print("Respuesta enviada exitosamente.\n")
        except Exception as e:
            print(f"Error enviando respuesta: {e}")
            
    def _extract_email(self, cadena: str) -> str:
        """
        Extrae la dirección de correo de una cadena en formato "Nombre <correo@example.com>".

        Args:
            cadena (str): Cadena de entrada.

        Returns:
            str: Correo extraído.
        """
        patron_correo = r"<(.*?)>"
        resultado = re.search(patron_correo, cadena)
        return resultado.group(1) if resultado else cadena

    def _validate_email(self, correo: str) -> bool:
        """
        Valida que una dirección de correo tenga el formato correcto.

        Args:
            correo (str): Dirección de correo.

        Returns:
            bool: True si es válida, False en caso contrario.
        """
        patron_correo = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        return re.match(patron_correo, correo) is not None

    def _html_response_format(self, response: str) -> str:
        """
        Convierte un texto de respuesta en formato HTML adecuado.

        Args:
            response (str): Texto de la respuesta.

        Returns:
            str: Texto en formato HTML.
        """
        html_response = response.replace("\n", "<br>")
        return f"""
        <html>
            <body>
                {html_response}
            </body>
        </html>
        """
    
