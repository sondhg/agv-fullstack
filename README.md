# How to run AGV web app

Pre-requisite: [Docker Desktop](https://www.docker.com/products/docker-desktop) must be installed on your machine.

## 1. Steps to run the app using Docker

### 1.1. First time setup

Clone my code

```bash
git clone https://github.com/sondhg/agv-fullstack.git
cd agv-fullstack
```

All later steps should be run in the `agv-fullstack` directory.

Run the app

```bash
docker compose up --build -d
```

The first time you run this web app, it will take a few minutes. Just wait until the app is up and running. If you wait for a while and error messages are shown in the terminal, press `Ctrl+C` to stop the process and run `docker compose up -d` again.

### 1.2. Stop the app

```bash
docker compose down
```

Later, if you want to run the app again, just run `docker compose up -d`.

### 1.3. Get code changes from GitHub and rebuild the app

```bash
git pull origin main
docker compose down
docker compose up --build -d
```

## 2. Access the app

- Open your browser and go to [http://localhost:5173](http://localhost:5173)
- Follow instructions on the Home page to use the app.
