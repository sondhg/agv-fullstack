# Web App as Central Controller for AGV System

## Main Goal

Generate and update a smart schedule for AGVs to avoid collisions and deadlocks using the **Dynamic Spare Point Application (DSPA)** technique specified in the `algorithms-pseudocode.tex` file located in the `docs` folder.

## Workflow

### Step 1: User Authentication

#### Register

- Users can register for an account by sending a POST request to:  
   `POST localhost:8000/api/auth/register/`
- Required fields:
  - `username`
  - `email`
  - `password`

#### Login

- Users can log in by sending a POST request to:  
   `POST localhost:8000/api/auth/login/`
- Required fields:
  - `username`
  - `password`
- On successful login, a JWT access_token is returned, which must be included in the Authorization header for subsequent requests.

#### Logout

- Users can log out by sending a POST request to:  
   `POST localhost:8000/api/auth/logout/`

---

### Step 2: User Creates a Map Layout

The map layout consists of nodes and edges, where nodes represent identified points (in real life, these are marked with RFID cards) and edges represent connections between these nodes (if any).

#### 2.1 Upload Map Data

- User sends:
  - A CSV file containing connections and distances between nodes to the API endpoint:  
     `POST localhost:8000/api/map/import-connections/`
  - A CSV file containing relative cardinal directions for each connection to the API endpoint:  
     `POST localhost:8000/api/map/import-directions/`
- Example files: `new-map-conn-and-dist.csv` and `new-map-dir.csv` (located in the `sample-data` folder).

#### 2.2 View Map

- Once the files are uploaded, the user can view the map on the frontend (Map page) by sending a GET request to:  
   `GET localhost:8000/api/map/get/`

---

### Step 3: User Sends Orders

#### 3.1 Create Orders

- Orders can be created:
  - Individually through a form.
  - In bulk by uploading a CSV file.
- Orders are sent to the API endpoint:  
   `POST localhost:8000/api/orders/create/`

#### 3.2 View Orders

- Created orders are displayed in a table on the Orders page by sending a GET request to:  
   `GET localhost:8000/api/orders/get/`

---

### Step 4: User Generates Initial Schedules

#### 4.1 Pre-requisite

- At least one order must be created before generating schedules.

#### 4.2 Generate Schedules

- On the Schedules page, users click the "Create Schedules" button, which sends a POST request to:  
   `POST localhost:8000/api/schedules/generate/`

#### 4.3 Server Processing

- The server uses the DSPA algorithm to calculate paths for each AGV, including:
  - `initial_path`: Shortest path from `parking_node` → `storage_node` → `workstation_node`. Eventually, the AGV needs to travel through all nodes in `initial_path`. However, if collisions or deadlocks are detected, AGV may need to move to a spare point (`sp`) to avoid them, then return to the `initial_path` once the path is clear.
  - `residual_path`: Remaining path points not yet visited (initially the same as `initial_path`).
  - `cp`: Shared points.
  - `scp`: Sequential shared points.
  - `sp`: Spare points.
- Generated schedules are stored in the database.

#### 4.4 View Schedules

- Schedules can be viewed in a table on the Schedules page by sending a GET request to:  
   `GET localhost:8000/api/schedules/get/`

---

### Step 5: AGVs Operate Based on Schedules

- AGVs travel based on the schedules generated by the server.
- Every time an AGV reaches a node, it sends its position to the server via MQTT.
- The server uses the AGV's position to recalculate the schedule and send it back to the AGV.
- The server also checks for collisions and deadlocks using the DSPA algorithm.
- If a collision or deadlock is detected, the server recalculates the schedule and sends it to the AGVs.
- The updated data include `residual_path`, `cp`, `scp`, and `sp`.

---

## Specific example of how I test the AGV system

I want to successfully mimic the `Example 3` specified in the research paper `algorithms-pseudocode.tex` file. This will be my testing script to see if my system works or not. The example consists of 3 AGVs and 3 orders.

- I create a map layout with 32 nodes. I used example files `new-map-conn-and-dist.csv` and `new-map-dir.csv` (located in the `sample-data` folder) to create the map layout.
- I create 3 orders similar to `orders-example-3.json` (located in the `sample-data` folder).
- I generate schedules for the 3 AGVs using the "Create Schedules" button on the Schedules page.
- I want to mimic AGVs' positions update to the server, but have not implemented the real physical AGVs or any simulation yet. I need to do this in the future to test if my web app works correctly with the AGVs.
- At each step, I must check if it has the same result as the example in the research paper. I will check the following:
  - The initial path for each AGV.
  - The residual path for each AGV.
  - The shared points (cp) for each AGV.
  - The sequential shared points (scp) for each AGV.
  - The spare points (sp) for each AGV.
  - The detection of collisions and deadlocks.

## Technologies Used

- **Backend**: Django (Python)
- **Frontend**: React (TypeScript, Vite) + Tailwind CSS + Shadcn UI
- **Database**: PostgreSQL
- **Communication**: MQTT broker (server ↔ AGVs)
- **Live Updates**: WebSocket

## Project Structure

This is not everything in the project, but just to give you an idea of how the project is structured.

    ```
    ├── agv_server
    │   ├── agv_server
    │   │   ├── settings.py
    │   │   ├── urls.py
    │   │   ├── wsgi.py
    │   │   ├── asgi.py
    │   ├── map_data
    │   ├── order_data
    │   ├── schedule_generate
    │   ├── users
    │   └── manage.py
    ├── requirements.txt
    ├── frontend
    └── simulation
    ```
