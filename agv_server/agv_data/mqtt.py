import paho.mqtt.client as mqtt
from django.conf import settings
from typing import Optional, Tuple

from .models import Agv
from .encode_decode_data_frames.agv_to_server_decoder import decode_message
from .encode_decode_data_frames.server_to_agv_encoder import encode_message

from .apply_main_algorithms.apply_main_algorithms import (
    _update_agv_position,
    _get_agv_by_id,
    _apply_control_policy,
    _trigger_deadlock_partner_control_policy,
)

MQTT_TOPIC_AGVDATA = settings.MQTT_TOPIC_AGVDATA
MQTT_TOPIC_AGVROUTE = settings.MQTT_TOPIC_AGVROUTE
MQTT_TOPIC_AGVHELLO = settings.MQTT_TOPIC_AGVHELLO


def _on_connect(client: mqtt.Client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully")
        client.subscribe(f"{settings.MQTT_TOPIC_AGVDATA}/#")
    else:
        print("Bad connection. Code:", rc)


def _on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    """
    Route incoming MQTT messages to appropriate handlers based on topic.
    """
    print(f"Received message on topic: {message.topic} with payload: {message.payload}")
    # Route message to appropriate handler based on topic prefix
    topic_name = str(message.topic)
    if topic_name.startswith(f"{MQTT_TOPIC_AGVDATA}/"):
        # include decoding and processing logic
        handle_agv_data_message(client, message)
    else:
        print(f"Received message on unhandled topic: {message.topic}")


def handle_agv_data_message(client: mqtt.Client, message: mqtt.MQTTMessage) -> None:
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
            return

        (this_agv_id, this_agv_current_node) = this_agv_data
        this_agv = _get_agv_by_id(this_agv_id)
        if not this_agv:
            return
        # Update AGV position and path information
        # Apply DSPA control policy to determine next action
        _update_agv_position(agv=this_agv, current_node=this_agv_current_node)
        initially_affected_agvs = _apply_control_policy(agv=this_agv)

        # Check if any other AGVs were waiting for this AGV due to deadlock resolution
        # and collect them to send MQTT messages
        partner_agvs = _trigger_deadlock_partner_control_policy(
            moved_agv_id=this_agv_id
        )

        # Send MQTT message to the main AGV
        _send_mqtt_message_to_agv(client, this_agv)

        # Send MQTT messages to AGVs affected by initial deadlock resolution
        if initially_affected_agvs:
            for affected_agv in initially_affected_agvs:
                _send_mqtt_message_to_agv(client, affected_agv)

        # Send MQTT messages to any partner AGVs that were affected by deadlock resolution
        if partner_agvs:
            for partner_agv in partner_agvs:
                _send_mqtt_message_to_agv(client, partner_agv)

    except Exception:
        pass


def _parse_agv_message(payload) -> Optional[Tuple[int, int]]:
    """Parse and validate AGV message payload."""
    try:
        decoded_data = decode_message(payload)
        agv_id = decoded_data.get("agv_id")
        current_node = decoded_data.get("current_node")

        if not agv_id or current_node is None:
            return None

        return int(agv_id), int(current_node)
    except ValueError:
        return None


def _send_mqtt_message_to_agv(client: mqtt.Client, agv: Agv) -> None:
    """
    Send encoded MQTT message to a specific AGV.

    Args:
        client: MQTT client instance
        agv: AGV instance to send message to
    """
    try:
        encoded_message = encode_message(
            motion_state=agv.motion_state,
            reserved_node=agv.reserved_node,
            direction_change=agv.direction_change,
        )

        client.publish(
            topic=f"{MQTT_TOPIC_AGVROUTE}/{agv.agv_id}", payload=encoded_message, qos=2
        )

    except Exception:
        pass


client = mqtt.Client()
client.on_connect = _on_connect
client.on_message = _on_message
client.username_pw_set(username=settings.MQTT_USER, password=settings.MQTT_PASSWORD)
client.connect(
    host=settings.MQTT_BROKER,
    port=settings.MQTT_PORT,
    keepalive=settings.MQTT_KEEPALIVE,
)
