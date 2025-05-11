import paho.mqtt.client as mqtt_client
import json
from .models import Agv
from .services.controller import ControlPolicyController
from .services.algorithm3 import DeadlockResolver
from .services.position_tracker import update_previous_node

# MQTT Configuration
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
CLIENT_ID = "django_server"

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
        client.subscribe("agvdata/#")
        print(f"Subscribed to topic: agvdata/#")
    else:
        print(f"Failed to connect: {rc}")


def on_message(client, userdata, msg):
    """
    Handle incoming MQTT messages.
    Implements identical logic to UpdateAGVPositionView.post()

    Args:
        client: MQTT client instance 
        userdata: User-defined data passed to callback
        msg: MQTT message object containing topic and payload

    Message format:
    {
        "agv_id": int,           # ID of the AGV (r_i)
        "current_node": int,     # Current position of the AGV (v_c^i)
    }
    """
    print(
        f"Received message on topic: {msg.topic} with payload: {msg.payload}")
    try:
        data = json.loads(msg.payload.decode())
        agv_id = data.get('agv_id')
        current_node = data.get('current_node')

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
        if result.get("motion_state") == Agv.WAITING:
            # Initialize the deadlock resolver
            resolver = DeadlockResolver()

            # Detect and resolve deadlocks
            deadlock_result = resolver.detect_and_resolve_deadlocks()

            # If deadlocks were resolved, refresh the AGV data
            if deadlock_result.get("deadlocks_resolved", 0) > 0:
                # Re-fetch the AGV to get updated state after deadlock resolution
                updated_agv = Agv.objects.get(agv_id=agv_id)

                # Update the result with the new state if this AGV was moved
                if agv_id in deadlock_result.get("agvs_moved", []):
                    result["motion_state"] = Agv.MOVING
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

        # Filter only required fields
        filtered_instructions = {
            "motion_state": result.get("motion_state"),
            "direction_change": result.get("direction_change"),
            "next_node": result.get("next_node")
        }

        client.publish(f"agvroute/{agv_id}", json.dumps(filtered_instructions))

    except json.JSONDecodeError as e:
        print(f"Failed to decode message: {e}")
    except Agv.DoesNotExist:
        print(f"AGV with ID {agv_id} not found")
    except Exception as e:
        print(f"Error processing message: {e}")


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
        )

        # Set up callbacks
        client.on_connect = on_connect
        client.on_message = on_message

        # Connect to broker
        try:
            client.connect(host=MQTT_BROKER, port=MQTT_PORT,
                           keepalive=MQTT_KEEPALIVE)
            print("MQTT client initialized")
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
