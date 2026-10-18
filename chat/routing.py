from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<code>[0-9a-f]{8})/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chat-notify/$', consumers.NotificationConsumer.as_asgi()),
]
