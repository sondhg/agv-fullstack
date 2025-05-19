from django.apps import AppConfig


class AgvDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agv_data'

    def ready(self):
        """
        Initialize the application when Django is ready.
        Starts the MQTT client safely.
        """        # Only start MQTT client in the main process (not in reloader)
        import os
        if os.getenv('RUN_MAIN', None) != 'true':
            # Import and start MQTT client
            from . import django_mqtt
            django_mqtt.start_mqtt_client()
