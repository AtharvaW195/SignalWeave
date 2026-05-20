from __future__ import annotations

from fastapi import APIRouter, Request

from app.core.schemas import ModeSummary, SourceType, TickEvent

router = APIRouter(prefix="/api")


@router.get("/health")
async def health(request: Request) -> dict[str, object]:
    orchestrator = request.app.state.orchestrator
    return {
        "status": "ok",
        "modes": [orchestrator.metrics(source).model_dump() for source in SourceType],
    }


@router.get("/modes", response_model=list[ModeSummary])
async def modes() -> list[ModeSummary]:
    return [
        ModeSummary(mode=SourceType.fintech, description="Market tick and trade surveillance"),
        ModeSummary(mode=SourceType.networking, description="Packet reliability and latency monitoring"),
        ModeSummary(mode=SourceType.system, description="Infrastructure and system health detection"),
    ]


@router.get("/history/{mode}")
async def history(mode: SourceType, request: Request) -> dict[str, object]:
    orchestrator = request.app.state.orchestrator
    return {"mode": mode.value, "events": [decision.model_dump() for decision in orchestrator.history(mode)]}


@router.post("/analyze")
async def analyze(event: TickEvent, request: Request) -> dict[str, object]:
    orchestrator = request.app.state.orchestrator
    decision = await orchestrator.analyze(event)
    return decision.model_dump()

