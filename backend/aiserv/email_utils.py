from datetime import datetime, timezone, timedelta
from django.utils.timezone import now, timedelta

import json
import logging
import base64
import re
from dateutil import tz
from jinja2 import Template
import pytz


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .models import StartConfig, ScheduleConfig, PriorityConfig, EventConfig, PromptData,PromptResponse, HistoryConfig, NotificationConfig
from .utils import flow_notification_to_front
from .text_feeling import analizar_texto

from .calendar_utils import generate_event, fetch_events ,change_event,cancel_event,find_event_in_calendar

import time
from django.db import close_old_connections
from .models import aiservUser
from .auth_utils import check_existing_tokens, initialize_services

import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"), 
)
logger = logging.getLogger(__name__)
TZ_MADRID = tz.gettz("Europe/Madrid") 

def main(user_id):
    """
    Main function that manages the periodic email check cycle and automatic response generation.
    Args:
        user_id (int): The ID of the user whose email activity will be periodically checked.
    """

    try:
        # Obtenemos al usuario de la base de datos
        user = aiservUser.objects.get(id=user_id)

        # Verificamos y refrescamos las credenciales del usuario
        credentials = check_existing_tokens(user)
        if not credentials:
            logger.error(f"No se pudieron obtener o actualizar las credenciales para {user.email}.")
            return

        # Inicializamos los servicios de Gmail y Google Calendar
        gmail_service, calendar_service, oauth_service = initialize_services(credentials)

        # Obtener los IDs de las etiquetas
        label_ids = id_labels(gmail_service)
        if not label_ids:
            logger.error(f"No se pudieron obtener los IDs de las etiquetas para {user.email}.")
            return

        # Asignar los IDs de etiquetas obtenidos
        label_superior_id = label_ids.get('superior', None)
        label_companero_id = label_ids.get('compañero', None)
        label_clientes_importante_id = label_ids.get('cliente importante', None)
        label_nuevos_clientes_id = label_ids.get('nuevo cliente', None)

        while True:
            # Cerramos conexiones antiguas para evitar problemas en hilos de larga duración
            close_old_connections()

            # Actualizamos solo el estado del usuario sin volver a obtener credenciales o servicios
            user.refresh_from_db()

            # Si `is_active_auto` es False, detenemos el bucle
            if not user.is_active_auto:
                logger.info(f"El usuario {user.email} ha desactivado la autogestión. Deteniendo verificación.")
                break

            # Procesamos los correos solo si los servicios fueron correctamente inicializados
            if gmail_service and calendar_service:
                try:
                    logger.info(f"Procesando correos para {user.email}")

                    # Leer correos no leídos

                    # Inicializamos la variable 'messages' como una lista vacía
                    messages = []

                    if label_superior_id:
                        messages += read_email_with_label(label_superior_id, gmail_service, label_name="superior")

                    if not messages and label_companero_id:
                        messages += read_email_with_label(label_companero_id, gmail_service, label_name="compañero")

                    if not messages and label_clientes_importante_id:
                        messages += read_email_with_label(label_clientes_importante_id, gmail_service, label_name="cliente importante")

                    if not messages and label_nuevos_clientes_id:
                        messages += read_email_with_label(label_nuevos_clientes_id, gmail_service, label_name="nuevo cliente")


                    # Si no hay correos etiquetados, leer los correos sin etiqueta
                    if not messages:
                        messages += read_email_without_label(gmail_service)

                    if not messages:
                        logger.info("No se encontraron correos sin leer.")
                        time.sleep(60)
                        continue

                    # Procesar cada correo
                    for entry in messages:
                        msg = entry.get("message")
                        label = entry.get("label")

                        if not msg:
                            logger.warning(f"Entrada sin 'message': {entry}")
                            continue


                        email_data = process_email(msg, gmail_service)

                        if email_data:
                            # Extraer datos del cuerpo del correo
                            extracted_data = extract_email_data(
                                email_data["Body"],
                                email_data["previous_messages"],
                                email_data["sent_dates"],
                                email_data["Subject"],
                                user,
                                calendar_service
                            )

                            # Clasificar el tipo de correo
                            classify_email(email_data, extracted_data, user, gmail_service, calendar_service,label)

                except Exception as e:
                    logger.error(f"Error procesando correos para {user.email}: {str(e)}")
            else:
                logger.error(f"Error: No se pudieron inicializar los servicios de Gmail o Calendar para {user.email}")

            # Esperamos 30 minutos antes de volver a comprobar
            time.sleep(60)

    except Exception as e:
        logger.error(f"Error en la función main: {str(e)}")


