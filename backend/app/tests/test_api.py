from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_and_modes_endpoints() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"

        modes = client.get("/api/modes")
        assert modes.status_code == 200
        assert len(modes.json()) == 3
