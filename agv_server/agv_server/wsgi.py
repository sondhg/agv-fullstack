"""
WSGI config for agv_server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from agv_data.services.mqtt_handler import init_mqtt_handler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agv_server.settings')

application = get_wsgi_application()

# Initialize MQTT handler when server starts
mqtt_handler = init_mqtt_handler()