def id_labels(gmail_service):
    """
    Retrieves the IDs of available Gmail labels for a specific user.
    Args:
        gmail_service: Initialized Gmail API service.
    Returns:
        dict: A dictionary with label names and their corresponding IDs.
    """

    try:
        # Llamada a la API para listar las etiquetas
        labels = gmail_service.users().labels().list(userId='me').execute()

        # Creamos un diccionario para almacenar los IDs de las etiquetas
        label_ids = {}
        for label in labels['labels']:
            label_ids[label['name']] = label['id']

        logger.info(f"Etiquetas disponibles: {label_ids}")
        return label_ids

    except Exception as e:
        logger.error(f"Error al obtener las etiquetas: {e}")
        return {}

    
def read_email_with_label(label_id, gmail_service, label_name=None, num_messages=100):
    """
    Reads unread emails with a specific label from the user's Gmail account,
    limited to the last N days.
    """
    try:
        cutoff_date = (datetime.now() - timedelta(days=5)).strftime('%Y/%m/%d')
        query = f'is:unread after:{cutoff_date}'

        result = gmail_service.users().messages().list(
            userId='me',
            q=query,
            labelIds=[label_id],
            maxResults=num_messages
        ).execute()

        messages = result.get("messages", [])

        return [{"message": msg, "label": label_name} for msg in messages]

    except Exception as e:
        logger.error(f"Error al recuperar mensajes con la etiqueta {label_name or label_id}: {e}")
        return []



def read_email_without_label(gmail_service, num_messages=100):
    """
    Reads unread emails from the user's Gmail inbox (in:inbox),
    limited to the last N days.
    """
    try:
        logger.info("Buscando correos sin etiqueta en la bandeja de entrada")

        cutoff_date = (datetime.now() - timedelta(days=5)).strftime('%Y/%m/%d')
        query = f'is:unread in:inbox after:{cutoff_date}'

        result = gmail_service.users().messages().list(
            userId='me',
            q=query,
            maxResults=num_messages
        ).execute()

        messages = result.get("messages", [])

        return [{"message": msg, "label": None} for msg in messages]

    except Exception as e:
        logger.error(f"Error al recuperar mensajes de la bandeja de entrada: {e}")
        return []



def mark_as_read(gmail_service, message_id):
    """
    Marks an email as read.
    Args:
        gmail_service: Gmail API service.
        message_id: ID of the message.
    """

    try:
        gmail_service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
    except Exception as e:
        logger.error(f"Error al marcar como leído: {e}")


