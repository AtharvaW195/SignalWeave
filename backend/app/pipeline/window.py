"""
Sliding window per-symbol for feature computation.
Design:
- Keep a fixed-size deque of recent ticks.
- Expose helper methods to compute simple rolling stats used by detectors and ML features.
"""
from collections import deque
from typing import Deque, Dict, List

class StreamWindow:
    def __init__(self, size: int = 64):
        self.size = size
        self.windows = {}  # symbol -> deque of ticks

    def append(self, tick: Dict):
        sym = tick["symbol"]
        if sym not in self.windows:
            self.windows[sym] = deque(maxlen=self.size)
        self.windows[sym].append(tick)

    def get(self, symbol: str) -> List[Dict]:
        return list(self.windows.get(symbol, []))

    def length(self, symbol: str) -> int:
        return len(self.windows.get(symbol, []))
