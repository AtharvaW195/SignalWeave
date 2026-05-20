from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    fintech = "fintech"
    networking = "networking"
    system = "system"


class TickType(str, Enum):
    price = "price"
    packet = "packet"
    metric = "metric"


class TickEvent(BaseModel):
    event_id: str
    timestamp: int
    source: SourceType
    symbol: str
    tick_type: TickType
    value: float
    volume: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class FeatureSnapshot(BaseModel):
    rolling_mean: float
    rolling_std: float
    z_score: float
    ema: float
    volatility: float
    delta: float
    rate_of_change: float
    spike_intensity: float
    anomaly_history: float
    history_depth: int


class DetectorResult(BaseModel):
    layer: Literal["rule", "statistical", "ml"]
    score: float
    is_anomaly: bool
    reason: str


class AggregatedDecision(BaseModel):
    event_id: str
    source: SourceType
    symbol: str
    anomaly_score: float
    confidence: float
    severity: Literal["low", "medium", "high", "critical"]
    is_anomaly: bool
    reason: str
    model: str
    features: FeatureSnapshot
    tick: TickEvent
    detector_breakdown: dict[str, DetectorResult]


class StreamMetrics(BaseModel):
    mode: SourceType
    throughput_per_second: float
    average_latency_ms: float
    anomaly_rate: float
    total_events: int
    active_subscribers: int


class ModeSummary(BaseModel):
    mode: SourceType
    description: str