def process_email(message, gmail_service):
    """
    Processes each email, extracts necessary information, generates a response, 
    and interacts with the Google Calendar based on the email content.
    """
    try:
        # Obtenemos los datos completos del correo desde la API de Gmail
        email_data = gmail_service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        headers = email_data.get('payload', {}).get('headers', [])
        subject = "Sin asunto"
        sender = "Desconocido"
        body = "Sin contenido"
        previous_messages = ""  # Almacenaremos aquí los mensajes anteriores
        message_id = None  # Para almacenar el Message-ID
        thread_id = email_data.get('threadId')  # Obtenemos el threadId para el hilo del correo
        sent_dates = []  # Lista para almacenar las fechas de cada correo en el hilo

        # Extraemos los encabezados de asunto, remitente y Message-ID
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value'].strip() if header['value'] else 'Sin asunto'
            if header['name'] == 'From':
                sender = header['value']
            if header['name'] == 'Message-ID':  # Extraemos el Message-ID
                message_id = header['value']
            if header['name'] == 'Date':
                sent_date = header.get('value')
                if sent_date:
                    sent_dates.append(sent_date)

        # Extraer todos los mensajes del hilo si existe un threadId
        if thread_id:
            thread = gmail_service.users().threads().get(userId='me', id=thread_id).execute()
            messages_in_thread = thread.get('messages', [])

            # Extraer las fechas de todos los mensajes del hilo
            for msg in messages_in_thread:
                msg_headers = msg.get('payload', {}).get('headers', [])
                for header in msg_headers:
                    if header['name'] == 'Date':
                        date_in_thread = header.get('value')
                        if date_in_thread:
                            sent_dates.append(date_in_thread)

        # Ordenar las fechas antes de usarlas
        if sent_dates:
            # Convertir las fechas a objetos datetime, ordenarlas y volverlas a formato string
            date_format = "%a, %d %b %Y %H:%M:%S %z"
            sorted_dates = sorted([datetime.strptime(date, date_format) for date in sent_dates])
            sent_dates = [date.strftime(date_format) for date in sorted_dates]

        # Extraemos el cuerpo del correo
        if 'parts' in email_data['payload']:
            for part in email_data['payload']['parts']:
                if part['mimeType'] in ['text/plain', 'text/html']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'data' in email_data['payload']['body']:
            body = base64.urlsafe_b64decode(email_data['payload']['body']['data']).decode('utf-8')

        # Si no hay contenido en el cuerpo, lo indicamos
        if not body.strip():
            logger.error(f"El correo de {sender} no tiene cuerpo.")
            return None

        # Si el correo es parte de un hilo, extraemos los correos anteriores (historial)
        if 'parts' in email_data['payload']:
            for part in email_data['payload']['parts']:
                if part['mimeType'] == 'text/html':  # O 'text/plain', dependiendo del formato
                    previous_messages += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

        # Creamos un diccionario con los datos del correo, incluyendo threadId y Message-ID
        return {
            "Sender": sender,
            "Subject": subject,
            "Body": body,
            "previous_messages": previous_messages,
            "id": message['id'],
            "threadId": thread_id, 
            "Message-ID": message_id,
            "sent_dates": sent_dates  # Pasamos las fechas ordenadas
        }
    
    

    except Exception as e:
        logger.error(f"Error procesando el correo: {e}")
        return None



def extract_email_data(body, previous_messages, sent_date, subject, user,calendar_service):
    """
    Extracts event-related data from the email body for generating events in Google Calendar.

    Args:
        body (str): The body of the email.
        previous_messages (str): Previous email messages in a thread, if any.
        sent_date (list of str): Dates when the email was sent.
        subject (str): Subject of the email.
        user (str): Email or identifier of the user.

    Returns:
        dict: Parsed email data in JSON format (date, participants, location, etc.).
    """
    try:

        # Definir la zona horaria de Europa/Madrid
        tz = pytz.timezone('Europe/Madrid')

        # Convertir la fecha y hora actuales a una cadena ISO
        date_hour = datetime.now(tz).isoformat()

        # Convertir lista de fechas de envío a una cadena
        sent_dates_str = ', '.join(sent_date)

        # Obtener los datos del modelo PromptData
        promptData = PromptData.objects.get()

        events = fetch_events(calendar_service)

        logger.info(f"EVENTOS: {events}")

        # Convertir a objeto datetime (por si necesitas asegurarte)
        date_obj = datetime.fromisoformat(date_hour)

        # Obtener el día de la semana en español
        day = date_obj.strftime('%A') 

        logger.info(f"Dia: {day}")


        # Crear el contexto base para el template de Jinja
        base_context = {
            "subject": subject,
            "body": body,
            "date_hour": date_hour,
            "sent_dates_str": sent_dates_str,
            "previous_messages": previous_messages,
            "user": user,
            "events": events,
            "day": day
        }

        # Campos a procesar como templates en `PromptData`
        template_fields = [
            "start", "date", "change_date", "place", "participants", 
            "email_type", "link", "attachments", "details", "duration", "previousMessages"
        ]

        # Procesar cada campo de `PromptData` como un template
        rendered_fields = {}
        for field in template_fields:
            field_value = getattr(promptData, field, "")
            if field_value:  # Solo procesar si el campo no está vacío
                field_template = Template(field_value)
                rendered_fields[field] = field_template.render(base_context)
            else:
                rendered_fields[field] = ""  # Campo vacío en el caso de que no haya datos

        # Unir `base_context` con los campos renderizados
        context = {**base_context, **rendered_fields}

        # Leer el template principal desde el archivo
        prompt_data = os.getenv('PROMPT_DATA')
        with open(prompt_data, 'r') as file:
            template_content = file.read()

        # Renderizar el contenido del archivo usando Jinja con el contexto completo
        template = Template(template_content)
        promptAI = template.render(context)

        # print('DATA =', promptAI)

        # Llamada a OpenAI
        # response = client.chat.completions.create(
        #     model="gpt-4",
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": promptAI
        #         }
        #     ]
        # )

        response = client.chat.completions.create(
            model="o4-mini-2025-04-16",
            messages=[{"role":"user", "content": promptAI}],
            response_format={"type": "json_object"}
        )

        logger.info(f"DATA: {response}")


        if response and response.choices:
            json_response = response.choices[0].message.content

            if isinstance(json_response, dict):
                event_data = json_response
            else:
                event_data = json.loads(json_response)
        else:
            raise ValueError("No se pudo obtener una respuesta válida de OpenAI.")

        logger.info("Datos del correo:", event_data)
        return event_data

    except Exception as e:
        logger.error(f"Error extrayendo datos: {e}")
        return None
    

