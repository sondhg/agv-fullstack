# AGV Control Web App (ReactJS Frontend)

> GUI: graphical user interface

## Clone my code

```bash
git clone https://github.com/sondhg/agv-frontend-typescript.git
cd agv-frontend-typescript
```

## Required installations

- [NodeJS](https://nodejs.org/en).

## Run the app

**IMPORTANT**: Since I can't use Hoang Anh's server yet, I wrote a backend Django server. Please use it, otherwise the app won't work.

### Run GUI with agv-frontend-typescript

#### Method 1: Run manually

```bash
npm i
npm run dev
o
```

The command `o` means "open", it will redirect you to [http://localhost:5173](http://localhost:5173). Here you see the GUI.

If you wanna stop the GUI, press `Ctrl+C` or `q` in the terminal.

If you wanna run the GUI again later, you just have to run

```bash
npm run dev
```

#### Method 2: Use Docker

- Download [Docker Desktop](https://www.docker.com/products/docker-desktop).
- Open Docker Desktop. Make sure it's running.
- Open a terminal in the project directory `agv-frontend-typescript`, then run:

```bash
docker-compose up --build
```

- Open your browser and navigate to http://localhost:5173 to see the GUI.

- To stop the GUI, press `Ctrl+C`, then press `q` in the terminal you used to run docker-compose.

- If you wanna run the GUI again later, you just have to run

```bash
docker-compose up
```

### Run my-django-server

Clone and follow the README instructions in my [my-django-server](https://github.com/sondhg/my-django-server) repo to have a PostgreSQL database at port 5432 and a Django server at port 8000 like I do.

## Using the GUI

1. Use the sidebar to navigate between pages.
2. Must login to access ADMIN pages (Orders, AGVs, Schedules, Dashboard)

## Important files

Use `Ctrl+P` in VSCode to search for these files.

- API functions and configs

  - Files in `services/APIs` folder
  - `axiosCustomize.tsx`

- **WebSocket for live data** (testing with Binance API):
  - Files in `src/app/admin/dashboard` folder
  - WebSocket URL: wss://stream.binance.com:9443/ws/btcusdt@aggTrade

## Learning resources

- [React Hook YouTube Playlist](https://www.youtube.com/playlist?list=PLncHg6Kn2JT7QbvdNNAmQZLqWchnJEoH5)
- [React Hook PDF](https://drive.google.com/drive/folders/1WYAyusS4m498bqCR8iyzRYmS26zGh8g-)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
