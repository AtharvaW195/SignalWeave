from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field

from app.core.schemas import TickEvent


@dataclass
class StreamWindow:
    size: int
    events: deque[TickEvent] = field(default_factory=deque)

    def add(self, event: TickEvent) -> None:
        self.events.append(event)
        while len(self.events) > self.size:
            self.events.popleft()

    def values(self) -> list[float]:
        return [event.value for event in self.events]

    def anomaly_history(self) -> float:
        if not self.events:
            return 0.0
        return sum(1 for event in self.events if event.metadata.get("is_anomaly")) / len(self.events)


class WindowRegistry:
    def __init__(self, size: int = 64) -> None:
        self.size = size
        self._windows: dict[str, StreamWindow] = defaultdict(lambda: StreamWindow(size=size))

    def window_for(self, stream_key: str) -> StreamWindow:
        return self._windows[stream_key]

