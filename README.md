# How to run AGV web app

Pre-requisite: [Docker Desktop](https://www.docker.com/products/docker-desktop) must be installed on your machine.

1. **Clone repo**:

   ```bash
   git clone https://github.com/sondhg/agv-fullstack.git
   cd agv-fullstack
   ```

2. **Run PostgreSQL database and Django backend server**:

   Open the FIRST terminal:

   ```bash
   cd agv_server
   docker compose up -d db
   docker compose run web python manage.py migrate
   docker compose up
   ```

   Ensure you run these commands in the outer `agv_server` folder containing `manage.py`, NOT the inner `agv_server` folder containing `settings.py`.

3. **Run React frontend**:

   Open the SECOND terminal:

   ```bash
   cd frontend
   docker compose up --build
   ```

4. **Access the app**:

   - Backend API: [http://localhost:8000](http://localhost:8001) (If you see something here, it means the server is up and working fine. No interaction needed here).
   - Frontend: [http://localhost:5173](http://localhost:5173).

5. **Stop services**:
   Press `Ctrl+C` in each terminal then run:

   ```bash
   docker compose down
   ```

   Execute this in both `agv_server` and `frontend` directories.

6. **Restart the web app**:

   If you did all steps above at least once, then later, when you want to run the app again, simply open 2 terminals and run `docker compose up` in each directory

   - Backend:
     ```bash
     cd agv_server
     docker compose up
     ```
   - Frontend:
     ```bash
     cd frontend
     docker compose up
     ```

   Access the app at the same URLs as above.
