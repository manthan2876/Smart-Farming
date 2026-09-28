from __future__ import annotations

import asyncio
import os
import sys
import time
import jwt
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app.core.config import settings
from app.core.events import prediction_hub
from app.main import app


async def test_prediction_hub():
    print("\n[1/3] Testing In-Memory PredictionStatusHub (< 1ms broadcast)...")
    test_id = 99999
    received_events = []

    async def subscriber():
        async for event in prediction_hub.subscribe(test_id):
            received_events.append(event)
            if event.get("stage") == "completed":
                break

    sub_task = asyncio.create_task(subscriber())
    await asyncio.sleep(0.05)  # Ensure subscriber is registered

    # Emit stages via publish_sync and publish
    t0 = time.perf_counter()
    prediction_hub.publish_sync(test_id, {"stage": "initialization", "status": "completed"})
    await prediction_hub.publish(test_id, {"stage": "crop_routing", "status": "completed"})
    await prediction_hub.publish(test_id, {"stage": "completed", "status": "completed"})
    t_broadcast = (time.perf_counter() - t0) * 1000

    await asyncio.wait_for(sub_task, timeout=2.0)
    print(f"   Broadcast latency for 3 stages: {t_broadcast:.2f} ms")
    assert len(received_events) == 3, f"Expected 3 events, got {len(received_events)}"
    assert received_events[-1]["stage"] == "completed"
    print("   PredictionStatusHub real-time streaming: PASS")


def test_internal_cron_security():
    print("\n[2/3] Testing Internal Cron Security & QStash Signatures...")
    client = TestClient(app)

    # 1. Unauthenticated call -> Must be rejected with 401
    resp = client.post("/internal/cron/weather-risks")
    print(f"   Unauthenticated call returned: HTTP {resp.status_code}")
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"

    # 2. Call with invalid signature -> Must be rejected with 401
    resp = client.post(
        "/internal/cron/weather-risks",
        headers={"Upstash-Signature": "invalid.fake.jwt"},
    )
    print(f"   Invalid signature call returned: HTTP {resp.status_code}")
    assert resp.status_code == 401

    # 3. Call with valid CRON_SECRET bearer token -> Must succeed
    resp = client.post(
        "/internal/cron/weather-risks",
        headers={"Authorization": f"Bearer {settings.CRON_SECRET}"},
    )
    print(f"   CRON_SECRET bearer call returned: HTTP {resp.status_code} - {resp.json().get('status')}")
    assert resp.status_code == 200

    # 4. Call with genuine QStash JWT signed with Current Signing Key
    current_key = settings.QSTASH_CURRENT_SIGNING_KEY or settings.US_EAST_1_QSTASH_CURRENT_SIGNING_KEY
    assert current_key, "QSTASH_CURRENT_SIGNING_KEY must be set"
    current_jwt = jwt.encode(
        {"iss": "Upstash", "sub": "https://api/internal/cron/weather-risks", "exp": int(time.time()) + 300},
        current_key,
        algorithm="HS256",
    )
    resp = client.post(
        "/internal/cron/weather-risks",
        headers={"Upstash-Signature": current_jwt},
    )
    print(f"   Current Key signed QStash call returned: HTTP {resp.status_code} - {resp.json().get('status')}")
    assert resp.status_code == 200

    # 5. Call with genuine QStash JWT signed with Next Signing Key (key rotation test)
    next_key = settings.QSTASH_NEXT_SIGNING_KEY or settings.US_EAST_1_QSTASH_NEXT_SIGNING_KEY
    assert next_key, "QSTASH_NEXT_SIGNING_KEY must be set"
    next_jwt = jwt.encode(
        {"iss": "Upstash", "sub": "https://api/internal/cron/weather-risks", "exp": int(time.time()) + 300},
        next_key,
        algorithm="HS256",
    )
    resp = client.post(
        "/internal/cron/weather-risks",
        headers={"Upstash-Signature": next_jwt},
    )
    print(f"   Next Key signed QStash call returned: HTTP {resp.status_code} - {resp.json().get('status')}")
    assert resp.status_code == 200

    print("   QStash signature & bearer authentication: PASS")


def test_blob_purge_endpoint():
    print("\n[3/3] Testing Orphaned Blob Purge Cron Endpoint...")
    client = TestClient(app)
    resp = client.post(
        "/internal/cron/purge-blobs",
        headers={"Authorization": f"Bearer {settings.CRON_SECRET}"},
    )
    print(f"   Purge endpoint response: HTTP {resp.status_code} - {resp.json()}")
    assert resp.status_code == 200
    assert resp.json().get("status") == "success"
    print("   Orphaned blob purge execution: PASS")


def main():
    print("=" * 60)
    print("SMART FARMING: QSTASH & EVENT HUB INTEGRATION TEST SUITE")
    print("=" * 60)
    asyncio.run(test_prediction_hub())
    test_internal_cron_security()
    test_blob_purge_endpoint()
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! IMPLEMENTATION FULLY VERIFIED.")
    print("=" * 60)


if __name__ == "__main__":
    main()
