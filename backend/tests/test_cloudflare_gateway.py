"""
test_cloudflare_gateway.py - Unit tests for Cloudflare Worker Gateway integration.
Verifies that the backend forwards Bearer GATEWAY_API_KEY tokens to upstream
microservice clients (Vision, Translation, Advisory).
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.core.config import settings
from app.services.model_client import call_model_service
from app.services.translation.service import (
    translate_batch_indictrans,
    translate_batch_indictrans_sync,
)
from app.services.recommendation.service import call_remote_advisory_server


@pytest.mark.asyncio
async def test_model_client_sends_gateway_api_key():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "crop": {"label": "Tomato", "confidence": 0.95},
        "disease": {"label": "Early Blight", "confidence": 0.90},
    }

    with patch.object(settings, "MODEL_SERVER_URL", "https://smart-farming-gateway.workers.dev/vision"):
        with patch.object(settings, "GATEWAY_API_KEY", "test-secret-key-123"):
            with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp) as mock_post:
                result = await call_model_service(b"fake_image_bytes", "leaf.jpg")

                assert result["crop"]["label"] == "Tomato"
                call_args, call_kwargs = mock_post.call_args
                assert call_args[0] == "https://smart-farming-gateway.workers.dev/vision/predict"
                assert call_kwargs["headers"].get("Authorization") == "Bearer test-secret-key-123"


@pytest.mark.asyncio
async def test_translation_async_sends_gateway_api_key():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"translations": ["प्रभावित पौधों को अलग करें।"]}

    with patch.object(settings, "TRANSLATION_SERVER_URL", "https://smart-farming-gateway.workers.dev/translation"):
        with patch.object(settings, "GATEWAY_API_KEY", "test-secret-key-123"):
            with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp) as mock_post:
                result = await translate_batch_indictrans(["Isolate affected plants."], "hi")

                assert result == ["प्रभावित पौधों को अलग करें।"]
                call_args, call_kwargs = mock_post.call_args
                assert call_args[0] == "https://smart-farming-gateway.workers.dev/translation/translate"
                assert call_kwargs["headers"].get("Authorization") == "Bearer test-secret-key-123"


def test_translation_sync_sends_gateway_api_key():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"translations": ["प्रभावित पौधों को अलग करें।"]}

    with patch.object(settings, "TRANSLATION_SERVER_URL", "https://smart-farming-gateway.workers.dev/translation"):
        with patch.object(settings, "GATEWAY_API_KEY", "test-secret-key-123"):
            with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
                result = translate_batch_indictrans_sync(["Isolate affected plants."], "hi")

                assert result == ["प्रभावित पौधों को अलग करें।"]
                call_args, call_kwargs = mock_post.call_args
                assert call_args[0] == "https://smart-farming-gateway.workers.dev/translation/translate"
                assert call_kwargs["headers"].get("Authorization") == "Bearer test-secret-key-123"


def test_advisory_sends_gateway_api_key():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "immediate_action": "Apply copper fungicide immediately.",
        "treatment": "Spray Mancozeb at 2g/L.",
    }

    with patch.object(settings, "ADVISORY_SERVER_URL", "https://smart-farming-gateway.workers.dev/advisory"):
        with patch.object(settings, "GATEWAY_API_KEY", "test-secret-key-123"):
            with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
                payload = {"crop": "Tomato", "disease": "Late Blight", "confidence": 0.9}
                result = call_remote_advisory_server(payload)

                assert result is not None
                assert result["immediate_action"] == "Apply copper fungicide immediately."
                call_args, call_kwargs = mock_post.call_args
                assert call_args[0] == "https://smart-farming-gateway.workers.dev/advisory/advise"
                assert call_kwargs["headers"].get("Authorization") == "Bearer test-secret-key-123"


def test_clients_without_gateway_api_key_do_not_send_auth_header():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "immediate_action": "Apply copper fungicide immediately.",
    }

    with patch.object(settings, "ADVISORY_SERVER_URL", "http://127.0.0.1:8003"):
        with patch.object(settings, "GATEWAY_API_KEY", None):
            with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
                call_remote_advisory_server({"crop": "Tomato", "disease": "Late Blight"})
                call_args, call_kwargs = mock_post.call_args
                assert "Authorization" not in call_kwargs["headers"]

