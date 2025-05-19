# 🚗 AGV Web App

## Important Notes

- I Dockerized the frontend as production-ready, which means if you edit the frontend code when the web app is running, the changes do not take effect.
- However, I Dockerized the backend as development-ready, which means if you edit the backend code when the web app is running, the changes take effect immediately. If not, you need to rebuild the backend image with `docker compose up --build` command.
- The MQTT broker I use for backend is `broker.emqx.io`, which is a public broker. If you want to config your own broker, you should edit code in `django_mqtt.py` and `test_sending_to_mqtt.py` file. Just use `Ctrl+P` in VSCode to find these files. You may need to config some IP address for the web app to connect to your broker too.

## 🚀 How to Run This Web App with Docker

> ⚠️ **Pre-requisite:**  
> You must have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed before proceeding.

### 1. Clone the Repository

```bash
git clone https://github.com/sondhg/agv-fullstack.git
```

### 2. Navigate to the Project Root

Make sure you are in the root directory of the project (where the `docker-compose.yml` file is located):

```bash
cd agv_fullstack
```

All commands should be run from the root directory of the project.

### 3. Start the Web App

If it's your first time running this web app:

```bash
docker compose up --build
```

- Alternative: If you don't want to see the logs of the web app in your terminal, you can add `-d` flag to run it in detached mode instead:

```bash
docker compose up -d --build
```

Please know that running in detached mode means: Even if you close the terminal, the web app will still run in the background.

- Wait till it finishes. May take a while; later runs will be faster.

This will start:

- **Frontend:** [http://localhost:8080](http://localhost:8080)
- **Backend:** [http://localhost:8000](http://localhost:8000)

You only need to access the frontend at [http://localhost:8080](http://localhost:8080). The backend is automatically configured to connect to the frontend.

### 4. Stop the Web App

When you are done using the web app, you can stop it with:

```bash
docker compose down
```

If you don't run `docker compose down`, the web app will continue running in the background. This means ports 8080 and 8000 will be occupied until you eventually run the command.  
**Recommendation:** Run `docker compose down` when you are done using the web app.

### 5. Subsequent Runs

To use the web app next times, you can just run:

```bash
docker compose up
```

Again, the `-d` flag is optional. If you want to run it in detached mode, you can add `-d` flag:

```bash
docker compose up -d
```

---

## 📝 How to Use This Web App

Assume you have already run the web app with Docker and you can access it at [http://localhost:8080](http://localhost:8080).

First, you'll see the **Home** page. There is a sidebar on the left for navigation (You can toggle this sidebar with `Ctrl+B`). You can also navigate between pages using keyboard shortcut `Ctrl + K`.

---

### 1. Register, then Login

- Do this before anything else. If you do not login, you cannot access any page other than the **Home** page.
- Later, when you are bored, you can log out by clicking your username icon at the bottom of the left sidebar.

---

### 2. Create Map Data

1. Navigate to **Map** page.
2. Click **"Download sample CSV files"** button. Two CSV files will be downloaded.
3. Click **"Import 1st CSV"** button and select the `map-connection-and-distance.csv` file.
4. Click **"Import 2nd CSV"** button and select the `map-direction.csv` file.
5. Click **"Show map image"** and you'll see an SVG image of the map.

---

### 3. Create Orders

1. Navigate to **Orders** page.
2. Click **"CSV instructions"** button. There are two buttons for downloading two different CSV files. You can choose any of them.
3. Click **"Import CSV"** button and select the downloaded CSV file.

---

### 4. Create Initial AGV Data

1. Navigate to **AGVs** page.
2. Click **"Create AGV"** button and fill in the data.
   - The `preferred_parking_node` field **MUST** match the `parking_node` of an order.
   - For example, if there is an order whose `parking_node` = 1, then there should be at least one AGV whose `preferred_parking_node` = 1. Otherwise, this order will not be assigned to any AGV.
3. Once done, click **"Dispatch orders to AGVs"** button. This will assign the orders to the AGVs and generate some initial data.

---

### 5. Simulate AGV Updating Their Positions to MQTT Broker via a Python Script

Follow these steps if you don't have physical AGVs to test the web app yet. This is a simulation of AGVs updating their positions to the MQTT broker to receive instructions.

1. Open a new terminal, still in the root directory of the project, and run:

   ```bash
   python test_sending_to_mqtt.py
   ```

2. Inside the terminal, it will ask you to enter the AGV ID (`agv_id`) and the new position (`current_node`) of the AGV, as normal decimal integers.
   - Enter AGV ID, hit `Enter`, then enter the new position, and hit `Enter` again.
   - Once done, the encoded message will be published to MQTT topic `agvdata/{agv_id}`.
   - The server will process the message and update the AGV's position in the database.
   - The server will respond with instructions by publishing to topic `agvroute/{agv_id}`. The instructions will be printed in the terminal in a human-readable format for you to see.
   - Hit `Enter` to continue with the next message.
   - Hit `Ctrl + C` to stop the script once you are done.
