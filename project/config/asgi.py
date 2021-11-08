import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Load apps
http_application = get_asgi_application()

# Import routing from
from apps.chats.websockets import routing as chat_routing


application = ProtocolTypeRouter({
    "http": http_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat_routing.websocket_urlpatterns
        )
    ),
})