from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.api import router as api_router
from app.routes.ws import router as ws_router
from app.streams.orchestrator import StreamOrchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.orchestrator = StreamOrchestrator()
    await app.state.orchestrator.start()
    yield
    await app.state.orchestrator.stop()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.include_router(ws_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "ready"}

