## Backend Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/sondhg/agv-fullstack.git
   cd agv-fullstack/backend
   ```

2. **Set up a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r agv_server/requirements.txt
   ```

4. **Set up the PostgreSQL database**:

   - **Using pgAdmin4**:

     1. Open pgAdmin4 and log in.
     2. Right-click on "Servers" and select "Create > Server...".
     3. In the "General" tab, name your server (e.g., `PostgreSQL 17`).
     4. In the "Connection" tab, fill in the following details:
        - **Host name/address**: `localhost`
        - **Port**: `5432`
        - **Username**: `postgres` (or your PostgreSQL username)
        - **Password**: `12345678` (or your PostgreSQL password)
     5. Click "Save" to create the server.
     6. Expand the server in the left-hand menu, right-click on the server name (e.g., `PostgreSQL 17`), and select "Create > Database...".
     7. Name the database `agv_backend` and click "Save".

   - **Update the database credentials**:
     Open the `backend/agv_server/agv_server/settings.py` file and ensure the `DATABASES` section matches your setup:
     ```python
     DATABASES = {
           "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "agv_backend",
                "USER": "postgres",  # Replace with your PostgreSQL username if different
                "PASSWORD": "12345678",  # Replace with your PostgreSQL password if different
                "HOST": "localhost",
                "PORT": "5432",
           }
     }
     ```

5. **Run migrations**:

   Navigate to the `backend/agv_server` directory:

   ```bash
   cd agv_server
   ```

   Then run the following commands:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Start the backend server**:

   Ensure you are still in the `backend/agv_server` directory:

   ```bash
   python manage.py runserver
   ```

   The backend server will be running at `http://127.0.0.1:8000/`. You must not close this terminal when the server is running, or else the server will be shut down.

## Frontend Setup

1. **Navigate to the frontend directory**:

   From the root of the project `agv-fullstack`, open another terminal, run:

   ```bash
   cd frontend
   ```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Start the graphical user interface**:

   ```bash
   npm run dev
   ```

   The frontend GUI will be running at `http://localhost:5173/`.

## Running the Application

1. Open your browser and navigate to `http://localhost:5173/`.
2. Use the application as per the provided features.
