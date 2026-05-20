from __future__ import annotations

import time


def unix_timestamp() -> int:
    return int(time.time())


def monotonic_ms() -> float:
    return time.perf_counter() * 1000.0

