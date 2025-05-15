from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/agv-consumer/$", consumers.AgvConsumer.as_asgi()),
]
