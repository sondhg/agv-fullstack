# Running the AGV Web App with Docker

Pre-requisite: You must have Docker Desktop installed.

## Quick Start

First time, run:

```bash
docker compose up --build
```

This will start:

- Frontend at http://localhost:5173
- Backend at http://localhost:8000

Later, you can just run:

```bash
docker compose up
```

## Full Reset

If you need to completely reset:

```bash
docker compose down
docker compose up --build
```

Run Redis via Docker with command

```bash
docker run --rm -p 6379:6379 redis:7
```
