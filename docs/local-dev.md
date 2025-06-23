# Local Development Setup

This file shows what commands to run to set up a local development environment for the project.

Assume all commands are run from the root of the project directory. Each part is run in a separate terminal.

- Run virtual environment setup

```bash
.venv\Scripts\activate
```

- Run React frontend

```bash
cd frontend
pnpm run dev
```

- Run Redis server (must be running before starting the Django server)

```bash
docker run --rm -p 6379:6379 redis:7
```

- Run Mosquitto MQTT broker (must be running before starting the Django server)

```bash
mosquitto -v
```

- Run Django server

```bash
cd agv_server
py manage.py runserver
```
