"""
test_pipeline_integration.py — Integration test for the complete backend scouting pipeline.
"""

from pathlib import Path
import pytest

from app.context import create_context
from app.pipeline import run_pipeline

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_TEST_IMAGE = PROJECT_ROOT / "Datasets" / "testing_images" / "aphids_tomato.jpeg"


@pytest.mark.anyio
async def test_pipeline_smoke(monkeypatch):
    async def mock_vision(context, image_bytes, filename="upload.jpg", content_type="image/jpeg"):
        context["crop"] = {"label": "Tomato", "confidence": 0.95}
        context["disease"] = {"label": "Early Blight", "confidence": 0.90}
        context["severity"] = {"percent": 25.0, "bucket": "low"}
        context["status"]["preprocessing"] = "completed"
        context["status"]["crop_identification"] = "completed"
        context["status"]["disease_classification"] = "completed"
        context["status"]["severity"] = "completed"
        return context

    monkeypatch.setattr("app.pipeline.execute_remote_vision_pipeline", mock_vision)

    context = create_context(
        image_path=str(DEFAULT_TEST_IMAGE),
        user_id="test_user",
        location="Gujarat, India",
        lat=21.7645,
        lon=72.1519,
        language="English",
    )
    result = await run_pipeline(context, image_bytes=b"dummy_image_bytes")
    assert result["request_id"]
    assert "status" in result
    assert result["crop"]["label"] == "Tomato"
    assert result["disease"]["label"] == "Early Blight"
    assert result["status"]["pipeline"] == "completed"

