"""
test_ai_service_client.py - Unit tests for AI Microservice client integration.
Verifies that the backend forwards Bearer auth tokens to upstream AI microservices
(Vision, Translation, Advisory) hosted on Hugging Face Spaces.
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
async def test_model_client_sends_ai_service_auth():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "crop": {"label": "Tomato", "confidence": 0.95},
        "disease": {"label": "Early Blight", "confidence": 0.90},
    }

    with patch.object(settings, "MODEL_SERVER_URL", "https://maharsh8805-smart-farming-ai.hf.space/vision"):
        with patch.object(settings, "GATEWAY_API_KEY", "test-secret-key-123"):
            with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp) as mock_post:
                result = await call_model_service(b"fake_image_bytes", "leaf.jpg")

                assert result["crop"]["label"] == "Tomato"
                call_args, call_kwargs = mock_post.call_args
                assert call_args[0] == "https://maharsh8805-smart-farming-ai.hf.space/vision/predict"
                assert call_kwargs["headers"].get("Authorization") == "Bearer test-secret-key-123"


@pytest.mark.asyncio
async def test_translation_async_sends_ai_service_auth():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"translations": ["प्रभावित पौधों को अलग करें।"]}

    with patch.object(settings, "TRANSLATION_SERVER_URL", "https://maharsh8805-smart-farming-ai.hf.space/translation"):
        with patch.object(settings, "GATEWAY_API_KEY", "test-secret-key-123"):
            with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp) as mock_post:
                result = await translate_batch_indictrans(["Isolate affected plants."], "hi")

                assert result == ["प्रभावित पौधों को अलग करें।"]
                call_args, call_kwargs = mock_post.call_args
                assert call_args[0] == "https://maharsh8805-smart-farming-ai.hf.space/translation/translate"
                assert call_kwargs["headers"].get("Authorization") == "Bearer test-secret-key-123"


def test_translation_sync_sends_ai_service_auth():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"translations": ["प्रभावित पौधों को अलग करें।"]}

    with patch.object(settings, "TRANSLATION_SERVER_URL", "https://maharsh8805-smart-farming-ai.hf.space/translation"):
        with patch.object(settings, "GATEWAY_API_KEY", "test-secret-key-123"):
            with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
                result = translate_batch_indictrans_sync(["Isolate affected plants."], "hi")

                assert result == ["प्रभावित पौधों को अलग करें।"]
                call_args, call_kwargs = mock_post.call_args
                assert call_args[0] == "https://maharsh8805-smart-farming-ai.hf.space/translation/translate"
                assert call_kwargs["headers"].get("Authorization") == "Bearer test-secret-key-123"


def test_advisory_sends_ai_service_auth():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "immediate_action": "Apply copper fungicide immediately.",
        "treatment": "Spray Mancozeb at 2g/L.",
    }

    with patch.object(settings, "ADVISORY_SERVER_URL", "https://maharsh8805-smart-farming-ai.hf.space/advisory"):
        with patch.object(settings, "GATEWAY_API_KEY", "test-secret-key-123"):
            with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
                payload = {"crop": "Tomato", "disease": "Late Blight", "confidence": 0.9}
                result = call_remote_advisory_server(payload)

                assert result is not None
                assert result["immediate_action"] == "Apply copper fungicide immediately."
                call_args, call_kwargs = mock_post.call_args
                assert call_args[0] == "https://maharsh8805-smart-farming-ai.hf.space/advisory/advise"
                assert call_kwargs["headers"].get("Authorization") == "Bearer test-secret-key-123"


def test_clients_without_auth_key_do_not_send_auth_header():
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


@pytest.mark.asyncio
async def test_tts_client_sends_ai_service_auth(tmp_path):
    from app.api.endpoints.tts import generate_tts, TTSRequest

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "audioContent": "dGVzdC1hdWRpby1ieXRlcw==",
        "format": "mp3",
    }

    with patch.object(settings, "TTS_SERVER_URL", "https://maharsh8805-smart-farming-ai.hf.space/tts"):
        with patch.object(settings, "GATEWAY_API_KEY", "test-secret-key-123"):
            with patch("app.api.endpoints.tts.AUDIO_CACHE_DIR", tmp_path):
                with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp) as mock_post:
                    payload = TTSRequest(text="Unique phrase for auth check 12345", language="en")
                    result = await generate_tts(
                        payload=payload,
                        user_id="test-user-id",
                    )

                    assert result["format"] == "wav"
                    assert "audioContent" in result
                    assert mock_post.called
                    call_args, call_kwargs = mock_post.call_args
                    assert "https://maharsh8805-smart-farming-ai.hf.space/tts" in call_args[0]
                    assert call_kwargs["headers"].get("Authorization") == "Bearer test-secret-key-123"


def test_ai_service_url_auto_resolution():
    from app.core.config import Settings
    s = Settings(
        AI_SERVICE_URL="https://my-space.hf.space",
        MODEL_SERVER_URL="",
        TRANSLATION_SERVER_URL="",
        ADVISORY_SERVER_URL="",
        TTS_SERVER_URL="",
    )
    assert s.MODEL_SERVER_URL == "https://my-space.hf.space/vision"
    assert s.TRANSLATION_SERVER_URL == "https://my-space.hf.space/translation"
    assert s.ADVISORY_SERVER_URL == "https://my-space.hf.space/advisory"
    assert s.TTS_SERVER_URL == "https://my-space.hf.space/tts"


def test_ai_service_legacy_tunnel_sanitization():
    from app.core.config import Settings
    s = Settings(
        MODEL_SERVER_URL="https://new-awards-florence-icq.trycloudflare.com",
        TRANSLATION_SERVER_URL="https://smart-farming-gateway.user.workers.dev/translation",
        ADVISORY_SERVER_URL="https://stale-tunnel.ngrok-free.app/advisory",
        TTS_SERVER_URL="https://tunnel.ngrok.io/tts",
        AI_SERVICE_URL="https://maharsh8805-smart-farming-ai.hf.space",
    )
    assert s.MODEL_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/vision"
    assert s.TRANSLATION_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/translation"
    assert s.ADVISORY_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/advisory"
    assert s.TTS_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/tts"


def test_ai_service_url_suffix_normalization():
    from app.core.config import Settings
    s = Settings(
        MODEL_SERVER_URL="https://maharsh8805-smart-farming-ai.hf.space/vision/predict",
        TRANSLATION_SERVER_URL="https://maharsh8805-smart-farming-ai.hf.space/translation/translate",
        ADVISORY_SERVER_URL="https://maharsh8805-smart-farming-ai.hf.space/advisory/advise",
        TTS_SERVER_URL="https://maharsh8805-smart-farming-ai.hf.space/tts/synthesize",
    )
    assert s.MODEL_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/vision"
    assert s.TRANSLATION_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/translation"
    assert s.ADVISORY_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/advisory"
    assert s.TTS_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/tts"


def test_only_single_ai_service_url_configured():
    from app.core.config import Settings
    s = Settings(
        AI_SERVICE_URL="https://maharsh8805-smart-farming-ai.hf.space",
        ENVIRONMENT="production",
    )
    assert s.MODEL_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/vision"
    assert s.TRANSLATION_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/translation"
    assert s.ADVISORY_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/advisory"
    assert s.TTS_SERVER_URL == "https://maharsh8805-smart-farming-ai.hf.space/tts"
