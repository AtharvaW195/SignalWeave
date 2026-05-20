from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

from app.core.config import settings
from app.core.schemas import FeatureSnapshot, SourceType


FEATURE_ORDER = [
    "rolling_mean",
    "rolling_std",
    "z_score",
    "ema",
    "volatility",
    "delta",
    "rate_of_change",
    "spike_intensity",
    "anomaly_history",
    "history_depth",
]


@dataclass
class ModelBundle:
    isolation_forest: IsolationForest
    one_class_svm: Pipeline


class SyntheticTrainingSet:
    def __init__(self, seed: int = 11) -> None:
        self._rng = np.random.default_rng(seed)

    def build(self, source: SourceType, rows: int = 700) -> tuple[np.ndarray, np.ndarray]:
        base = self._base_for(source)
        normal = self._rng.normal(loc=base, scale=base * 0.08, size=(rows, len(FEATURE_ORDER)))
        anomalies = self._inject_anomalies(normal[: max(12, rows // 10)].copy(), source)
        x = np.vstack([normal, anomalies])
        y = np.concatenate([np.zeros(len(normal)), np.ones(len(anomalies))])
        return x, y

    def _base_for(self, source: SourceType) -> np.ndarray:
        if source is SourceType.fintech:
            return np.array([185, 2, 0.1, 184, 0.02, 0.2, 0.01, 0.7, 0.05, 18], dtype=float)
        if source is SourceType.networking:
            return np.array([20, 4.5, 0.08, 19, 0.18, 0.8, 0.04, 1.0, 0.07, 18], dtype=float)
        return np.array([58, 6.5, 0.12, 57, 0.14, 1.0, 0.08, 1.3, 0.09, 18], dtype=float)

    def _inject_anomalies(self, data: np.ndarray, source: SourceType) -> np.ndarray:
        if source is SourceType.fintech:
            data[:, 0] += self._rng.normal(22, 5, size=len(data))
            data[:, 5] += self._rng.normal(13, 4, size=len(data))
        elif source is SourceType.networking:
            data[:, 1] += self._rng.normal(11, 2, size=len(data))
            data[:, 4] += self._rng.normal(0.4, 0.1, size=len(data))
        else:
            data[:, 0] += self._rng.normal(21, 4, size=len(data))
            data[:, 3] += self._rng.normal(18, 5, size=len(data))
        data[:, 2] += self._rng.normal(3.5, 0.7, size=len(data))
        data[:, 7] += self._rng.normal(2.5, 0.7, size=len(data))
        return data


class ModelTrainer:
    def __init__(self, artifact_dir: Path | None = None) -> None:
        self.artifact_dir = artifact_dir or settings.artifact_dir
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def model_path(self, source: SourceType, name: str) -> Path:
        return self.artifact_dir / f"{source.value}_{name}.joblib"

    def train(self, source: SourceType) -> ModelBundle:
        x, _ = SyntheticTrainingSet().build(source)
        isolation_forest = IsolationForest(contamination=0.08, random_state=11, n_estimators=120)
        isolation_forest.fit(x)

        one_class_svm = Pipeline([
            ("scaler", StandardScaler()),
            ("svm", OneClassSVM(nu=0.08, gamma="scale")),
        ])
        one_class_svm.fit(x)

        bundle = ModelBundle(isolation_forest=isolation_forest, one_class_svm=one_class_svm)
        joblib.dump(bundle.isolation_forest, self.model_path(source, "isolation_forest"))
        joblib.dump(bundle.one_class_svm, self.model_path(source, "one_class_svm"))
        return bundle

    def load_or_train(self, source: SourceType) -> ModelBundle:
        iso_path = self.model_path(source, "isolation_forest")
        svm_path = self.model_path(source, "one_class_svm")
        if iso_path.exists() and svm_path.exists():
            return ModelBundle(isolation_forest=joblib.load(iso_path), one_class_svm=joblib.load(svm_path))
        return self.train(source)


def feature_vector(features: FeatureSnapshot) -> np.ndarray:
    return np.asarray([getattr(features, name) for name in FEATURE_ORDER], dtype=float).reshape(1, -1)