def classify_email(email_data, extracted_data, user, gmail_service, calendar_service,label):
    """
    Classifies the type of email and follows the corresponding workflow according to the type of event.
    Args:
        data: Extracted email body data.
        user: The user receiving the email.
        gmail_service: Gmail API service.
        calendar_service: Google Calendar API service to handle events.
    """
    try:
        email_type = extracted_data.get('email_type')
        user_data = aiservUser.objects.get(id=user.id)

        mark_as_read(gmail_service, email_data['id'])

        gmail = user_data.email
        body = email_data.get('Body', '')
        subject = email_data.get('Subject', '')
        sender = extract_email(email_data.get("Sender", ""))


        logger.info(f"\n\n  {email_data}  \n\n")

        if email_type in ['new_event', '<new_event>']:
            logger.info("Nuevo evento detectado.")

            availability = (
                check_availability(user, extracted_data, calendar_service)
                if extracted_data and 'date' in extracted_data else False
            )

            response = generate_response(user, extracted_data, availability, calendar_service, email_data, email_type)

            if response:
                try:
                    send_email_response(email_data, response, gmail_service, user)
                except Exception as e:
                    logger.error(e)

                summary = ' '.join(body.split()[:15])

                HistoryConfig.objects.create(
                    gmail=gmail,
                    sender=sender,
                    subject=subject,
                    summary=summary,
                    sent_date=now(),
                    expire_date=now() + timedelta(days=5)
                )

                flow_notification_to_front(
                    gmail=gmail,
                    sender=sender,
                    subject=subject,
                    body=body,
                    type="new_event",
                    label=label
                )
            else:
                logger.error("Error: La respuesta generada no es válida.")

        elif email_type in ['meeting_invitation', '<meeting_invitation>']:
            logger.info("Invitación a evento detectada.")

            availability = (
                check_availability(user, extracted_data, calendar_service)
                if extracted_data and 'date' in extracted_data else False
            )

            response = generate_response(user, extracted_data, availability, calendar_service, email_data, email_type)

            if response:
                try:
                    send_email_response(email_data, response, gmail_service, user)
                except Exception as e:
                    logger.error(e)

                flow_notification_to_front(
                    gmail=gmail,
                    sender=sender,
                    subject=subject,
                    body=body,
                    type="meeting_invitation",
                    label=label
                )
            else:
                logger.error("Error: La respuesta generada no es válida.")

        elif email_type in ['change_event', '<change_event>']:
            logger.info("Cambio de evento solicitado.")

            solicitante = sender
            event_id = find_event_in_calendar(extracted_data, calendar_service)

            if not event_id:
                logger.error("Evento no encontrado.")
                return
            
            try:

                event_details = calendar_service.events().get(calendarId='primary', eventId=event_id).execute()
                participants = [att['email'] for att in event_details.get('attendees', [])]

                if solicitante in participants:
                    availability = check_availability(user, extracted_data, calendar_service)
                    if availability:
                        logger.info("Cambiando el evento en el calendario.")
                        try:
                            change_event(extracted_data, calendar_service, event_id, user)
                        except Exception as e:
                            logger.error(f"Error en change event: {e}")

                        flow_notification_to_front(
                            gmail=gmail,
                            sender=sender,
                            subject=subject,
                            body=body,
                            type="change_event",
                            label=label
                        )
                    else:
                        logger.error("No hay disponibilidad para realizar el cambio.")
                else:
                    logger.error("El solicitante no está autorizado para cambiar el evento.")
            except Exception as e:
                logger.error(f"Error cambiando el evento {e}")

        elif email_type in ['cancel_event', '<cancel_event>']:
            logger.info("Solicitud de cancelación de evento.")

            solicitante = sender
            event_id = find_event_in_calendar(extracted_data, calendar_service)

            if not event_id:
                logger.error("Evento no encontrado.")
                return

            event_details = calendar_service.events().get(calendarId='primary', eventId=event_id).execute()
            participants = [att['email'] for att in event_details.get('attendees', [])]

            if solicitante in participants:
                try:
                    cancel_event(calendar_service, event_id)
                    logger.info("Evento cancelado.")
                except Exception as e:
                    logger.error(e)

                flow_notification_to_front(
                    gmail=gmail,
                    sender=sender,
                    subject=subject,
                    body=body,
                    type="cancel_event",
                    label=label
                )
            else:
                logger.error("El solicitante no está autorizado para cancelar el evento.")

        elif email_type in ['doubt', '<doubt>']:
            logger.info("El correo contiene una duda.")

            flow_notification_to_front(
                gmail=gmail,
                sender=sender,
                subject=subject,
                body=body,
                type="doubt",
                label=label
            )

        elif email_type in ['confirm_event', '<confirm_event>']:
            logger.info("Confirmación de evento recibida.")

            flow_notification_to_front(
                gmail=gmail,
                sender=sender,
                subject=subject,
                body=body,
                type="confirm_event",
                label=label
            )

        elif email_type in ['decline_event', '<decline_event>']:
            logger.info("Rechazo de evento recibido.")

            event_id = find_event_in_calendar(extracted_data, calendar_service)

            if not event_id:
                logger.error("Evento no encontrado.")
                return

            try:
                cancel_event(calendar_service, event_id)
                logger.info("Evento cancelado.")
            except Exception as e:
                logger.error(e)

            flow_notification_to_front(
                gmail=gmail,
                sender=sender,
                subject=subject,
                body=body,
                type="decline_event",
                label=label
            )

        else:
            logger.info("Tipo de correo no identificado.")

    except Exception as e:
        logger.error(f"Error en la clasificación del correo: {e}")
    


