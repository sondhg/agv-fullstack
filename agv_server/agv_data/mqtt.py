import paho.mqtt.client as mqtt
from django.conf import settings
import logging
from .agv_to_server_decoder import decode_message
from typing import Optional, Tuple

from .apply_main_algorithms.apply_main_algorithms import _update_agv_position, _get_agv_by_id, _apply_control_policy, _trigger_deadlock_partner_control_policy

MQTT_BROKER = settings.MQTT_BROKER
MQTT_PORT = settings.MQTT_PORT
MQTT_KEEPALIVE = settings.MQTT_KEEPALIVE
MQTT_USER = settings.MQTT_USER
MQTT_PASSWORD = settings.MQTT_PASSWORD

MQTT_TOPIC_AGVDATA = settings.MQTT_TOPIC_AGVDATA
MQTT_TOPIC_AGVROUTE = settings.MQTT_TOPIC_AGVROUTE
MQTT_TOPIC_AGVHELLO = settings.MQTT_TOPIC_AGVHELLO

logger = logging.getLogger(__name__)


def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully")
        client.subscribe(f"{MQTT_TOPIC_AGVDATA}/#")
    else:
        print('Bad connection. Code:', rc)


def _on_message(client, userdata, message):
    """
    Route incoming MQTT messages to appropriate handlers based on topic.
    """
    print(
        f'Received message on topic: {message.topic} with payload: {message.payload}')
    # Route message to appropriate handler based on topic prefix
    if message.topic.startswith(f"{MQTT_TOPIC_AGVDATA}/"):
        handle_agv_data_message(client, message)
    else:
        print(f"Received message on unhandled topic: {message.topic}")


def handle_agv_data_message(client, message):
    """
    Handle AGV data messages containing location updates.
    Processes AGV location update and applies DSPA control policy.

    Args:
        mqtt_client: MQTT client instance
        message: MQTT message object with payload containing AGV data
    """
    try:
        # Parse and validate message
        this_agv_data = _parse_agv_message(message.payload)
        if this_agv_data is None:
            logger.warning("Skipping invalid AGV message")
            return

        (this_agv_id, this_agv_current_node) = this_agv_data
        this_agv = _get_agv_by_id(this_agv_id)
        if not this_agv:
            return
        # Update AGV position and path information
        _update_agv_position(agv=this_agv, current_node=this_agv_current_node)

        # Apply DSPA control policy to determine next action
        _apply_control_policy(agv=this_agv)

        # Check if any other AGVs were waiting for this AGV due to deadlock resolution
        _trigger_deadlock_partner_control_policy(moved_agv_id=this_agv_id)

        logger.info(
            f"Updated AGV {this_agv_id} location to node {this_agv_current_node}")

    except Exception as e:
        logger.error(f"Unexpected error in AGV data handler: {str(e)}")


def _parse_agv_message(payload) -> Optional[Tuple[str, int]]:
    """Parse and validate AGV message payload."""
    try:
        decoded_data = decode_message(payload)
        agv_id = decoded_data.get('agv_id')
        current_node = decoded_data.get('current_node')

        if not agv_id or current_node is None:
            logger.error("Missing required fields in AGV data message")
            return None

        return agv_id, current_node
    except ValueError as e:
        logger.error(f"Failed to decode AGV data message: {str(e)}")
        return None


client = mqtt.Client()
client.on_connect = _on_connect
client.on_message = _on_message
client.username_pw_set(username=settings.MQTT_USER,
                       password=settings.MQTT_PASSWORD)
client.connect(
    host=settings.MQTT_BROKER,
    port=settings.MQTT_PORT,
    keepalive=settings.MQTT_KEEPALIVE
)
