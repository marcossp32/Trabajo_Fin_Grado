from .models import NotificationConfig
from django.utils.timezone import now
from datetime import timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

def put_notification(gmail, sender, subject, body, type, label):
    summary = ' '.join(body.split()[:15])  # Primeras 15 palabras

    logger.debug(f"Label recibido: {label}")
    try:
        NotificationConfig.objects.create(
            gmail=gmail,
            sender=sender,
            title=subject,
            body=summary,
            type=type,
            sent_date=now(),
            expire_date=now() + timedelta(days=5),
            read=False,
            label=label
        )
        logger.info(f"Notificación guardada en DB para {gmail}")
    except Exception as e:
        logger.error(f"Error al guardar notificación: {e}", exc_info=True)



def send_signal():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notificaciones", 
        {
            "type": "send_notification",
            "value": True  
        }
    )

def flow_notification_to_front(gmail, sender, subject, body,type,label):

    try:
        put_notification(gmail, sender, subject, body,type,label)
    except Exception as e:
        print(e)
        return e
    
    send_signal()