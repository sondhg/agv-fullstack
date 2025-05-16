## Data Frame from AGV to Server

| Frame start | Frame length | Message type   | agv_id                                                                    | current_node                                                                                         | Frame end |
| ----------- | ------------ | -------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | --------- |
| 1 byte      | 1 byte       | 1 byte         | 2 bytes                                                                   | 2 bytes                                                                                              | 1 byte    |
| 0x7A        | 0x08         | 0x02           |                                                                           |                                                                                                      | 0x7F      |
|             |              | Message type 2 | Hexadecimal value corresponding to the decimal value of that AGV's agv_id | Hexadecimal value corresponding to the decimal value of that node: For example, node 16 will be 0x10 |           |

Use little-endian byte order.

Example: AGV 2 arrived at node 17 and will send a message in the format of a byte array to the MQTT topic agvdata/2. File `example_data_frame_agv_to_server.py`in root directory shows how AGV creates the message as the variable data_frame_agv_to_server.

## Data Frame from Server to AGV

| Frame start | Frame length | Message type   | Motion state                       | Next node                                                         | Direction change                                                  | Frame end |
| ----------- | ------------ | -------------- | ---------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------- | --------- |
| 1 byte      | 1 byte       | 1 byte         | 1 byte                             | 2 bytes                                                           | 1 byte                                                            | 1 byte    |
| 0x7A        | 0x08         | 0x03           |                                    |                                                                   |                                                                   | 0x7F      |
|             |              | Message type 3 | 0: IDLE<br>1: MOVING<br>2: WAITING | Hexadecimal value corresponding to the decimal value of next node | 0: GO_STRAIGHT<br>1: TURN_AROUND<br>2: TURN_LEFT<br>3: TURN_RIGHT<br>4: STAY_STILL |           |

Use little-endian byte order.

Example: Server wants AGV to move to node 18 going straight ahead. File `example_data_frame_server_to_agv.py` in root directory shows how Server creates the message as the variable data_frame_server_to_agv.
