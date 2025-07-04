from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notificaciones", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notificaciones", self.channel_name)

    async def send_notification(self, event):
        value = event["value"]
        await self.send(text_data=json.dumps({
            "value": value
        }))
