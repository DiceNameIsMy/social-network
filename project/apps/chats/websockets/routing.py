from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/', consumers.ChatConsumer.as_asgi()),
]