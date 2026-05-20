from __future__ import annotations

from app.core.schemas import AggregatedDecision, DetectorResult, FeatureSnapshot, TickEvent


class DecisionAggregator:
    def combine(
        self,
        event: TickEvent,
        features: FeatureSnapshot,
        rule_result: DetectorResult,
        stat_result: DetectorResult,
        ml_result: DetectorResult,
    ) -> AggregatedDecision:
        weighted_score = (
            rule_result.score * 0.35
            + stat_result.score * 0.3
            + ml_result.score * 0.35
        )
        confidence = min(0.99, 0.5 + weighted_score / 2.0)
        is_anomaly = weighted_score >= 0.58 or rule_result.is_anomaly and (stat_result.is_anomaly or ml_result.is_anomaly)
        severity = self._severity(weighted_score)
        reason_parts = [result.reason for result in (rule_result, stat_result, ml_result) if result.is_anomaly]
        reason = " + ".join(reason_parts) if reason_parts else "normal operating envelope"
        return AggregatedDecision(
            event_id=event.event_id,
            source=event.source,
            symbol=event.symbol,
            anomaly_score=round(weighted_score, 3),
            confidence=round(confidence, 3),
            severity=severity,
            is_anomaly=is_anomaly,
            reason=reason,
            model=ml_result.reason if ml_result.is_anomaly else "isolation_forest",
            features=features,
            tick=event,
            detector_breakdown={
                "rule": rule_result,
                "statistical": stat_result,
                "ml": ml_result,
            },
        )

    def _severity(self, score: float) -> str:
        if score >= 0.85:
            return "critical"
        if score >= 0.7:
            return "high"
        if score >= 0.5:
            return "medium"
        return "low"