def check_availability(user, data, calendar_service) -> bool:
    """
    Devuelve True si el intervalo propuesto no se solapa con ningún evento
    (teniendo en cuenta la tolerancia), False en caso contrario.
    """
    try:
        tolerance = ScheduleConfig.objects.get(gmail=user.email).tolerance or 0

        logger.info(f"TOLERANCE: {tolerance}")

        proposed_start = datetime.fromisoformat(
            data.get("new_date") or data.get("date")
        )
        if proposed_start.tzinfo is None:             
            proposed_start = proposed_start.replace(tzinfo=TZ_MADRID)

        dur_raw = data.get("duration", "").lower()
        if "hora" in dur_raw:
            dur = timedelta(hours=int(__import__("re").findall(r"\d+", dur_raw)[0]))
        elif "minuto" in dur_raw:
            dur = timedelta(minutes=int(__import__("re").findall(r"\d+", dur_raw)[0]))
        elif dur_raw.isdigit():
            dur = timedelta(minutes=int(dur_raw))
        else:
            dur = timedelta(minutes=30)            

        proposed_end = proposed_start + dur

        for ev in fetch_events(calendar_service):
            raw_start = ev["start"]
            raw_end   = ev["end"]

            if len(raw_start) == 10:               
                ev_start = datetime.fromisoformat(raw_start).replace(tzinfo=TZ_MADRID)
                ev_end   = ev_start + timedelta(days=1) - timedelta(seconds=1)
            else:
                ev_start = datetime.fromisoformat(raw_start)
                ev_end   = datetime.fromisoformat(raw_end)

            ev_end_with_tol = ev_end + timedelta(minutes=tolerance)

            # solapamiento
            if proposed_start < ev_end_with_tol and proposed_end > ev_start:
                return False

        return True

    except Exception:
        logger.exception("Error comprobando la disponibilidad")
        return False    



