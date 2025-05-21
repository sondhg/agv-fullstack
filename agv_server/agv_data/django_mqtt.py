import paho.mqtt.client as mqtt_client
import json
from .models import Agv
from .services.controller import ControlPolicyController
from .services.algorithm3 import DeadlockResolver
from .services.position_tracker import update_previous_node
from .agv_to_server_decoder import decode_message
from .server_to_agv_encoder import encode_message, MOVING

# MQTT Configuration
import os
# In development: use localhost, in Docker: use service name
MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_KEEPALIVE = 60
CLIENT_ID = "django_server"

TOPIC_AGV_DATA = "agvdata"
TOPIC_AGV_HELLO = "agvhello"

# Initialize global client variable
client = None


def on_connect(client, userdata, flags, rc, properties):
    """
    Callback when client connects to broker.

    Args:
        client: MQTT client instance
        userdata: User-defined data passed to callback
        flags: Response flags from broker
        rc (int): Connection result code
        properties: MQTT v5.0 properties
    """
    if rc == 0:
        print("Connected to MQTT broker successfully")
        # Subscribe to all AGV data topics using wildcard
        client.subscribe(f"{TOPIC_AGV_DATA}/#")
        print(f"Subscribed to topic: {TOPIC_AGV_DATA}/#")
        # Subscribe to the new hello topic
        client.subscribe(f"{TOPIC_AGV_HELLO}/#")
        print(f"Subscribed to topic: {TOPIC_AGV_HELLO}/#")
    else:
        print(f"Failed to connect: {rc}")


def on_message(client, userdata, msg):
    """
    Route incoming MQTT messages to appropriate handlers based on topic.

    Args:
        client: MQTT client instance 
        userdata: User-defined data passed to callback
        msg: MQTT message object containing topic and payload
    """
    # Route message to appropriate handler based on topic prefix
    if msg.topic.startswith(f"{TOPIC_AGV_DATA}/"):
        handle_agv_data_message(client, msg)
    elif msg.topic.startswith(f"{TOPIC_AGV_HELLO}/"):
        handle_agv_hello_message(client, msg)
    else:
        print(f"Received message on unhandled topic: {msg.topic}")
    """
    Handle incoming MQTT messages from AGVs.
    Implements identical logic to UpdateAGVPositionView.post()

    Args:
        client: MQTT client instance 
        userdata: User-defined data passed to callback
        msg: MQTT message object containing topic and payload

    Message format:
        Byte array following data frame specification
    """


def initialize_mqtt_client():
    """
    Initialize and connect the MQTT client.

    Returns:
        mqtt_client.Client: The initialized MQTT client
    """
    global client

    # Only create a new client if one doesn't exist
    if client is None:
        client = mqtt_client.Client(
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
            client_id=CLIENT_ID
        )        # Set up callbacks
        client.on_connect = on_connect
        client.on_message = on_message

        # Connect to broker
        try:
            client.connect(host=MQTT_BROKER, port=MQTT_PORT,
                           keepalive=MQTT_KEEPALIVE)
            print(f"MQTT client initialized with broker: {MQTT_BROKER}")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")

    return client


def start_mqtt_client():
    """
    Start the MQTT client loop. Call this only from the AppConfig.ready() method.
    """
    client = initialize_mqtt_client()

    # Check if the loop is already running
    if not client.is_connected():
        client.loop_start()
        print("MQTT client loop started")


def handle_agv_data_message(client, msg):
    """
    Handle incoming AGV data messages.

    Args:
        client: MQTT client instance
        msg: MQTT message object containing topic and payload
    """
    print(
        f"Received message on topic: {msg.topic} with payload: {msg.payload.hex()}")
    try:
        # Decode byte array message
        data = decode_message(msg.payload)
        agv_id = data['agv_id']
        current_node = data['current_node']

        if not all([agv_id is not None, current_node is not None]):
            print(f"Invalid message format: {data}")
            return

        agv = Agv.objects.get(agv_id=agv_id)

        # Store previous position for logging
        previous_node = agv.current_node

        # Update previous_node field before changing current_node
        update_previous_node(agv)

        # Update AGV position in database
        agv.current_node = current_node
        agv.save()

        # Calculate next action using control policy
        controller = ControlPolicyController()
        result = controller.update_agv_state(agv_id)

        # Get the updated AGV data for the response
        updated_agv = Agv.objects.get(agv_id=agv_id)

        # Handle deadlock detection and resolution
        deadlock_info = {}
        agvs_to_update = set([agv_id])  # Start with the triggering AGV

        if result.get("motion_state") == Agv.WAITING:
            # Initialize the deadlock resolver
            resolver = DeadlockResolver()

            # Detect and resolve deadlocks
            deadlock_result = resolver.detect_and_resolve_deadlocks()

            # If deadlocks were resolved, refresh the AGV data and update moved AGVs
            if deadlock_result.get("deadlocks_resolved", 0) > 0:
                agvs_to_update.update(deadlock_result.get("agvs_moved", []))

                # Re-fetch the AGV to get updated state after deadlock resolution
                updated_agv = Agv.objects.get(agv_id=agv_id)

                # Update the result with the new state if this AGV was moved
                if agv_id in deadlock_result.get("agvs_moved", []):
                    result["motion_state"] = MOVING
                    result["message"] = "AGV moved to spare point to resolve deadlock"
                    result["next_node"] = updated_agv.next_node

                deadlock_info = {
                    "deadlock_resolved": True,
                    "deadlock_details": deadlock_result
                }

        # Add detailed state information to the response
        if result["success"]:
            result.update({
                "reserved_node": updated_agv.reserved_node,
                "spare_flag": updated_agv.spare_flag,
                "spare_points": updated_agv.spare_points,
                "moved_from": previous_node,
                "previous_node": updated_agv.previous_node,
                "residual_path": updated_agv.residual_path,
                "direction_change": updated_agv.direction_change,
                **deadlock_info  # Add deadlock information if applicable
            })

        # Log the position update for debugging
        print(f"AGV {agv_id} updated position from {previous_node} to {current_node}, " +
              f"motion_state: {result.get('motion_state', 'unknown')}, next_node: {result.get('next_node', None)}")

        # Send instructions to all affected AGVs
        for affected_agv_id in agvs_to_update:
            # Skip if it's the triggering AGV, as we'll handle it below
            if affected_agv_id != agv_id:
                # Get the updated state for this AGV
                affected_agv = Agv.objects.get(agv_id=affected_agv_id)

                # Create byte array message for this AGV

                message = encode_message(
                    motion_state=affected_agv.motion_state,
                    next_node=affected_agv.next_node,
                    direction_change=affected_agv.direction_change
                )

                # Publish instructions to this AGV's route topic
                client.publish(f"agvroute/{affected_agv_id}", message)
                print(f"Sent updated instructions to AGV {affected_agv_id}")

        # Send instructions to the triggering AGV

        message = encode_message(
            motion_state=result.get("motion_state"),
            next_node=result.get("next_node"),
            direction_change=result.get("direction_change")
        )

        client.publish(f"agvroute/{agv_id}", message)

    except ValueError as e:
        print(f"Failed to decode/encode message: {e}")
    except Agv.DoesNotExist:
        print(f"AGV with ID {agv_id} not found")
    except Exception as e:
        print(f"Error processing message: {e}")


def handle_agv_hello_message(client, msg):
    pass
