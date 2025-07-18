FRAME_START = 0x7A  # fixed value
FRAME_LENGTH = 0x08  # fixed value
MESSAGE_TYPE = 0x02  # fixed value
PAYLOAD_AGV_ID = 2  # Example for AGV with agv_id=2
PAYLOAD_CURRENT_NODE = 17  # Example for current_node=17
FRAME_END = 0x7F  # fixed value

payload_agv_id_to_bytes = PAYLOAD_AGV_ID.to_bytes(2, byteorder="little")
payload_current_node_to_bytes = PAYLOAD_CURRENT_NODE.to_bytes(2, byteorder="little")


data_frame_agv_to_server = bytearray()
data_frame_agv_to_server.append(FRAME_START)
data_frame_agv_to_server.append(FRAME_LENGTH)
data_frame_agv_to_server.append(MESSAGE_TYPE)
data_frame_agv_to_server.extend(payload_agv_id_to_bytes)
data_frame_agv_to_server.extend(payload_current_node_to_bytes)
data_frame_agv_to_server.append(FRAME_END)

print("data_frame_agv_to_server:", data_frame_agv_to_server)
