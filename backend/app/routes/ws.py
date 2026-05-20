from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.schemas import SourceType

router = APIRouter(prefix="/ws")


@router.websocket("/stream/{mode}")
async def stream(websocket: WebSocket, mode: SourceType) -> None:
    await websocket.accept()
    orchestrator = websocket.app.state.orchestrator
    queue = await orchestrator.subscribe(mode)
    try:
        await websocket.send_json({"type": "history", "mode": mode.value, "events": [item.model_dump() for item in orchestrator.history(mode)]})
        while True:
            payload = await queue.get()
            await websocket.send_json({"type": "tick", "payload": payload})
    except WebSocketDisconnect:
        orchestrator.unsubscribe(mode, queue)
    finally:
        orchestrator.unsubscribe(mode, queue)

