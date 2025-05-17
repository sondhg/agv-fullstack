# This file gives example to describe the data frame used for sending messages to MQTT broker topic agvroute/{agv_id} from Django server

FRAME_START = 0x7A  # fixed value
FRAME_LENGTH = 0x08  # fixed value
MESSAGE_TYPE = 0x03  # fixed value

# Payload
# Example for motion_state=1. motion_state can be 0 (IDLE), 1 (MOVING), or 2 (WAITING)
MOTION_STATE = 1
NEXT_NODE = 18  # Example for next_node=18
# Example for direction_change=0. direction_change can be 0 (GO_STRAIGHT) or 1 (TURN_AROUND) or 2 (TURN_LEFT) OR 3 (TURN_RIGHT) or 4 (STAY_STILL)
DIRECTION_CHANGE = 0

FRAME_END = 0x7F  # fixed value

motion_state_to_bytes = MOTION_STATE.to_bytes(1, byteorder='little')
next_node_to_bytes = NEXT_NODE.to_bytes(2, byteorder='little')
direction_change_to_bytes = DIRECTION_CHANGE.to_bytes(1, byteorder='little')

data_frame_server_to_agv = bytearray()
data_frame_server_to_agv.append(FRAME_START)
data_frame_server_to_agv.append(FRAME_LENGTH)
data_frame_server_to_agv.append(MESSAGE_TYPE)
data_frame_server_to_agv.extend(motion_state_to_bytes)
data_frame_server_to_agv.extend(next_node_to_bytes)
data_frame_server_to_agv.extend(direction_change_to_bytes)
data_frame_server_to_agv.append(FRAME_END)
print("data_frame_server_to_agv:", data_frame_server_to_agv)
