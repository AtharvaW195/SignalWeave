from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "SignalWeave"
    api_prefix: str = "/api"
    default_window_size: int = 64
    model_name: str = "isolation_forest"
    artifact_dir: Path = Path(__file__).resolve().parents[2] / "artifacts"
    history_limit: int = 240
    tick_interval_seconds: float = 0.15


settings = Settings()
settings.artifact_dir.mkdir(parents=True, exist_ok=True)
