from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import AsyncIterator

from app.core.config import settings
from app.core.schemas import SourceType, TickEvent, TickType
from app.utils.time import unix_timestamp


@dataclass
class StreamProfile:
    symbols: list[str]
    tick_type: TickType
    base_value: float
    volatility: float
    volume_range: tuple[int, int]


class TickStreamSimulator:
    def __init__(self) -> None:
        self._rng = random.Random(42)
        self._profiles: dict[SourceType, StreamProfile] = {
            SourceType.fintech: StreamProfile(["AAPL", "MSFT", "NVDA", "TSLA"], TickType.price, 185.0, 2.3, (900, 4200)),
            SourceType.networking: StreamProfile(["NODE_1", "NODE_2", "EDGE_A", "EDGE_B"], TickType.packet, 18.0, 3.8, (300, 1300)),
            SourceType.system: StreamProfile(["CPU_1", "MEM_1", "APP_1", "DB_1"], TickType.metric, 53.0, 5.7, (1, 12)),
        }

    async def stream(self, mode: SourceType) -> AsyncIterator[TickEvent]:
        profile = self._profiles[mode]
        baseline = profile.base_value
        while True:
            symbol = self._rng.choice(profile.symbols)
            drift = self._rng.uniform(-profile.volatility, profile.volatility)
            shock = self._anomaly_shock(mode)
            baseline = max(0.1, baseline + drift + shock)
            volume = self._rng.randint(*profile.volume_range)
            metadata = self._metadata_for(mode, baseline)
            yield TickEvent(
                event_id=f"{mode.value[:3]}-{unix_timestamp()}-{self._rng.randint(1000, 9999)}",
                timestamp=unix_timestamp(),
                source=mode,
                symbol=symbol,
                tick_type=profile.tick_type,
                value=round(baseline, 4),
                volume=volume,
                metadata=metadata,
            )
            await asyncio.sleep(settings.tick_interval_seconds)

    def _anomaly_shock(self, mode: SourceType) -> float:
        roll = self._rng.random()
        if mode is SourceType.fintech and roll < 0.04:
            return self._rng.uniform(8.0, 24.0)
        if mode is SourceType.networking and roll < 0.05:
            return self._rng.uniform(9.0, 18.0)
        if mode is SourceType.system and roll < 0.05:
            return self._rng.uniform(12.0, 30.0)
        return 0.0

    def _metadata_for(self, mode: SourceType, value: float) -> dict[str, float | str]:
        if mode is SourceType.fintech:
            return {
                "latency_ms": round(self._rng.uniform(2.0, 8.0), 2),
                "price_band": "equity",
                "region": self._rng.choice(["us-east-1", "us-west-2", "eu-central-1"]),
            }
        if mode is SourceType.networking:
            return {
                "latency_ms": round(value + self._rng.uniform(1.0, 4.0), 2),
                "packet_loss": round(self._rng.uniform(0.0, 0.12), 3),
                "retransmissions": round(self._rng.uniform(0, 8), 1),
                "region": self._rng.choice(["us-east-1", "ap-south-1", "eu-west-1"]),
            }
        return {
            "latency_ms": round(self._rng.uniform(10.0, 80.0), 2),
            "memory_mb": round(self._rng.uniform(1024.0, 8192.0), 1),
            "load_avg": round(self._rng.uniform(0.2, 5.0), 2),
            "region": self._rng.choice(["us-east-1", "us-west-2", "eu-north-1"]),
        }

