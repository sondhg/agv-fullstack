"""
ASGI config for agv_server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agv_server.settings')

# ! Initialize Django ASGI application early to ensure the AppRegistry is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# ! Do not Shift+Alt+F to format this file, as it will break the import order. The line below must be imported after the line django_asgi_app = get_asgi_application()

from agv_data.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns)
})
