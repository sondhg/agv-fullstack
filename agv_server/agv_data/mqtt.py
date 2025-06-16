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
    Decodes message and updates AGV's current_node in the database.

    Args:
        mqtt_client: MQTT client instance
        msg: MQTT message object with payload containing AGV data
    """
    try:
        # Decode the message using the AGV-to-Server decoder
        decoded_data = decode_message(msg.payload)

        # Extract AGV ID and current node from decoded data
        agv_id = decoded_data.get('agv_id')
        current_node = decoded_data.get('current_node')

        if not agv_id or current_node is None:
            logger.error("Missing required fields in AGV data message")
            return

        # Find the AGV in the database
        try:
            agv = Agv.objects.get(agv_id=agv_id)

            # Create control policy and update AGV's travel information
            control_policy = ControlPolicy(agv=agv)
            control_policy.update_current_node_and_previous_node(
                current_node=current_node)
            control_policy.update_remaining_path(current_node=current_node)
            control_policy.update_next_node()
            control_policy.update_common_nodes(current_node=current_node)
            control_policy.update_adjacent_common_nodes(
                current_node=current_node)

            is_movement_condition_1_satisfied = control_policy.is_movement_condition_1_satisfied()
            is_movement_condition_2_satisfied = control_policy.is_movement_condition_2_satisfied()

            if is_movement_condition_1_satisfied or is_movement_condition_2_satisfied:
                control_policy._set_agv_moving_without_spare_flag_and_empty_backup_nodes()
            else:
                reserved_nodes_of_other_agvs = control_policy._get_reserved_nodes_of_other_agvs()
                if agv.next_node not in reserved_nodes_of_other_agvs:
                    spare_flag_of_this_agv = agv.spare_flag
                    if spare_flag_of_this_agv:
                        control_policy.remove_backup_node_associated_with_current_node()
                    else:
                        # Apply for backup nodes using Algorithm 4
                        backup_allocator = BackupNodesAllocator(agv=agv)
                        backup_allocator.apply_for_backup_nodes()
                    is_movement_condition_3_satisfied = control_policy.is_movement_condition_3_satisfied()
                    if is_movement_condition_3_satisfied:
                        control_policy._set_agv_moving_with_spare_flag()
                else:  # agv.next_node in reserved_nodes_of_other_agvs
                    is_none_of_three_conditions_satisfied = control_policy.is_none_of_three_conditions_satisfied()
                    if is_none_of_three_conditions_satisfied:
                        control_policy._set_agv_waiting()
                        deadlock_resolver = DeadlockResolver(agv=agv)
                        is_loop_deadlock_detected = deadlock_resolver.is_loop_deadlock_detected()
                        is_heading_on_deadlock_detected = deadlock_resolver.is_heading_on_deadlock_detected()
                        if is_heading_on_deadlock_detected:
                            deadlock_resolver.resolve_heading_on_deadlock()
                        elif is_loop_deadlock_detected:
                            deadlock_resolver.resolve_loop_deadlock()
                        else:  # No deadlock detected
                            deadlock_resolver._set_reserved_node_as_current_node()

            logger.info(
                f"Updated AGV {agv_id} location to node {current_node}")

        except Agv.DoesNotExist:
            logger.error(f"AGV with ID {agv_id} not found in database")
        except Exception as e:
            logger.error(f"Error updating AGV data: {str(e)}")

    except ValueError as e:
        logger.error(f"Failed to decode AGV data message: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in AGV data handler: {str(e)}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
client.connect(
    host=settings.MQTT_BROKER,
    port=settings.MQTT_PORT,
    keepalive=settings.MQTT_KEEPALIVE
)
