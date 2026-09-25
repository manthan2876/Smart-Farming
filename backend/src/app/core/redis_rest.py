from __future__ import annotations

import json
import logging
import os
from typing import Any
import httpx

from app.core.config import settings

logger = logging.getLogger("smart-farming.redis_rest")


class UpstashRedisREST:
    """Lightweight, connectionless Upstash Redis client using HTTP REST API.

    100% serverless compatible: zero persistent TCP sockets, scales to zero with Cloud Run.
    Supports both async and synchronous execution with built-in JSON serialization.
    """

    def __init__(self):
        self.url = (getattr(settings, "UPSTASH_REDIS_REST_URL", None) or os.getenv("UPSTASH_REDIS_REST_URL") or "").rstrip("/")
        self.token = getattr(settings, "UPSTASH_REDIS_REST_TOKEN", None) or os.getenv("UPSTASH_REDIS_REST_TOKEN") or ""
        self.enabled = bool(self.url and self.token)
        if not self.enabled:
            logger.info("Upstash Redis REST is not configured (UPSTASH_REDIS_REST_URL / TOKEN not set).")

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
        }

    # -------------------------------------------------------------------------
    # Async Methods (for FastAPI async request handlers)
    # -------------------------------------------------------------------------

    async def get(self, key: str) -> Any | None:
        """Retrieve a value by key. Deserializes JSON if possible."""
        if not self.enabled:
            return None
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                resp = await client.get(f"{self.url}/get/{key}", headers=self.headers)
                if resp.status_code == 200:
                    raw = resp.json().get("result")
                    if raw is None:
                        return None
                    if isinstance(raw, str):
                        try:
                            return json.loads(raw)
                        except (ValueError, TypeError):
                            return raw
                    return raw
        except Exception as exc:
            logger.warning("Upstash Redis REST GET failed for '%s': %s", key, exc)
        return None

    async def set(self, key: str, value: Any, ex: int | None = None) -> bool:
        """Store a key-value pair with optional TTL in seconds."""
        if not self.enabled:
            return False
        try:
            val_str = json.dumps(value) if not isinstance(value, str) else value
            endpoint = f"{self.url}/set/{key}"
            if ex and ex > 0:
                endpoint += f"?ex={int(ex)}"

            async with httpx.AsyncClient(timeout=2.5) as client:
                resp = await client.post(endpoint, content=val_str, headers=self.headers)
                return resp.status_code == 200 and resp.json().get("result") == "OK"
        except Exception as exc:
            logger.warning("Upstash Redis REST SET failed for '%s': %s", key, exc)
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key."""
        if not self.enabled:
            return False
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                resp = await client.get(f"{self.url}/del/{key}", headers=self.headers)
                return resp.status_code == 200
        except Exception as exc:
            logger.warning("Upstash Redis REST DEL failed for '%s': %s", key, exc)
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        if not self.enabled:
            return False
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                resp = await client.get(f"{self.url}/exists/{key}", headers=self.headers)
                return resp.status_code == 200 and int(resp.json().get("result", 0)) > 0
        except Exception as exc:
            logger.warning("Upstash Redis REST EXISTS failed for '%s': %s", key, exc)
            return False

    async def incr(self, key: str) -> int | None:
        """Atomically increment a key (useful for rate limiting)."""
        if not self.enabled:
            return None
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                resp = await client.get(f"{self.url}/incr/{key}", headers=self.headers)
                if resp.status_code == 200:
                    return int(resp.json().get("result", 0))
        except Exception as exc:
            logger.warning("Upstash Redis REST INCR failed for '%s': %s", key, exc)
        return None

    # -------------------------------------------------------------------------
    # Synchronous Methods (for background threads, Celery/ARQ legacy, or scripts)
    # -------------------------------------------------------------------------

    def get_sync(self, key: str) -> Any | None:
        """Synchronous version of get()."""
        if not self.enabled:
            return None
        try:
            with httpx.Client(timeout=2.5) as client:
                resp = client.get(f"{self.url}/get/{key}", headers=self.headers)
                if resp.status_code == 200:
                    raw = resp.json().get("result")
                    if raw is None:
                        return None
                    if isinstance(raw, str):
                        try:
                            return json.loads(raw)
                        except (ValueError, TypeError):
                            return raw
                    return raw
        except Exception as exc:
            logger.warning("Upstash Redis REST GET_SYNC failed for '%s': %s", key, exc)
        return None

    def set_sync(self, key: str, value: Any, ex: int | None = None) -> bool:
        """Synchronous version of set()."""
        if not self.enabled:
            return False
        try:
            val_str = json.dumps(value) if not isinstance(value, str) else value
            endpoint = f"{self.url}/set/{key}"
            if ex and ex > 0:
                endpoint += f"?ex={int(ex)}"

            with httpx.Client(timeout=2.5) as client:
                resp = client.post(endpoint, content=val_str, headers=self.headers)
                return resp.status_code == 200 and resp.json().get("result") == "OK"
        except Exception as exc:
            logger.warning("Upstash Redis REST SET_SYNC failed for '%s': %s", key, exc)
            return False

    def delete_sync(self, key: str) -> bool:
        """Synchronous version of delete()."""
        if not self.enabled:
            return False
        try:
            with httpx.Client(timeout=2.5) as client:
                resp = client.get(f"{self.url}/del/{key}", headers=self.headers)
                return resp.status_code == 200
        except Exception as exc:
            logger.warning("Upstash Redis REST DEL_SYNC failed for '%s': %s", key, exc)
            return False


# Global singleton client instance
redis_rest = UpstashRedisREST()
