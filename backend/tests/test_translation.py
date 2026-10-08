import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.core.config import settings
from app.services.translation.service import (
    normalize_language_code,
    split_into_sentences,
    join_sentences,
    translate_batch_indictrans,
    translate_batch_indictrans_sync,
    translate_batch,
    translate_batch_sync,
    translate_recommendation,
)


def test_split_into_sentences():
    # English sentences with period, question mark, exclamation
    text = "Your crop shows signs of leaf blight. Please apply fungicide! Are symptoms spreading?"
    sents = split_into_sentences(text)
    assert len(sents) == 3
    assert sents[0] == "Your crop shows signs of leaf blight."
    assert sents[1] == "Please apply fungicide!"
    assert sents[2] == "Are symptoms spreading?"

    # Indic sentences with danda (।)
    indic_text = "પાકમાં રોગ દેખાય છે। તરત જ દવા છાંટો।"
    indic_sents = split_into_sentences(indic_text)
    assert len(indic_sents) == 2
    assert indic_sents[0] == "પાકમાં રોગ દેખાય છે।"
    assert indic_sents[1] == "તરત જ દવા છાંટો।"

    # Empty string or single sentence
    assert split_into_sentences("") == []
    assert split_into_sentences("Single sentence.") == ["Single sentence."]


def test_join_sentences():
    sents = ["First sentence.", "Second sentence."]
    assert join_sentences(sents) == "First sentence. Second sentence."
    assert join_sentences([]) == ""


def test_normalize_language_code():
    assert normalize_language_code("Hindi") == "hi"
    assert normalize_language_code("hi") == "hi"
    assert normalize_language_code("hi-IN") == "hi"
    assert normalize_language_code("Gujarati") == "gu"
    assert normalize_language_code("gu") == "gu"
    assert normalize_language_code("English") == "en"
    assert normalize_language_code(None) == "en"


@pytest.mark.asyncio
async def test_translate_batch_indictrans_success():
    texts = [
        "Your crop shows signs of leaf blight. Apply copper fungicide.",
        "Maintain proper plant spacing.",
    ]
    
    # Mock response from IndicTrans2 FastAPI server
    mock_translations = [
        "आपकी फसल में पत्ती झुलसा के लक्षण दिख रहे हैं।",
        "कॉपर फफूंदनाशी का प्रयोग करें।",
        "पौधों के बीच उचित दूरी बनाए रखें।",
    ]

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"translations": mock_translations}

    with patch.object(settings, "TRANSLATION_SERVER_URL", "http://fake-colab-tunnel.ngrok-free.app"):
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp) as mock_post:
            result = await translate_batch_indictrans(texts, "hi")

            assert len(result) == 2
            # First text has 2 sentences reassembled
            assert result[0] == "आपकी फसल में पत्ती झुलसा के लक्षण दिख रहे हैं। कॉपर फफूंदनाशी का प्रयोग करें।"
            assert result[1] == "पौधों के बीच उचित दूरी बनाए रखें।"

            # Verify request headers and payload
            call_kwargs = mock_post.call_args
            assert call_kwargs.kwargs["headers"]["ngrok-skip-browser-warning"] == "69420"
            assert call_kwargs.kwargs["json"]["target"] == "hi"
            assert len(call_kwargs.kwargs["json"]["texts"]) == 3


def test_translate_batch_indictrans_sync_success():
    texts = ["Isolate infected plants. Spray immediately."]
    mock_translations = ["संक्रमित पौधों को अलग करें।", "तुरंत छिड़काव करें।"]

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"translations": mock_translations}

    with patch.object(settings, "TRANSLATION_SERVER_URL", "http://fake-colab-tunnel.ngrok-free.app"):
        with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
            result = translate_batch_indictrans_sync(texts, "hi")
            assert len(result) == 1
            assert result[0] == "संक्रमित पौधों को अलग करें। तुरंत छिड़काव करें।"
            assert mock_post.called


@pytest.mark.asyncio
async def test_translate_batch_indictrans_unconfigured():
    with patch.object(settings, "TRANSLATION_SERVER_URL", ""):
        with pytest.raises(RuntimeError, match="TRANSLATION_SERVER_URL is not configured"):
            await translate_batch_indictrans(["Hello"], "hi")