def generate_response(user, extracted_data, availability, calendar_service,email_data,email_type):

    """
    Generates an automated email response based on the email content and the user's configuration.

    Args:
        user: The user instance for which the response is being generated.
        email_data: A dictionary containing the sender, subject, and body of the email.
        availability: A boolean indicating if the user is available for the requested time.
        calendar_service: Initialized Google Calendar API service.

    Returns:
        str: The generated response to be sent.
    """
    try:
        gmail = user.email

        # Obtener las configuraciones del usuario desde la base de datos
        start_config, _ = StartConfig.objects.get_or_create(gmail=gmail)
        schedule_config, _ = ScheduleConfig.objects.get_or_create(gmail=gmail)
        priority_config, _ = PriorityConfig.objects.get_or_create(gmail=gmail)
        event_config, _ = EventConfig.objects.get_or_create(gmail=gmail)

        # Recoger los datos de configuración desde la base de datos
        config_data = {
            'start_config': {
                'full_name': start_config.full_name,
                'charge': start_config.charge,
                'language': start_config.language,
                'details': start_config.details,
            },
            'schedule_config': {
                'work_hours_from': schedule_config.work_hours_from,
                'work_hours_to': schedule_config.work_hours_to,
                'no_meetings_hours_from': schedule_config.no_meetings_hours_from,
                'no_meetings_hours_to': schedule_config.no_meetings_hours_to,
                'no_meetings_days': schedule_config.no_meetings_days,
                'tolerance': schedule_config.tolerance,
            },
            'priority_config': {
                'priority_issues': priority_config.priority_issues,
                'priority_people': priority_config.priority_people,
                'priority_hours_from': priority_config.priority_hours_from,
                'priority_hours_to': priority_config.priority_hours_to,
                'priority_days': priority_config.priority_days,
            },
            'event_config': {
                'meeting_duration': event_config.meeting_duration,
                'notify_meeting': event_config.notify_meeting,
                'propose_meeting': event_config.propose_meeting,
                'meeting_limit': event_config.meeting_limit,
            }
        }


        sender = email_data["Sender"]
        subject = email_data["Subject"]
        body = email_data["Body"]

        # Análisis de emociones
        emocion = analizar_texto(body)

        # Asegurarse de que 'emocion' es un diccionario y obtener la clave principal
        if isinstance(emocion, dict):
            # Ordenar las emociones por el valor más alto
            emociones_ordenadas = sorted(emocion.items(), key=lambda x: x[1], reverse=True)
            
            # Obtener las tres emociones principales (si hay más de una)
            emocion_principal_1 = emociones_ordenadas[0]  # Primera emoción (principal)
            emocion_principal_2 = emociones_ordenadas[1] if len(emociones_ordenadas) > 1 else None
            emocion_principal_3 = emociones_ordenadas[2] if len(emociones_ordenadas) > 2 else None
        else:
            raise ValueError("Error en el formato de las emociones detectadas.")

        emociones_diccionario = {
            'anger': {
                'interpretacion': 'El remitente está enfadado o molesto.',
                'respuesta': 'Responde con calma, reconoce las preocupaciones de la persona y ofrece soluciones o disculpas si es necesario.'
            },
            'anticipation': {
                'interpretacion': 'El remitente está esperando algo o tiene expectativas.',
                'respuesta': 'Reconoce las expectativas y proporciona claridad sobre los próximos pasos o el resultado esperado.'
            },
            'disgust': {
                'interpretacion': 'El remitente está disgustado o tiene aversión hacia algo.',
                'respuesta': 'Responde con respeto, reconoce el disgusto y trata de ofrecer una solución o alternativa.'
            },
            'fear': {
                'interpretacion': 'El remitente tiene miedo o está preocupado.',
                'respuesta': 'Responde con empatía, ofreciendo garantías y clarificando cualquier incertidumbre.'
            },
            'joy': {
                'interpretacion': 'El remitente está feliz o celebrando algo.',
                'respuesta': 'Responde con entusiasmo, comparte la alegría y refuerza la relación con una respuesta positiva.'
            },
            'sadness': {
                'interpretacion': 'El remitente está triste o abatido.',
                'respuesta': 'Responde con empatía, mostrando apoyo y ofreciendo consuelo si es posible.'
            },
            'surprise': {
                'interpretacion': 'El remitente está sorprendido, ya sea positivamente o negativamente.',
                'respuesta': 'Si es una sorpresa positiva, comparte la emoción. Si es negativa, ofrece una explicación o soluciones.'
            },
            'trust': {
                'interpretacion': 'El remitente tiene confianza en ti o en la situación.',
                'respuesta': 'Confirma y refuerza la confianza, asegurando que cumplirás con lo esperado.'
            },
            'positive': {
                'interpretacion': 'El remitente tiene una actitud positiva o optimista.',
                'respuesta': 'Refuerza la positividad, mantén una actitud alegre y agradece cualquier gesto positivo.'
            },
            'negative': {
                'interpretacion': 'El remitente tiene una actitud negativa o pesimista.',
                'respuesta': 'Responde con empatía, mostrando disposición para mejorar la situación o solucionar problemas.'
            }
        }

        
        previous_messages = email_data["previous_messages"]

        promptResponse = PromptResponse.objects.get()

        # Crear el contexto base
        base_context = {
            "sender": sender,
            "subject": subject,
            "body": body,
            "availability": availability,
            "emocion_principal_1": emocion_principal_1,
            "emociones_diccionario": emociones_diccionario,
            "emocion_principal_2": emocion_principal_2,
            "emocion_principal_3": emocion_principal_3,
            "previous_messages": previous_messages,
            "config_data": config_data
        }

        # Campos a procesar como templates en `PromptResponse`
        template_fields = [
            "start", "email", "availability_yes", "availability_no", "instructions",
            "emotion1", "emotion2", "emotion3", "previousMessages", "full_name", 
            "charge", "language", "details", "work_hour", "decline_event_hour",
            "decline_event_day", "priority_people", "priority_issues", 
            "duration_event", "max_events"
        ]

        # Procesar cada campo de `PromptResponse` como un template
        rendered_fields = {}
        for field in template_fields:
            field_value = getattr(promptResponse, field, "")
            if field_value:  # Solo procesar si el campo no está vacío
                field_template = Template(field_value)
                rendered_fields[field] = field_template.render(base_context)
            else:
                rendered_fields[field] = ""  # Campo vacío si no hay datos

        # Unir `base_context` con los campos renderizados
        context = {**base_context, **rendered_fields}

        # Leer el template principal desde el archivo
        prompt_response = os.getenv('PROMPT_RESPONSE')
        with open(prompt_response, 'r') as file:
            template_content = file.read()

        # Renderizar el contenido del archivo usando Jinja con el contexto completo
        template = Template(template_content)
        promptAI = template.render(context)


        # Llamada a OpenAI para generar la respuesta
        response = client.chat.completions.create(
            model="o4-mini-2025-04-16",
            messages=[
                {
                    "role": "user",
                    "content": promptAI
                }
            ]
        )

        if response and response.choices:
            generated_response = response.choices[0].message.content

            if email_type == 'new_event':

                # Crear el evento en el calendario si el usuario está disponible
                if availability == True:
                    generate_event(extracted_data, email_data["Sender"], email_data["Subject"], calendar_service, user,email_type)

                return generated_response
            
            if email_type == 'meeting_invitation':

                # Crear el evento en el calendario si el usuario está disponible
                if availability == True:
                    generate_event(extracted_data, email_data["Sender"], email_data["Subject"], calendar_service, user,email_type)

                return generated_response
            
            return generated_response

        return None

    except Exception as e:
        logger.error(f"Error detectado: {e}")
        return None
    



