# SignalWeave — Fintech Market Surveillance MVP

This repo contains a simulated, fintech-focused market surveillance platform designed as a production-style engineering project.

Run backend locally (Python virtualenv):

```bash
cd backend
python -m venv .venv
. .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

Run frontend (Node + Vite):

```bash
cd frontend
npm install
npm run dev
```

The backend exposes a WebSocket at `ws://localhost:8000/ws/ticks` streaming simulated ticks, features, and detector outputs.

Design notes are in-code as comments explaining tradeoffs and why components exist.

Quick DB demo (Docker compose):

1. Start services (backend, frontend, db, pgadmin):

```bash
docker compose up --build
```

2. Open the frontend (Vite) at http://localhost:5173 and you will see the Live Tick Feed and a "Database (demo)" panel with buttons to load recent ticks/anomalies and download CSVs.

3. To view the DB directly use pgAdmin at http://localhost:8080 (login: admin@example.com / admin) and add a server connecting to host `host.docker.internal` (or `localhost` on Linux) port `5432`.

If you prefer not to use Docker, see earlier README instructions to run backend and frontend manually and a one-off Postgres container example.
