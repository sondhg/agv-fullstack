## How to Use the Web App

1. **Clone the repository**:

   ```bash
   git clone https://github.com/sondhg/agv-fullstack.git
   cd agv-fullstack
   ```

2. **Start Backend Services**:

   ```bash
   cd agv_server
   docker-compose up --build
   ```

   This starts the PostgreSQL database, Django backend, and Nginx proxy. Ensure you run these commands in the outer `agv_server` folder containing `manage.py`, NOT the inner `agv_server` folder containing `settings.py`.

3. **Start Frontend Application**:

   Open a new terminal:

   ```bash
   cd frontend
   docker-compose up --build
   ```

4. **Access the Application**:

   - Backend API: [http://localhost:8001](http://localhost:8001) (If you see something here, it means the server is up and working fine. No interaction needed here).
   - Frontend: [http://localhost:5173](http://localhost:5173).

5. **Stop Services**:
   Press `Ctrl+C` in each terminal, then run:

   ```bash
   docker-compose down
   ```

   Execute this in both `agv_server` and `frontend` directories.

6. **Restart the Web App**:

   - Backend:
     ```bash
     cd agv_server
     docker-compose up
     ```
   - Frontend:
     ```bash
     cd frontend
     docker-compose up
     ```

   Access the app at the same URLs as above.