@pytest.mark.asyncio
async def test_translate_batch_cascade_fallback_to_hf():
    texts = ["Test recommendation text."]

    with patch.object(settings, "TRANSLATION_SERVER_URL", "http://fake-colab-tunnel.ngrok-free.app"):
        # Make IndicTrans2 raise an error (e.g. Colab disconnected / timeout)
        with patch(
            "app.services.translation.service.translate_batch_indictrans",
            side_effect=httpx.ConnectTimeout("Connection timed out"),
        ):
            # Make HF fallback succeed
            with patch(
                "app.services.translation.service.translate_batch_hf_fallback",
                new_callable=AsyncMock,
                return_value=["अनुवादित पाठ।"],
            ) as mock_hf:
                with patch("app.core.redis_rest.redis_rest.mget", new_callable=AsyncMock, return_value=[None]):
                    with patch("app.core.redis_rest.redis_rest.set", new_callable=AsyncMock, return_value=True):
                        result = await translate_batch(texts, "hi")
                        assert result == ["अनुवादित पाठ।"]
                        assert mock_hf.called


@pytest.mark.asyncio
async def test_translate_recommendation():
    rec = {
        "immediate_action": "Isolate affected plants.",
        "treatment": "Apply fungicide.",
        "prevention": "Rotate crops.",
        "monitoring": "Check weekly.",
        "provider": "qwen",
    }

    mock_translated = [
        "प्रभावित पौधों को अलग करें।",
        "कवकनाशी लगाएं।",
        "फसल चक्र अपनाएं।",
        "साप्ताहिक जांच करें।",
    ]

    with patch(
        "app.services.translation.service.translate_batch",
        new_callable=AsyncMock,
        return_value=mock_translated,
    ):
        result = await translate_recommendation(rec, "hi")
        assert result["immediate_action"] == "प्रभावित पौधों को अलग करें।"
        assert result["treatment"] == "कवकनाशी लगाएं।"
        assert result["language"] == "hi"
        assert result["provider"] == "qwen"  # Non-text preserved


def test_translate_batch_sync_fallback():
    texts = ["Sample text."]
    with patch.object(settings, "TRANSLATION_SERVER_URL", "http://fake-colab.ngrok-free.app"):
        with patch(
            "app.services.translation.service.translate_batch_indictrans_sync",
            side_effect=RuntimeError("Colab offline"),
        ):
            # When IndicTrans2 fails, translate_batch_sync falls back to original text without throwing
            result = translate_batch_sync(texts, "gu")
            assert result == ["Sample text."]


def test_translate_prediction_endpoint_success():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api.deps import get_current_user
    from app.core import get_session
    from app.models.prediction import Prediction
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from app.core import Base

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    session = TestingSession()
    pred = Prediction(
        id=101,
        user_id="user-123",
        status="completed",
        raw_path="data/uploads/leaf.jpg",
        result={
            "recommendation": {
                "immediate_action": "Isolate affected plants.",
                "treatment": "Apply copper spray.",
            }
        },
    )
    session.add(pred)
    session.commit()

    def override_get_session():
        yield session

    def override_get_current_user():
        return "user-123"

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    mock_translated_rec = {
        "immediate_action": "प्रभावित पौधों को अलग करें।",
        "treatment": "कॉपर स्प्रे लगाएं।",
        "language": "hi",
    }

    try:
        with patch(
            "app.api.endpoints.translation.translate_recommendation",
            new_callable=AsyncMock,
            return_value=mock_translated_rec,
        ):
            with TestClient(app) as client:
                resp = client.post("/predictions/101/translate?target_language=Hindi")
                assert resp.status_code == 200
                data = resp.json()
                assert isinstance(data, dict)
                assert data["prediction_id"] == 101
                assert data["language"] == "hi"
                assert data["cached"] is False
                assert data["recommendation"]["immediate_action"] == "प्रभावित पौधों को अलग करें।"
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(get_current_user, None)
        session.close()
        Base.metadata.drop_all(bind=test_engine)



