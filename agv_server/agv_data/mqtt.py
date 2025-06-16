import paho.mqtt.client as mqtt
from django.conf import settings
import json
import logging
from .agv_to_server_decoder import decode_message
from .models import Agv
from .services.algorithm2.algorithm2 import ControlPolicy
from .services.algorithm3.algorithm3 import DeadlockResolver
from .services.algorithm4.algorithm4 import BackupNodesAllocator

MQTT_BROKER = settings.MQTT_BROKER
MQTT_PORT = settings.MQTT_PORT
MQTT_KEEPALIVE = settings.MQTT_KEEPALIVE
MQTT_USER = settings.MQTT_USER
MQTT_PASSWORD = settings.MQTT_PASSWORD

MQTT_TOPIC_AGVDATA = settings.MQTT_TOPIC_AGVDATA
MQTT_TOPIC_AGVROUTE = settings.MQTT_TOPIC_AGVROUTE
MQTT_TOPIC_AGVHELLO = settings.MQTT_TOPIC_AGVHELLO

logger = logging.getLogger(__name__)


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
    """
    Handle AGV data messages containing location updates.
    Processes AGV location update and applies DSPA control policy.

    Args:
        mqtt_client: MQTT client instance
        msg: MQTT message object with payload containing AGV data
    """
    try:
        # Parse and validate message
        agv_data = _parse_agv_message(msg.payload)
        if not agv_data:
            return

        agv_id, current_node = agv_data
        agv = _get_agv_by_id(agv_id)
        if not agv:
            return        # Update AGV position and path information
        _update_agv_position(agv, current_node)

        # Apply DSPA control policy to determine next action
        _apply_control_policy(agv)

        # Check if any other AGVs were waiting for this AGV due to deadlock resolution
        _trigger_deadlock_partner_control_policy(agv_id)

        logger.info(f"Updated AGV {agv_id} location to node {current_node}")

    except Exception as e:
        logger.error(f"Unexpected error in AGV data handler: {str(e)}")


def _parse_agv_message(payload):
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


def _get_agv_by_id(agv_id):
    """Get AGV instance by ID."""
    try:
        return Agv.objects.get(agv_id=agv_id)
    except Agv.DoesNotExist:
        logger.error(f"AGV with ID {agv_id} not found in database")
        return None


def _update_agv_position(agv, current_node):
    """Update AGV's position and path information."""
    control_policy = ControlPolicy(agv)
    control_policy.update_position_info(current_node)


def _apply_control_policy(agv):
    """Apply DSPA control policy to determine AGV's next action."""
    control_policy = ControlPolicy(agv)

    # Check if AGV can move based on basic conditions
    if control_policy.can_move_freely():
        control_policy.set_moving_state()
        # Clear deadlock resolution state if it was set
        if agv.waiting_for_deadlock_resolution:
            deadlock_resolver = DeadlockResolver(agv)
            deadlock_resolver.clear_deadlock_resolution_state()
        return

    # Handle backup node scenarios
    if control_policy.should_use_backup_nodes():
        _handle_backup_node_scenario(agv)
        return

    # Handle waiting and deadlock scenarios
    _handle_waiting_scenario(agv)


def _trigger_deadlock_partner_control_policy(moved_agv_id):
    """
    When an AGV moves, check if any other AGVs were waiting for this AGV
    due to deadlock resolution, and trigger their control policy.
    """
    try:
        # Find AGVs that were waiting for this AGV due to deadlock resolution
        waiting_agvs = Agv.objects.filter(
            waiting_for_deadlock_resolution=True,
            deadlock_partner_agv_id=moved_agv_id,
            motion_state=Agv.WAITING
        )

        for waiting_agv in waiting_agvs:
            logger.info(f"Triggering control policy for AGV {waiting_agv.agv_id} "
                        f"after partner AGV {moved_agv_id} moved")
            _apply_control_policy(waiting_agv)

    except Exception as e:
        logger.error(
            f"Error triggering deadlock partner control policy: {str(e)}")


def _handle_backup_node_scenario(agv):
    """Handle scenarios involving backup nodes."""
    control_policy = ControlPolicy(agv)
    if agv.spare_flag:
        control_policy.cleanup_current_backup_node()
    else:
        backup_allocator = BackupNodesAllocator(agv)
        backup_allocator.allocate_backup_nodes()

    if control_policy.can_move_with_backup():
        control_policy.set_moving_with_backup_state()


def _handle_waiting_scenario(agv):
    """Handle waiting scenarios and potential deadlocks."""
    control_policy = ControlPolicy(agv)
    control_policy.set_waiting_state()

    deadlock_resolver = DeadlockResolver(agv)
    if deadlock_resolver.has_heading_on_deadlock():
        deadlock_resolver.resolve_heading_on_deadlock()
    elif deadlock_resolver.has_loop_deadlock():
        deadlock_resolver.resolve_loop_deadlock()
    else:
        deadlock_resolver.reserve_current_position()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
client.connect(
    host=settings.MQTT_BROKER,
    port=settings.MQTT_PORT,
    keepalive=settings.MQTT_KEEPALIVE
)
