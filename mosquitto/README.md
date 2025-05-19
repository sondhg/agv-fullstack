# Mosquitto MQTT Broker for AGV Communication

This directory contains the configuration for the Eclipse Mosquitto MQTT broker used in the AGV communication system.

## Configuration

The configuration is simple:

- Listens on port 1883 for MQTT connections
- Allows anonymous connections
- Persists messages to disk

## Docker Integration

The Mosquitto broker is automatically started as part of the Docker Compose setup. The configuration and data are persisted using Docker volumes.

## Local Development

For local development, you need to install Mosquitto on your machine.

### Windows:

1. Download from https://mosquitto.org/download/
2. Install with default settings
3. You may need to open a terminal and run
   ```bash
   mosquitto
   ```
   before running the Django server to ensure Mosquitto is running.

Both the Django server and test script will automatically connect to localhost.
