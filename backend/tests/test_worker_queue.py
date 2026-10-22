from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_queue_health_direct_sync_mode(client: TestClient, monkeypatch):
    """Verify queue-health reporting in default synchronous / free-tier cloud mode."""
    monkeypatch.setattr(settings, "REQUIRE_REDIS", False)
    response = client.get("/queue-health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "smart-farming-backend"
    assert data["mode"] == "direct_sync"
    assert data["redis_connected"] is False
    assert data["worker_healthy"] is True
    assert "Direct pipeline execution active" in data["details"]["message"]


def test_queue_health_worker_mode_pool_missing(client: TestClient, monkeypatch):
    """Verify queue-health reports degraded state when REQUIRE_REDIS=True but arq_pool is uninitialized."""
    monkeypatch.setattr(settings, "REQUIRE_REDIS", True)
    monkeypatch.setattr(app.state, "arq_pool", None)

    response = client.get("/queue-health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["mode"] == "arq_worker"
    assert data["worker_healthy"] is False
    assert "ARQ pool is not connected" in data["details"]["error"]


def test_queue_health_worker_mode_healthy(client: TestClient, monkeypatch):
    """Verify queue-health reports active queue metrics when ARQ pool is live."""
    monkeypatch.setattr(settings, "REQUIRE_REDIS", True)

    mock_pool = MagicMock()
    mock_pool.ping = AsyncMock(return_value=True)
    mock_pool.zcard = AsyncMock(return_value=3)
    monkeypatch.setattr(app.state, "arq_pool", mock_pool)

    response = client.get("/queue-health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["mode"] == "arq_worker"
    assert data["redis_connected"] is True
    assert data["worker_healthy"] is True
    assert data["pending_jobs"] == 3


def test_readiness_worker_guard(client: TestClient, monkeypatch):
    """Verify /ready endpoint reports 503 if REQUIRE_REDIS=True and worker pool is disconnected."""
    monkeypatch.setattr(settings, "REQUIRE_REDIS", True)
    monkeypatch.setattr(app.state, "arq_pool", None)

    response = client.get("/ready")
    assert response.status_code == 503
    assert "Worker queue is not ready" in response.json()["detail"]


def test_prometheus_metrics_endpoint(client: TestClient):
    """Verify Prometheus /metrics endpoint exposes system uptime, status, and prediction counters."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    body = response.text
    assert "smart_farming_uptime_seconds" in body
    assert "smart_farming_db_status" in body
    assert "smart_farming_predictions_total" in body
    assert "smart_farming_worker_mode_enabled" in body

