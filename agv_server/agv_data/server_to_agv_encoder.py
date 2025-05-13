"""
Encoder for messages sent from server to AGVs via MQTT.
Converts JSON format instructions into byte array messages.
"""
from .models import Agv
# Frame constants
FRAME_START = 0x7A
FRAME_LENGTH = 0x08
MESSAGE_TYPE = 0x03
FRAME_END = 0x7F

# Motion states
IDLE = Agv.IDLE
MOVING = Agv.MOVING
WAITING = Agv.WAITING

# Direction changes
GO_STRAIGHT = Agv.GO_STRAIGHT
TURN_AROUND = Agv.TURN_AROUND
TURN_LEFT = Agv.TURN_LEFT
TURN_RIGHT = Agv.TURN_RIGHT


def encode_message(motion_state: int, next_node: int, direction_change: int) -> bytes:
    """
    Encode server message into byte array format.

    Args:
        motion_state (int): AGV motion state (0=IDLE, 1=MOVING, 2=WAITING)
        next_node (int): Next node ID for AGV to move to
        direction_change (int): Direction change instruction
                              (0=GO_STRAIGHT, 1=TURN_AROUND, 
                               2=TURN_LEFT, 3=TURN_RIGHT)

    Returns:
        bytes: Encoded message as byte array

    Raises:
        ValueError: If input parameters are invalid
    """
    # Validate inputs
    if motion_state not in (IDLE, MOVING, WAITING):
        raise ValueError(f"Invalid motion state: {motion_state}")

    if direction_change not in (GO_STRAIGHT, TURN_AROUND, TURN_LEFT, TURN_RIGHT):
        raise ValueError(f"Invalid direction change: {direction_change}")

    try:
        # Convert values to bytes
        motion_state_bytes = motion_state.to_bytes(1, byteorder='little')
        next_node_bytes = next_node.to_bytes(2, byteorder='little')
        direction_change_bytes = direction_change.to_bytes(
            1, byteorder='little')

        # Create frame
        frame = bytearray()
        frame.append(FRAME_START)
        frame.append(FRAME_LENGTH)
        frame.append(MESSAGE_TYPE)
        frame.extend(motion_state_bytes)
        frame.extend(next_node_bytes)
        frame.extend(direction_change_bytes)
        frame.append(FRAME_END)

        return bytes(frame)

    except Exception as e:
        raise ValueError(f"Failed to encode message: {str(e)}")
