# SignalWeave

SignalWeave is a production-style real-time event intelligence platform for fintech, networking, and system monitoring telemetry.

## What it includes

- FastAPI backend with REST and WebSocket streaming
- Unified tick schema across all domains
- Sliding-window feature engineering
- Rule-based, statistical, and ML anomaly detection
- React + TypeScript observability dashboard
- Synthetic data simulation and reusable training artifacts
- Docker assets for local deployment

## Local run

Backend:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Test

```bash
cd backend
python -m pytest app/tests -q
```
