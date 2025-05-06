# AGV Server API Documentation

## Base Information

- Base URL: `/api`
- Content-Type: `application/json`
- Authentication: JWT (JSON Web Token)

## Authentication

### Register

- **URL**: `/api/auth/register/`
- **Method**: `POST`
- **Description**: Register a new user
- **Request Body**:
  ```json
  {
    "name": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": 1, // Integer: User ID
    "name": "John Doe", // String: Full name of user
    "email": "john.doe@example.com" // String: Email address
  }
  ```

### Login

- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Description**: Authenticate user and get tokens
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOiJ...", // String: JWT access token
    "refresh_token": "eyJhbGciOiJ...", // String: JWT refresh token
    "email": "john.doe@example.com", // String: Email address
    "name": "John Doe", // String: Full name of user
    "message": "Login successful" // String: Status message
  }
  ```
- **Notes**: Access token is also set as an HTTP-only cookie

### Logout

- **URL**: `/api/auth/logout/`
- **Method**: `POST`
- **Description**: Logout user and invalidate tokens
- **Request Body**:
  ```json
  {
    "email": "string",
    "refresh_token": "string"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "Logged out successfully"
  }
  ```

### Get User Info

- **URL**: `/api/auth/user/`
- **Method**: `GET`
- **Description**: Get current user information
- **Authentication**: Required (access_token cookie)
- **Response**: `200 OK`
  ```json
  {
    "id": "integer",
    "name": "string",
    "email": "string"
  }
  ```

## AGV Management

### List AGVs

- **URL**: `/api/agvs/get/`
- **Method**: `GET`
- **Description**: Get list of all AGVs
- **Response**: `200 OK`
  ```json
  [
    {
      "agv_id": 1, // Integer: Unique identifier for the AGV
      "preferred_parking_node": 5, // Integer: Node ID where AGV parks when idle
      "previous_node": 3, // Integer or null: Last node visited, used for turn direction calculation
      "current_node": 4, // Integer or null: Current position of AGV
      "next_node": 7, // Integer or null: Next node to visit
      "reserved_node": 7, // Integer or null: Node reserved by AGV
      "motion_state": 1, // Integer: AGV state (0=Idle, 1=Moving, 2=Waiting)
      "direction_change": 2, // Integer or null: Turn direction (0=Straight, 1=Reverse, 2=Left, 3=Right)
      "spare_flag": false, // Boolean: Whether AGV uses spare points
      "spare_points": {}, // Object: Map of shared points to spare points
      "initial_path": [5, 6, 7, 8], // Array: Original planned path
      "residual_path": [7, 8], // Array: Remaining nodes to visit
      "cp": [7], // Array: Shared points with other AGVs
      "scp": [], // Array: Sequential shared points
      "active_order": {
        "order_id": 101, // Integer: ID of current order
        "order_date": "2025-05-06", // String: Date of order (YYYY-MM-DD)
        "start_time": "14:30:00", // String: Start time (HH:MM:SS)
        "parking_node": 5, // Integer: Start node
        "storage_node": 7, // Integer: Pickup node
        "workstation_node": 8 // Integer: Delivery node
      }
    }
  ]
  ```

### Create AGV

- **URL**: `/api/agvs/create/`
- **Method**: `POST`
- **Description**: Create new AGV(s)
- **Request Body**: Single AGV or array of AGVs
  ```json
  {
    "agv_id": "integer",
    "preferred_parking_node": "integer"
  }
  ```
- **Response**: `201 Created` - Returns the created AGV(s) data

### Delete AGV

- **URL**: `/api/agvs/delete/{agv_id}/`
- **Method**: `DELETE`
- **Description**: Delete a specific AGV
- **Response**: `200 OK`

### Bulk Delete AGVs

- **URL**: `/api/agvs/bulk-delete/`
- **Method**: `DELETE`
- **Description**: Delete multiple AGVs
- **Request Body**:
  ```json
  {
    "agv_ids": ["integer"]
  }
  ```
- **Response**: `200 OK`

### Update AGV Position

- **URL**: `/api/agvs/update-position/`
- **Method**: `POST`
- **Description**: Update AGV position and get control decisions
- **Request Body**:
  ```json
  {
    "agv_id": 1, // Integer: ID of AGV reporting position
    "current_node": 4 // Integer: Current node AGV has reached
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "success": true, // Boolean: Operation success status
    "message": "AGV moving from node 4 to node 7", // String: Human readable status
    "state": "moving", // String: AGV state - "idle", "moving", or "waiting"
    "next_node": 7, // Integer or null: Next node to visit
    "direction_change": 2, // Integer or null: Turn direction (0=Straight, 1=Reverse, 2=Left, 3=Right)
    "reserved_node": 7, // Integer or null: Node reserved by AGV
    "spare_flag": false, // Boolean: Whether AGV is using spare points
    "spare_points": {}, // Object: Mapping of shared points to spare points
    "moved_from": 3, // Integer or null: Previous position
    "previous_node": 3, // Integer or null: Last node visited
    "residual_path": [7, 8, 9], // Array: Remaining nodes to visit
    "deadlock_resolved": true, // Boolean (optional): Whether a deadlock was resolved
    "deadlock_details": {
      // Object (optional): Details about resolved deadlock
      "deadlocks_resolved": 1,
      "agvs_moved": [2, 3]
    },
    "updated_agvs": [2, 3] // Array (optional): IDs of other AGVs updated
  }
  ```

### Dispatch Orders to AGVs

- **URL**: `/api/agvs/dispatch-orders-to-agvs/`
- **Method**: `POST`
- **Description**: Process orders and assign them to available AGVs
- **Request Body**:
  ```json
  {
    "algorithm": "dijkstra" // String (optional): Pathfinding algorithm to use. Default: "dijkstra"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "success": true, // Boolean: Operation success status
    "message": "2 orders processed successfully", // String: Human readable status
    "processed_orders": [
      // Array: Details of processed orders
      {
        "order_id": 101, // Integer: ID of processed order
        "agv_id": 1, // Integer: ID of assigned AGV
        "initial_path": [5, 6, 7, 8], // Array: Full planned path for the order
        "cp": [7], // Array: Shared points with other AGVs
        "scp": [] // Array: Sequential shared points
      }
    ]
  }
  ```

## Order Management

### List Orders

- **URL**: `/api/orders/get/`
- **Method**: `GET`
- **Description**: Get list of all orders
- **Response**: `200 OK`
  ```json
  [
    {
      "order_id": 101, // Integer: Unique identifier for the order
      "order_date": "2025-05-06", // String: Date of order (YYYY-MM-DD)
      "start_time": "14:30:00", // String: Start time (HH:MM:SS)
      "parking_node": 5, // Integer: Starting node for AGV
      "storage_node": 7, // Integer: Node where items are picked up
      "workstation_node": 8 // Integer: Node where items are delivered
    }
  ]
  ```

### Create Order

- **URL**: `/api/orders/create/`
- **Method**: `POST`
- **Description**: Create new order(s)
- **Request Body**: Single order or array of orders

  ```json
  {
    "order_id": 101, // Integer: Unique identifier for the order
    "order_date": "2025-05-06", // String: Date in YYYY-MM-DD format
    "start_time": "14:30:00", // String: Time in HH:MM:SS format
    "parking_node": 5, // Integer: Node where AGV starts from
    "storage_node": 7, // Integer: Node where items are picked up
    "workstation_node": 8 // Integer: Node where items are delivered
  }
  ```

- **Response**: `201 Created` - Returns the created order(s) data

### Delete Order

- **URL**: `/api/orders/delete/{order_id}/`
- **Method**: `DELETE`
- **Description**: Delete a specific order
- **Response**: `200 OK`

### Bulk Delete Orders

- **URL**: `/api/orders/bulk-delete/`
- **Method**: `DELETE`
- **Description**: Delete multiple orders
- **Request Body**:
  ```json
  {
    "order_ids": ["integer"]
  }
  ```
- **Response**: `200 OK`

## Map Management

### Import Connections

- **URL**: `/api/map/import-connections/`
- **Method**: `POST`
- **Description**: Import connection data from CSV file
- **Request**: Multipart form data with CSV file like `map-connection-and-distance.csv`
- **Response**: `200 OK`

### Import Directions

- **URL**: `/api/map/import-directions/`
- **Method**: `POST`
- **Description**: Import direction data from CSV file
- **Request**: Multipart form data with CSV file like `map-direction.csv`
- **Response**: `200 OK`

### Get Map Data

- **URL**: `/api/map/get/`
- **Method**: `GET`
- **Description**: Get all map data including nodes, connections, and directions
- **Response**: `200 OK`
  ```json
  {
    "nodes": [1, 2, 3, ...], // Array: All unique node IDs in the map
    "connections": [
      {
        "node1": 1, // Integer: Starting node ID
        "node2": 2, // Integer: Ending node ID
        "distance": 10 // Integer: Distance between nodes (10000 means no connection)
      }
    ],
    "directions": [
      {
        "node1": 1, // Integer: Reference node ID
        "node2": 2, // Integer: Target node ID
        "direction": 1 // Integer: Cardinal direction from node1 to node2 (node2 is to the {direction} of node1):
                      // 1 = North
                      // 2 = East
                      // 3 = South
                      // 4 = West
      }
    ]
  }
  ```
- **Error Responses**:
  - `206 Partial Content`: When only some map data is available
    ```json
    {
      "success": false, // Boolean: Operation status
      "message": "Connection data is missing. Please import the connections CSV file.", // String: Error description
      "missing": ["connections"], // Array: Missing data types
      "available": {
        // Object: Available data
        "nodes": [1, 2, 3],
        "directions": [{ "node1": 1, "node2": 2, "direction": 1 }]
      }
    }
    ```
  - `404 Not Found`: When no map data is available
    ```json
    {
      "success": false, // Boolean: Operation status
      "message": "No map data available. Please import both connection and direction data.", // String: Error description
      "missing": ["connections", "directions"] // Array: Missing data types
    }
    ```

### Delete All Map Data

- **URL**: `/api/map/delete/`
- **Method**: `POST`
- **Description**: Delete all map data
- **Response**: `200 OK`

## Error Responses

All endpoints may return the following error responses:

- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Authentication failed or token missing
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

Error response format:

```json
{
  "error": "string",
  "detail": "string" // Optional detailed error message
}
```

## Rate Limiting

Currently, no rate limiting is implemented on the API endpoints.

## Authentication Notes

1. After login, the access token is valid for 60 minutes
2. The refresh token is valid for 7 days
3. Access token is sent as an HTTP-only cookie
4. Include the access token cookie in all authenticated requests
