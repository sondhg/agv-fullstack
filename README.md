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

### Step 4: User Dispatch Created Orders to AGVs

#### 4.1 Pre-requisite

- At least one order must be created before dispatching orders to AGVs.

#### 4.2 Dispatch orders to AGVs

- On the AGVs page, users click the "Dispatch orders to AGVs" button, which sends a POST request to:  
   `POST localhost:8000/api/agvs/dispatch-orders-to-agvs/`

#### 4.4 View initialized AGV data after dispatching

- AGV data can be viewed in a table on the AGVs page by sending a GET request to:  
   `GET localhost:8000/api/agvs/get/`

---

### Step 5: AGVs Operate

- AGVs travel based on instructions by the server.
- Every time an AGV reaches a node, it sends its position to the server via MQTT.
- The server uses the AGV's position to recalculate parameters and send it back to the AGV.
- The server also checks for collisions and deadlocks using the DSPA algorithm.
- If a collision or deadlock is detected, the server evaluates the situation and sends solutions to the AGVs.

---

## Specific example of how I test the AGV system

I want to successfully mimic the `Example 3` specified in the research paper `algorithms-pseudocode.tex` file. This will be my testing script to see if my system works or not. The example consists of 3 AGVs and 3 orders.

- I create a map layout with 32 nodes. I used example files `new-map-conn-and-dist.csv` and `new-map-dir.csv` (located in the `sample-data` folder) to create the map layout.
- I create 3 orders similar to `orders-example-3.json` (located in the `sample-data` folder).
- I dispatch the orders to AGVs by clicking the "Dispatch orders to AGVs" button on the AGVs page. This sends a POST request to the server, which initializes the AGV data and assigns the orders to the AGVs.
- I want to mimic AGVs' positions update to the server, but have not implemented the real physical AGVs or any simulation yet. I need to do this in the future to test if my web app works correctly with the AGVs. For now, I use Postman to send a POST request to API endpoint `POST localhost:8000/api/agvs/update-position/` of the server with the AGV's position. The request body should contain the fields `agv_id` and `current_node`. For example, to update the position of AGV 1 to node 7, I send the following request body:
  ```json
  {
    "agv_id": 1,
    "current_node": 7
  }
  ```
- The detailed way of how I do the testing is specified in the `test-agvs-update-positions.md` file in the root directory.

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
    │   ├── agv_data
    │   ├── users
    │   └── manage.py
    ├── requirements.txt
    ├── frontend
    ```
