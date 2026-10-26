from __future__ import annotations

import asyncio
import hashlib
import time
from unittest.mock import AsyncMock, patch

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.events import prediction_hub
from app.main import app

client = TestClient(app)

TEST_SIGNING_KEY_CURRENT = "sigkey_current_test_1234567890abcdef"
TEST_SIGNING_KEY_NEXT = "sigkey_next_test_0987654321fedcba"
TEST_CRON_SECRET = "test_cron_secret_token_abcdef123456"


@pytest.fixture(autouse=True)
def configure_test_cron_keys(monkeypatch):
    monkeypatch.setattr(settings, "DEBUG", False)
    monkeypatch.setattr(settings, "CRON_SECRET", TEST_CRON_SECRET)
    monkeypatch.setattr(settings, "QSTASH_CURRENT_SIGNING_KEY", TEST_SIGNING_KEY_CURRENT)
    monkeypatch.setattr(settings, "QSTASH_NEXT_SIGNING_KEY", TEST_SIGNING_KEY_NEXT)
    monkeypatch.setattr(settings, "US_EAST_1_QSTASH_CURRENT_SIGNING_KEY", "")
    monkeypatch.setattr(settings, "US_EAST_1_QSTASH_NEXT_SIGNING_KEY", "")


def test_unauthenticated_cron_rejected():
    """Requests without Upstash-Signature or CRON_SECRET must be rejected with 401."""
    resp = client.post("/api/v1/internal/cron/weather-risks")
    assert resp.status_code == 401
    assert "Missing Upstash-Signature" in resp.json().get("detail", "")


def test_invalid_signature_rejected():
    """Requests with malformed or tampered signatures must return 401."""
    resp = client.post(
        "/api/v1/internal/cron/weather-risks",
        headers={"Upstash-Signature": "invalid.tampered.jwt_signature"},
    )
    assert resp.status_code == 401
    assert "verification failed" in resp.json().get("detail", "")


def test_expired_signature_rejected():
    """Requests with expired JWT signature must return 401."""
    expired_token = jwt.encode(
        {"iss": "Upstash", "sub": "https://api/internal/cron/weather-risks", "exp": int(time.time()) - 60},
        TEST_SIGNING_KEY_CURRENT,
        algorithm="HS256",
    )
    resp = client.post(
        "/api/v1/internal/cron/weather-risks",
        headers={"Upstash-Signature": expired_token},
    )
    assert resp.status_code == 401
    assert "expired" in resp.json().get("detail", "").lower()


def test_wrong_key_signature_rejected():
    """JWT signed with an unknown secret key must return 401."""
    unknown_token = jwt.encode(
        {"iss": "Upstash", "sub": "https://api/internal/cron/weather-risks", "exp": int(time.time()) + 300},
        "wrong_secret_key_that_is_not_configured",
        algorithm="HS256",
    )
    resp = client.post(
        "/api/v1/internal/cron/weather-risks",
        headers={"Upstash-Signature": unknown_token},
    )
    assert resp.status_code == 401


@patch("app.services.weather.proactive.evaluate_weather_risks", new_callable=AsyncMock)
def test_valid_cron_secret_bearer_accepted(mock_eval):
    """Requests with valid Authorization: Bearer <CRON_SECRET> must succeed."""
    mock_eval.return_value = None
    resp = client.post(
        "/api/v1/internal/cron/weather-risks",
        headers={"Authorization": f"Bearer {TEST_CRON_SECRET}"},
    )
    assert resp.status_code == 200
    assert resp.json().get("status") == "success"
    mock_eval.assert_awaited_once()


@patch("app.services.weather.proactive.evaluate_weather_risks", new_callable=AsyncMock)
def test_valid_x_cron_secret_header_accepted(mock_eval):
    """Requests with valid X-Cron-Secret header must succeed."""
    mock_eval.return_value = None
    resp = client.post(
        "/api/v1/internal/cron/weather-risks",
        headers={"X-Cron-Secret": TEST_CRON_SECRET},
    )
    assert resp.status_code == 200
    assert resp.json().get("status") == "success"
    mock_eval.assert_awaited_once()


