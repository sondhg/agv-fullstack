import paho.mqtt.client as mqtt
from django.conf import settings


MQTT_BROKER = settings.MQTT_BROKER
MQTT_PORT = settings.MQTT_PORT
MQTT_KEEPALIVE = settings.MQTT_KEEPALIVE
MQTT_USER = settings.MQTT_USER
MQTT_PASSWORD = settings.MQTT_PASSWORD

MQTT_TOPIC_AGVDATA = settings.MQTT_TOPIC_AGVDATA
MQTT_TOPIC_AGVROUTE = settings.MQTT_TOPIC_AGVROUTE
MQTT_TOPIC_AGVHELLO = settings.MQTT_TOPIC_AGVHELLO


def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully")
        mqtt_client.subscribe(f"{MQTT_TOPIC_AGVDATA}/#")
    else:
        print('Bad connection. Code:', rc)


def on_message(mqtt_client, userdata, msg):
    """
    Route incoming MQTT messages to appropriate handlers based on topic.
    """
    print(
        f'Received message on topic: {msg.topic} with payload: {msg.payload}')
    # Route message to appropriate handler based on topic prefix
    if msg.topic.startswith(f"{MQTT_TOPIC_AGVDATA}/"):
        handle_agv_data_message(mqtt_client, msg)
    else:
        print(f"Received message on unhandled topic: {msg.topic}")


def handle_agv_data_message(mqtt_client, msg):
    pass


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
client.connect(
    host=settings.MQTT_BROKER,
    port=settings.MQTT_PORT,
    keepalive=settings.MQTT_KEEPALIVE
)
