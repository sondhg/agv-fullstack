# 🚗 AGV Web App

## Important Notes

- **Frontend:** Production-ready (changes require rebuild)
- **Backend:** Development-ready (changes apply immediately)
- **MQTT Broker:** mosquitto (running on localhost:1883). Config in `django_mqtt.py` and `test_sending_to_mqtt.py`

## 🚀 Quick Start (Docker)

> ⚠️ **Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/)**

```bash
# 1. Clone and navigate to project. All commands should be run from the root directory (where the `compose.yaml` file is located)
git clone https://github.com/sondhg/agv-fullstack.git
cd agv_fullstack

# 2. Start application in detached mode (remove `-d` if you wanna see terminal logs)
docker compose up -d

# 3. Access frontend at http://localhost:8080
# Backend runs at http://localhost:8000 but direct access not needed

# 4. Stop application when done
docker compose down
```

## 📝 Usage Guide

### Navigation

- Access app at [http://localhost:8080](http://localhost:8080)
- Toggle sidebar with `Ctrl+B` or navigate with `Ctrl+K`

### Workflow

1. **Register & Login** (required for all features)

2. **Create Map Data**

   - Navigate to **Map** page → Download sample CSVs
   - Import both CSV files → Show map image

3. **Create Orders**

   - Navigate to **Orders** page → Download sample CSV
   - Import CSV file with order data

4. **Configure AGVs**

   - Navigate to **AGVs** page → Create AGVs
   - Ensure `preferred_parking_node` matches an order's `parking_node`
   - Click "Dispatch orders to AGVs"

5. **Simulate AGV Movement** (to mimic AGVs communicating with MQTT broker)
   ```bash
   python test_sending_to_mqtt.py
   ```
   - Enter AGV ID and position when prompted
   - The script publishes `agv_id` and `current_node` to topic `agvdata/{agv_id}` and receives server instructions from topic `agvroute/{agv_id}`
   - Press `Enter` to continue, `Ctrl+C` to exit
