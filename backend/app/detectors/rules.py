from __future__ import annotations

from app.core.schemas import DetectorResult, FeatureSnapshot, SourceType, TickEvent


class RuleBasedDetector:
    def detect(self, event: TickEvent, features: FeatureSnapshot) -> DetectorResult:
        if event.source is SourceType.fintech:
            if abs(features.delta) > 16 or features.spike_intensity > 3.2:
                return DetectorResult(layer="rule", score=0.93, is_anomaly=True, reason="price spike or suspicious jump")
        elif event.source is SourceType.networking:
            if event.metadata.get("packet_loss", 0.0) > 0.08 or features.rolling_std > 7:
                return DetectorResult(layer="rule", score=0.9, is_anomaly=True, reason="packet loss or reliability breach")
        else:
            if event.value > 88 or event.metadata.get("memory_mb", 0.0) > 7600:
                return DetectorResult(layer="rule", score=0.92, is_anomaly=True, reason="system saturation threshold breached")
        return DetectorResult(layer="rule", score=0.08, is_anomaly=False, reason="within domain guardrails")

