import paho.mqtt.client as mqtt
from django.conf import settings

from .models import Agv
from .services.controller import ControlPolicyController
from .services.algorithm3 import DeadlockResolver
from .services.position_tracker import update_previous_node
from .agv_to_server_decoder import decode_message
from .server_to_agv_encoder import encode_message, MOVING


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
    """
    Process messages from AGVs reporting their positions and respond with routing instructions.

    This function:
    1. Decodes incoming AGV position updates
    2. Updates the AGV's position in the database
    3. Calculates the next action using control policy
    4. Detects and resolves deadlocks if necessary
    5. Sends movement instructions to affected AGVs

    Args:
        mqtt_client: MQTT client instance for sending responses
        msg: MQTT message object containing topic and payload with AGV data
    """
    # Log received message for debugging purposes
    print(
        f"Received message on topic: {msg.topic} with payload: {msg.payload.hex()}")

    try:
        # STEP 1: Extract AGV data from the incoming message
        data = decode_message(msg.payload)
        agv_id = data['agv_id']
        current_node = data['current_node']

        # Validate required fields in the message
        if not all([agv_id is not None, current_node is not None]):
            print(f"Invalid message format - missing required fields: {data}")
            return

        # STEP 2: Update AGV position in the database
        try:
            agv = Agv.objects.get(agv_id=agv_id)
        except Agv.DoesNotExist:
            print(f"AGV with ID {agv_id} not found in database")
            return

        # Store previous position for tracking movement
        previous_position = agv.current_node

        # Update AGV position tracking data
        update_previous_node(agv)  # First update the tracking history
        agv.current_node = current_node  # Then set the new position
        agv.save()

        # STEP 3: Calculate next action for the AGV
        controller = ControlPolicyController()
        control_result = controller.update_agv_state(agv_id)

        # Refresh AGV data after control policy updates
        updated_agv = Agv.objects.get(agv_id=agv_id)

        # STEP 4: Handle potential deadlocks
        # Track which AGVs need instruction updates (start with triggering AGV)
        deadlock_info = {}
        affected_agvs = set([agv_id])

        # Check if AGV is in WAITING state (potential deadlock)
        if control_result.get("motion_state") == Agv.WAITING:
            # Detect and resolve any deadlocks in the system
            deadlock_info, affected_agvs, control_result = handle_potential_deadlock(
                agv_id, updated_agv, control_result, affected_agvs
            )

            # Re-fetch AGV data if deadlock resolution occurred
            if deadlock_info:
                updated_agv = Agv.objects.get(agv_id=agv_id)

        # STEP 5: Enhance response with detailed AGV state information
        if control_result["success"]:
            # Add complete AGV state to the response data
            control_result.update({
                "reserved_node": updated_agv.reserved_node,
                "spare_flag": updated_agv.spare_flag,
                "backup_nodes": updated_agv.backup_nodes,
                "moved_from": previous_position,
                "previous_node": updated_agv.previous_node,
                "remaining_path": updated_agv.remaining_path,
                "direction_change": updated_agv.direction_change,
                **deadlock_info  # Add deadlock information if applicable
            })

        # Log the position update and next instruction for debugging
        motion_state = control_result.get("motion_state", "unknown")
        next_node = control_result.get("next_node", None)
        print(f"AGV {agv_id} updated position from {previous_position} to {current_node}, "
              f"motion_state: {motion_state}, next_node: {next_node}")

        # STEP 6: Send instructions to all affected AGVs
        send_instructions_to_affected_agvs(
            mqtt_client,
            affected_agvs,
            agv_id,
            control_result
        )

    except ValueError as e:
        print(f"Failed to decode/encode message: {e}")
    except Agv.DoesNotExist:
        print(f"AGV with ID {agv_id} not found")
    except Exception as e:
        print(f"Error processing message: {e}")


def handle_potential_deadlock(agv_id, updated_agv, control_result, affected_agvs):
    """
    Helper function to detect and resolve deadlocks when an AGV is in WAITING state.

    Args:
        agv_id: ID of the AGV that triggered the update
        updated_agv: The updated AGV object
        control_result: The result from the control policy controller
        affected_agvs: Set of AGV IDs that will need instruction updates

    Returns:
        tuple: (deadlock_info, affected_agvs, updated_control_result)
    """
    # Initialize deadlock resolution components
    deadlock_info = {}
    resolver = DeadlockResolver()

    # Run deadlock detection and resolution algorithm
    deadlock_result = resolver.detect_and_resolve_deadlocks()

    # Process results if any deadlocks were resolved
    if deadlock_result.get("deadlocks_resolved", 0) > 0:
        # Add any moved AGVs to the list of AGVs needing updates
        moved_agvs = deadlock_result.get("agvs_moved", [])
        affected_agvs.update(moved_agvs)

        # If this AGV was moved as part of deadlock resolution, update its state
        if agv_id in moved_agvs:
            control_result["motion_state"] = MOVING
            control_result["message"] = "AGV moved to spare point to resolve deadlock"
            control_result["next_node"] = updated_agv.next_node

        # Record deadlock resolution details for logging/debugging
        deadlock_info = {
            "deadlock_resolved": True,
            "deadlock_details": deadlock_result
        }

    return deadlock_info, affected_agvs, control_result


def send_instructions_to_affected_agvs(mqtt_client, affected_agvs, triggering_agv_id, control_result):
    """
    Send appropriate movement instructions to all affected AGVs.

    Args:
        mqtt_client: MQTT client for publishing messages
        affected_agvs: Set of AGV IDs that need instruction updates
        triggering_agv_id: ID of the AGV that initiated the update
        control_result: The result from the control policy including motion state
    """
    # First send instructions to other affected AGVs (not the triggering AGV)
    for affected_agv_id in affected_agvs:
        if affected_agv_id != triggering_agv_id:
            # Get the current state of this affected AGV
            affected_agv = Agv.objects.get(agv_id=affected_agv_id)

            # Create instruction message for this AGV
            instruction_message = encode_message(
                motion_state=affected_agv.motion_state,
                next_node=affected_agv.next_node,
                direction_change=affected_agv.direction_change
            )

            # Publish instructions to this AGV's route topic
            agv_topic = f"{MQTT_TOPIC_AGVROUTE}/{affected_agv_id}"
            mqtt_client.publish(agv_topic, instruction_message)
            print(f"Sent updated instructions to AGV {affected_agv_id}")

    # Finally send instructions to the triggering AGV
    triggering_agv_message = encode_message(
        motion_state=control_result.get("motion_state"),
        next_node=control_result.get("next_node"),
        direction_change=control_result.get("direction_change")
    )

    mqtt_client.publish(
        f"{MQTT_TOPIC_AGVROUTE}/{triggering_agv_id}", triggering_agv_message)


# def send_agv_hello_message(client, msg, agv_id):
#     client.publish(f"{MQTT_TOPIC_AGVHELLO}/{agv_id}", "Hello from server")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
client.connect(
    host=settings.MQTT_BROKER,
    port=settings.MQTT_PORT,
    keepalive=settings.MQTT_KEEPALIVE
)
