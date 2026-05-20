from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass, field

from app.core.config import settings
from app.core.schemas import AggregatedDecision, SourceType, StreamMetrics, TickEvent
from app.pipeline.processor import EventProcessor
from app.streams.simulator import TickStreamSimulator


@dataclass
class ModeState:
    subscribers: list[asyncio.Queue[dict]] = field(default_factory=list)
    history: deque[AggregatedDecision] = field(default_factory=lambda: deque(maxlen=settings.history_limit))
    started_at: float = field(default_factory=time.time)
    events_seen: int = 0
    anomalies_seen: int = 0


class StreamOrchestrator:
    def __init__(self) -> None:
        self.simulator = TickStreamSimulator()
        self.processor = EventProcessor()
        self._states: dict[SourceType, ModeState] = {source: ModeState() for source in SourceType}
        self._tasks: dict[SourceType, asyncio.Task[None]] = {}

    async def start(self) -> None:
        for source in SourceType:
            if source not in self._tasks or self._tasks[source].done():
                self._tasks[source] = asyncio.create_task(self._run_mode(source))

    async def stop(self) -> None:
        for task in self._tasks.values():
            task.cancel()
        await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._tasks.clear()

    def history(self, mode: SourceType) -> list[AggregatedDecision]:
        return list(self._states[mode].history)

    def metrics(self, mode: SourceType) -> StreamMetrics:
        state = self._states[mode]
        elapsed = max(time.time() - state.started_at, 1e-6)
        return StreamMetrics(
            mode=mode,
            throughput_per_second=round(state.events_seen / elapsed, 2),
            average_latency_ms=round(18.0 + (state.anomalies_seen * 0.9), 2),
            anomaly_rate=round(state.anomalies_seen / max(state.events_seen, 1), 3),
            total_events=state.events_seen,
            active_subscribers=len(state.subscribers),
        )

    async def subscribe(self, mode: SourceType) -> asyncio.Queue[dict]:
        queue: asyncio.Queue[dict] = asyncio.Queue()
        self._states[mode].subscribers.append(queue)
        return queue

    def unsubscribe(self, mode: SourceType, queue: asyncio.Queue[dict]) -> None:
        state = self._states[mode]
        state.subscribers = [subscriber for subscriber in state.subscribers if subscriber is not queue]

    async def analyze(self, event: TickEvent) -> AggregatedDecision:
        processed = self.processor.process(event)
        decision = processed.decision
        state = self._states[event.source]
        state.history.append(decision)
        state.events_seen += 1
        if decision.is_anomaly:
            state.anomalies_seen += 1
        await self._broadcast(event.source, decision.model_dump())
        return decision

    async def _broadcast(self, mode: SourceType, payload: dict) -> None:
        for queue in list(self._states[mode].subscribers):
            await queue.put(payload)

    async def _run_mode(self, mode: SourceType) -> None:
        async for tick in self.simulator.stream(mode):
            await self.analyze(tick)

