from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.api.endpoints.predict import _public_result
from app.core import get_session
from app.models.user import User
from app.main import app


class FakeSession:
    def rollback(self) -> None:
        pass

    def close(self) -> None:
        pass

    def commit(self) -> None:
        pass

    def get(self, model, ident):
        if hasattr(model, "__name__") and model.__name__ == "User":
            return User(id=ident, role="admin" if "admin" in str(ident) else "farmer", password_hash="pw")
        return None

    def query(self, *args):
        class FakeQuery:
            def filter(self, *args, **kwargs):
                return self

            def group_by(self, *args, **kwargs):
                return self

            def scalar(self):
                return 0

            def all(self):
                return []

            def first(self):
                return None

        return FakeQuery()


app.dependency_overrides[get_session] = lambda: FakeSession()


def test_health_and_crops() -> None:
    client = TestClient(app)

    assert client.get("/health").json()["status"] == "ok"
    response = client.get("/crops")

    assert response.status_code == 200
    assert "Tomato" in response.json()["crops"]


def test_public_result_serialization() -> None:
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

    body = _public_result(result)
    assert "leaf_crop" not in body["image"]
    assert "_disease_model_cfg" not in body
    assert body["crop"]["label"] == "Tomato"


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


def test_weather_endpoint() -> None:
    client = TestClient(app)
    response = client.get(
        "/weather?lat=22.5726&lon=88.3639",
        headers={"X-User-ID": "farmer-1"},
    )
    assert response.status_code == 200
    assert "temperature_celsius" in response.json()


def test_admin_metrics_endpoint() -> None:
    client = TestClient(app)
    response = client.get(
        "/admin/metrics",
        headers={"X-User-ID": "admin-1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "processing_duration" in data
    assert "failures" in data
    assert "expert_metrics" in data



