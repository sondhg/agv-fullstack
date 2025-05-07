"""MQTT handler for AGV position updates."""
import json
import paho.mqtt.client as mqtt
from django.conf import settings
from agv_data.models import Agv
from agv_data.services.controller import ControlPolicyController
from agv_data.services.algorithm3 import DeadlockResolver
from agv_data.services.position_tracker import update_previous_node


class MQTTHandler:
    """
    Handles MQTT communication with AGVs.
    Implements the same control logic as UpdateAGVPositionView.
    """

    def __init__(self):
        """Initialize MQTT client and connect to broker."""
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.controller = ControlPolicyController()

        # Connect to MQTT broker using Django settings
        try:
            self.client.connect(
                host=settings.MQTT_BROKER_HOST,
                port=settings.MQTT_BROKER_PORT,
                keepalive=settings.MQTT_KEEPALIVE
            )
            self.client.loop_start()
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")

    def on_connect(self, client, userdata, flags, rc):
        """Callback when client connects to broker."""
        if rc == 0:
            print("Connected to MQTT broker successfully")
            # Subscribe to AGV position updates using topic from settings
            client.subscribe(f"{settings.MQTT_TOPIC_PREFIX}")
        else:
            print("Bad connection. Code:", rc)

    def on_message(self, client, userdata, msg):
        """
        Handle incoming MQTT messages.
        Implements identical logic to UpdateAGVPositionView.post()

        Message format:
        {
            "agv_id": int,           # ID of the AGV (r_i)
            "current_node": int,     # Current position of the AGV (v_c^i)
        }

        Response format identical to UpdateAGVPositionView
        """
        print(
            f'Received message on topic: {msg.topic} with payload: {msg.payload}')
        try:
            # Parse incoming message
            data = json.loads(msg.payload.decode())
            agv_id = data.get('agv_id')
            current_node = data.get('current_node')

            # Validate input data
            if not agv_id or current_node is None:
                error_response = {
                    "success": False,
                    "message": "agv_id and current_node are required fields"
                }
                self.send_response(agv_id, error_response)
                return

            # Get the AGV from database
            try:
                agv = Agv.objects.get(agv_id=agv_id)
            except Agv.DoesNotExist:
                error_response = {
                    "success": False,
                    "message": f"AGV with ID {agv_id} not found"
                }
                self.send_response(agv_id, error_response)
                return

            # Store previous position for logging
            previous_node = agv.current_node

            # Update previous_node field before changing current_node
            update_previous_node(agv)

            # Update AGV position in database
            agv.current_node = current_node
            agv.save()

            # Calculate next action using control policy
            result = self.controller.update_agv_state(agv_id)

            # Get the updated AGV data for the response
            updated_agv = Agv.objects.get(agv_id=agv_id)

            # Handle deadlock detection and resolution
            deadlock_info = {}
            if result.get("state") == "waiting":
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
                        result["state"] = "moving"
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
                  f"state: {result.get('state', 'unknown')}, next_node: {result.get('next_node', None)}")

            # Send response back to AGV
            self.send_response(agv_id, result)

        except json.JSONDecodeError:
            error_response = {
                "success": False,
                "message": "Invalid JSON format in message"
            }
            self.send_response(agv_id, error_response)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            error_response = {
                "success": False,
                "message": f"Error processing position update: {str(e)}",
                "details": traceback_str
            }
            self.send_response(agv_id, error_response)

    def send_response(self, agv_id, response_data):
        """Send response back to specific AGV."""
        response_topic = f"{settings.MQTT_TOPIC_PREFIX}/response/{agv_id}"
        self.client.publish(response_topic, json.dumps(response_data))


# Create a singleton instance
mqtt_handler = None


def init_mqtt_handler():
    """Initialize the MQTT handler singleton."""
    global mqtt_handler
    if mqtt_handler is None:
        mqtt_handler = MQTTHandler()
    return mqtt_handler
