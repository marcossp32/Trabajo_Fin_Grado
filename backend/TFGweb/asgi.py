import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import aiserv.routing  # Asegúrate de tener este archivo con las rutas WebSocket

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TFGweb.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Mantiene soporte para peticiones HTTP normales
    "websocket": AuthMiddlewareStack(
        URLRouter(
            aiserv.routing.websocket_urlpatterns  # Importa las rutas WebSocket
        )
    ),
})
    