@patch("app.services.weather.proactive.evaluate_weather_risks", new_callable=AsyncMock)
def test_qstash_current_signing_key_accepted(mock_eval):
    """Valid JWT signed with QSTASH_CURRENT_SIGNING_KEY must be accepted."""
    mock_eval.return_value = None
    valid_jwt = jwt.encode(
        {"iss": "Upstash", "sub": "https://api/v1/internal/cron/weather-risks", "exp": int(time.time()) + 300},
        TEST_SIGNING_KEY_CURRENT,
        algorithm="HS256",
    )
    resp = client.post(
        "/api/v1/internal/cron/weather-risks",
        headers={"Upstash-Signature": valid_jwt},
    )
    assert resp.status_code == 200
    assert resp.json().get("status") == "success"
    mock_eval.assert_awaited_once()


@patch("app.services.weather.proactive.evaluate_weather_risks", new_callable=AsyncMock)
def test_qstash_next_signing_key_rotation_accepted(mock_eval):
    """Valid JWT signed with QSTASH_NEXT_SIGNING_KEY must be accepted (key rotation)."""
    mock_eval.return_value = None
    next_jwt = jwt.encode(
        {"iss": "Upstash", "sub": "https://api/v1/internal/cron/weather-risks", "exp": int(time.time()) + 300},
        TEST_SIGNING_KEY_NEXT,
        algorithm="HS256",
    )
    resp = client.post(
        "/api/v1/internal/cron/weather-risks",
        headers={"Upstash-Signature": next_jwt},
    )
    assert resp.status_code == 200
    assert resp.json().get("status") == "success"
    mock_eval.assert_awaited_once()


def test_body_hash_mismatch_rejected():
    """If body claim is present in JWT, mismatch against body content must be rejected."""
    payload = b'{"test": "payload"}'
    fake_sha = hashlib.sha256(b'different payload').hexdigest()
    token = jwt.encode(
        {
            "iss": "Upstash",
            "sub": "https://api/v1/internal/cron/weather-risks",
            "body": fake_sha,
            "exp": int(time.time()) + 300,
        },
        TEST_SIGNING_KEY_CURRENT,
        algorithm="HS256",
    )
    resp = client.post(
        "/api/v1/internal/cron/weather-risks",
        headers={"Upstash-Signature": token},
        content=payload,
    )
    assert resp.status_code == 401
    assert "verification failed" in resp.json().get("detail", "")


@patch("app.core.storage.purge_orphaned_blobs")
@patch("app.core.storage.prune_cached_audio")
@patch("app.core.storage.prune_unflagged_heatmaps")
def test_blob_purge_endpoint_execution(mock_heatmaps, mock_audio, mock_blobs):
    """Storage purge cron endpoint executes cleanups and returns statistics."""
    mock_blobs.return_value = {"purged_raw": 2, "purged_processed": 1}
    mock_audio.return_value = {"pruned_audio_files": 5}
    mock_heatmaps.return_value = {"pruned_heatmaps": 3}

    resp = client.post(
        "/api/v1/internal/cron/purge-blobs",
        headers={"Authorization": f"Bearer {TEST_CRON_SECRET}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "success"
    assert data["orphaned_blobs"]["purged_raw"] == 2
    assert data["pruned_audio"]["pruned_audio_files"] == 5
    assert data["pruned_heatmaps"]["pruned_heatmaps"] == 3


@pytest.mark.anyio
async def test_prediction_status_hub_streaming():
    """In-memory PredictionStatusHub publishes and streams events with minimal latency."""
    test_id = 99999
    received_events = []

    async def subscriber():
        async for event in prediction_hub.subscribe(test_id):
            received_events.append(event)
            if event.get("stage") == "completed":
                break

    sub_task = asyncio.create_task(subscriber())
    await asyncio.sleep(0.01)

    t0 = time.perf_counter()
    prediction_hub.publish_sync(test_id, {"stage": "initialization", "status": "completed"})
    await prediction_hub.publish(test_id, {"stage": "crop_routing", "status": "completed"})
    await prediction_hub.publish(test_id, {"stage": "completed", "status": "completed"})
    t_broadcast = (time.perf_counter() - t0) * 1000

    await asyncio.wait_for(sub_task, timeout=2.0)
    assert len(received_events) == 3
    assert received_events[-1]["stage"] == "completed"
    assert t_broadcast < 50.0