# Envía una respuesta de correo electrónico usando la API de Gmail
def extract_email(cadena):
    """
    Extracts an email address from a string in the format 'Name <email@example.com>'.
    If the string is already a simple email, it returns it as is.
    """

    patron_correo = r"<(.*?)>"  # Expresión regular para extraer el correo dentro de '<>'
    resultado = re.search(patron_correo, cadena)
    
    return resultado.group(1) if resultado else cadena

def validate_email(correo):
    """
    Validates if an email address is in the correct format.
    """

    patron_correo = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(patron_correo, correo) is not None

def html_response_format(response):
    """
    Converts the generated response content into a suitable HTML format.
    Uses <br> to maintain line breaks without adding extra spaces.
    """

    # Reemplazamos los saltos de línea por <br> para mantener el espaciado controlado
    html_response = response.replace("\n", "<br>")

    return f"""
    <html>
        <body>
            {html_response}
        </body>
    </html>
    """

def send_email_response(email_data, response, gmail_service, user):
    """
    Sends a response to an email, ensuring it follows the conversation thread.
    Args:
        email_data: Data from the received email, including sender, subject, and body.
        response: The body of the response to be sent.
        gmail_service: Gmail API service to send the email.
        user: The current user whose information will be used to send the response.
    """

    to = extract_email(email_data.get("Sender", ""))  # Extraer solo el correo electrónico del remitente
    from_email = user.email
    original_subject = email_data.get("Subject", "Sin asunto")

    # Validar que el correo del destinatario es correcto
    if not validate_email(to):
        logger.error(f"Error: Dirección de correo inválida '{to}'")
        return

    # El asunto debe coincidir exactamente con el original, añadiendo "Re:" si no está presente
    if not original_subject.lower().startswith("re:"):
        subject = f"Re: {original_subject}"
    else:
        subject = original_subject

    # Crear el mensaje MIME
    mime_message = MIMEMultipart('alternative')
    mime_message['Subject'] = subject
    mime_message['From'] = from_email
    mime_message['To'] = to

    # Obtener el 'Message-ID' del correo original y el threadId
    message_id = email_data.get("Message-ID")
    thread_id = email_data.get("threadId")

    # Si se encuentra el Message-ID, configuramos los encabezados para seguir el hilo
    if message_id:
        mime_message['In-Reply-To'] = message_id
        mime_message['References'] = message_id

    # Generar un nuevo `Message-ID` único para este mensaje
    mime_message['Message-ID'] = f"<{int(time.time())}@{user.email.split('@')[1]}>"

    # Convertir la respuesta en formato HTML adecuado
    html_body = html_response_format(response)

    # Adjuntar el cuerpo en texto plano y HTML al mensaje MIME
    mime_message.attach(MIMEText(response, 'plain'))  # Cuerpo de texto plano
    mime_message.attach(MIMEText(html_body, 'html'))  # Cuerpo en formato HTML

    # Codificar el mensaje MIME en base64 para enviarlo con la API de Gmail
    raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode('utf-8')

    # Verificar que tenemos un threadId para seguir el hilo en Gmail
    if not thread_id:
        logger.error("Error: No se encontró threadId para este correo.")
        return

    # Crear el cuerpo del mensaje para la API de Gmail, añadiendo `threadId` para asegurar el hilo en Gmail
    message_response = {
        'raw': raw_message,
        'threadId': thread_id  # Mantener el hilo en Gmail usando el threadId
    }

    try:
        # Enviar el correo a través de la API de Gmail, asegurándose de seguir el hilo
        gmail_service.users().messages().send(userId='me', body=message_response).execute()
        logger.info("Respuesta enviada exitosamente.\n")
    except Exception as e:
        logger.error(f"Error enviando respuesta: {e}")




# Función para validar la respuesta antes de enviarla
def validate_response(response):
    
    None


