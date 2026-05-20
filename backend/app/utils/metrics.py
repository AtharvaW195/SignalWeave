from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class RollingCounter:
    window_size: int = 128
    values: deque[float] = field(default_factory=lambda: deque(maxlen=128))

    def add(self, value: float) -> None:
        self.values.append(value)

    def average(self) -> float:
        if not self.values:
            return 0.0
        return sum(self.values) / len(self.values)

