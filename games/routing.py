from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chess/(?P<code>[0-9a-f]{8})/$', consumers.ChessConsumer.as_asgi()),
    re_path(r'ws/xiangqi/(?P<code>[0-9a-f]{8})/$', consumers.XiangqiConsumer.as_asgi()),
    re_path(r'ws/go/(?P<code>[0-9a-f]{8})/$', consumers.GoConsumer.as_asgi()),
    re_path(r'ws/gomoku/(?P<code>[0-9a-f]{8})/$', consumers.GomokuConsumer.as_asgi()),
]
