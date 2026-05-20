from __future__ import annotations

from dataclasses import dataclass, field

from app.core.schemas import DetectorResult, FeatureSnapshot, SourceType
from app.ml.trainer import ModelTrainer, feature_vector


@dataclass
class ModelService:
    trainer: ModelTrainer = field(default_factory=ModelTrainer)

    def predict(self, source: SourceType, features: FeatureSnapshot) -> DetectorResult:
        bundle = self.trainer.load_or_train(source)
        vector = feature_vector(features)
        iso_score = float(bundle.isolation_forest.decision_function(vector)[0])
        iso_pred = int(bundle.isolation_forest.predict(vector)[0])
        svm_pred = int(bundle.one_class_svm.predict(vector)[0])
        svm_score = float(bundle.one_class_svm.decision_function(vector)[0])
        anomaly_score = self._normalize(iso_score, svm_score, iso_pred, svm_pred)
        is_anomaly = anomaly_score >= 0.58 or iso_pred == -1 or svm_pred == -1
        reason = "isolation_forest" if abs(iso_score) <= abs(svm_score) else "one_class_svm"
        return DetectorResult(layer="ml", score=round(anomaly_score, 3), is_anomaly=is_anomaly, reason=reason)

    def _normalize(self, iso_score: float, svm_score: float, iso_pred: int, svm_pred: int) -> float:
        base = 0.55 + min(0.35, abs(iso_score) * 0.12 + abs(svm_score) * 0.18)
        if iso_pred == -1:
            base += 0.08
        if svm_pred == -1:
            base += 0.08
        return float(min(0.99, max(0.0, base)))

