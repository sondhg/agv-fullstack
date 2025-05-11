export const TOPIC_AGVDATA = "agvdata"; // Topic for AGVs to publish data to server
export const TOPIC_AGVROUTE = "agvroute"; // Topic for server to send route commands to AGVs
export const TOPIC_AGVSTATUS = "agvstatus"; // Topic for AGVs to publish status updates to server
export const WEBSOCKET_MQTT_URL = "ws://broker.emqx.io:8083/mqtt"; // ! WebSocket URL for MQTT broker
export const RECONNECT_PERIOD = 5000; // Try to reconnect every 5 seconds
export const CONNECT_TIMEOUT = 30000; // How long to wait for a connection to be established before timing out
