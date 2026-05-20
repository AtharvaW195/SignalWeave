from __future__ import annotations

from app.core.schemas import SourceType, TickEvent, TickType
from app.pipeline.processor import EventProcessor


def test_processor_flags_outlier_fintech_tick() -> None:
    processor = EventProcessor()
    baseline = TickEvent(
        event_id="t-1",
        timestamp=1710000000,
        source=SourceType.fintech,
        symbol="AAPL",
        tick_type=TickType.price,
        value=145.0,
        volume=1200,
        metadata={"latency_ms": 4.0, "region": "us-east-1"},
    )
    processor.process(baseline)

    anomaly = TickEvent(
        event_id="t-2",
        timestamp=1710000001,
        source=SourceType.fintech,
        symbol="AAPL",
        tick_type=TickType.price,
        value=189.5,
        volume=6000,
        metadata={"latency_ms": 11.0, "region": "us-east-1"},
    )
    result = processor.process(anomaly)

    assert result.decision.anomaly_score >= 0.5
    assert result.decision.features.spike_intensity > 0

