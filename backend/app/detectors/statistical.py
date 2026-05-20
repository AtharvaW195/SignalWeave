from __future__ import annotations

from app.core.schemas import DetectorResult, FeatureSnapshot, SourceType, TickEvent


class StatisticalDetector:
    def detect(self, event: TickEvent, features: FeatureSnapshot) -> DetectorResult:
        score = min(1.0, abs(features.z_score) / 4.0 + min(features.volatility * 2.0, 0.35) + min(features.anomaly_history, 0.2))
        if event.source is SourceType.networking:
            score += min(0.2, float(event.metadata.get("packet_loss", 0.0)) * 2.0)
        elif event.source is SourceType.system:
            score += min(0.18, float(event.metadata.get("latency_ms", 0.0)) / 500.0)
        is_anomaly = score >= 0.55 or abs(features.z_score) > 3.0
        reason = "z-score + volatility spike" if is_anomaly else "stable moving window"
        return DetectorResult(layer="statistical", score=round(min(score, 1.0), 3), is_anomaly=is_anomaly, reason=reason)

