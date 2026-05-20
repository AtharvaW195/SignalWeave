from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.core.config import settings
from app.core.schemas import AggregatedDecision, FeatureSnapshot, TickEvent
from app.detectors.aggregation import DecisionAggregator
from app.detectors.rules import RuleBasedDetector
from app.detectors.statistical import StatisticalDetector
from app.ml.inference import ModelService
from app.pipeline.window import WindowRegistry


@dataclass
class ProcessedEvent:
    tick: TickEvent
    features: FeatureSnapshot
    decision: AggregatedDecision


class EventProcessor:
    def __init__(self) -> None:
        self.windows = WindowRegistry(size=settings.default_window_size)
        self.rule_detector = RuleBasedDetector()
        self.stat_detector = StatisticalDetector()
        self.model_service = ModelService()
        self.aggregator = DecisionAggregator()

    def _key(self, event: TickEvent) -> str:
        return f"{event.source.value}:{event.symbol}:{event.tick_type.value}"

    def _features_for(self, event: TickEvent) -> FeatureSnapshot:
        window = self.windows.window_for(self._key(event))
        values = np.asarray(window.values() + [event.value], dtype=float)
        mean = float(values.mean())
        std = float(values.std(ddof=0)) if values.size > 1 else 0.0
        previous = window.events[-1].value if window.events else event.value
        delta = float(event.value - previous)
        ema = self._ema(values)
        roc = float(delta / max(abs(previous), 1e-6))
        z_score = float((event.value - mean) / max(std, 1e-6))
        volatility = float(std / max(mean, 1e-6))
        spike_intensity = float(abs(delta) / max(std, 1e-6))
        anomaly_history = window.anomaly_history()
        window.add(event)
        return FeatureSnapshot(
            rolling_mean=mean,
            rolling_std=std,
            z_score=z_score,
            ema=ema,
            volatility=volatility,
            delta=delta,
            rate_of_change=roc,
            spike_intensity=spike_intensity,
            anomaly_history=anomaly_history,
            history_depth=len(window.events),
        )

    def _ema(self, values: np.ndarray, alpha: float = 0.25) -> float:
        ema = float(values[0])
        for value in values[1:]:
            ema = alpha * float(value) + (1 - alpha) * ema
        return ema

    def process(self, event: TickEvent) -> ProcessedEvent:
        features = self._features_for(event)
        rule_result = self.rule_detector.detect(event, features)
        stat_result = self.stat_detector.detect(event, features)
        ml_result = self.model_service.predict(event.source, features)
        decision = self.aggregator.combine(event, features, rule_result, stat_result, ml_result)
        event.metadata = {**event.metadata, "is_anomaly": decision.is_anomaly, "severity": decision.severity}
        return ProcessedEvent(tick=event, features=features, decision=decision)

