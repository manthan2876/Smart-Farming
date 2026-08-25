from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.api.deps import get_current_user
from backend.api.routes import _public_result
from backend.database.session import get_session
from backend.main import app


class FakeSession:
    def rollback(self) -> None:
        pass

    def close(self) -> None:
        pass


app.dependency_overrides[get_session] = lambda: FakeSession()


def test_health_and_crops() -> None:
    client = TestClient(app)

    assert client.get("/health").json()["status"] == "ok"
    response = client.get("/crops")

    assert response.status_code == 200
    assert "Tomato" in response.json()["crops"]


def test_predict_serializes_pipeline_result(monkeypatch) -> None:
    result = {
        "request_id": "request-1",
        "user": {"user_id": "farmer-1", "language": "English"},
        "image": {
            "raw_path": "uploads/image.jpg",
            "processed_path": "processed/image.jpg",
            "leaf_crop": SimpleNamespace(tolist=lambda: [[1]]),
        },
        "crop": {"label": "Tomato", "confidence": 0.9},
        "disease": {"label": "Healthy", "confidence": 0.8, "model_used": "tomato"},
        "severity": {"percent": 0.0, "affected_area": 0.0, "bucket": "low"},
        "pests": [],
        "pest_classification": {},
        "weather": {"status": "failed"},
        "recommendation": {"fertilizer": "None"},
        "notes": [],
        "status": {"preprocessing": "completed"},
        "_disease_model_cfg": {"path": "secret"},
    }
    monkeypatch.setattr("backend.api.routes.run_pipeline", lambda context: result)
    monkeypatch.setattr(
        "backend.api.routes.record_prediction",
        lambda session, user_id, saved: SimpleNamespace(id=42),
    )

    response = TestClient(app).post(
        "/predict",
        headers={"X-User-ID": "farmer-1"},
        files={"file": ("leaf.jpg", b"not-a-real-image", "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["prediction_id"] == 42
    assert "leaf_crop" not in body["image"]
    assert "_disease_model_cfg" not in body


def test_predict_requires_temporary_identity() -> None:
    response = TestClient(app).post(
        "/predict",
        files={"file": ("leaf.jpg", b"image", "image/jpeg")},
    )

    assert response.status_code == 401


def test_feedback_schema_requires_prediction_id() -> None:
    response = TestClient(app).post(
        "/feedback",
        headers={"X-User-ID": "farmer-1"},
        json={"is_correct": True},
    )

    assert response.status_code == 422
