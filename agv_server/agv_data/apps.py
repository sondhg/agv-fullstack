from django.apps import AppConfig


class AgvDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agv_data'

    def ready(self):
        import os
        if os.getenv('RUN_MAIN'):
            # Import and start MQTT client only when app is ready
            from . import mqtt
            mqtt.client.loop_start()
