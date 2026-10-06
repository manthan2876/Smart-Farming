from __future__ import annotations

import io
import sys
from pathlib import Path
import pytest
import numpy as np
from PIL import Image as PILImage
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "model_service") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "model_service"))

from app.main import app
from app.api.deps import get_current_user
from app.core import get_session
from app.models import User, Prediction, ExpertReview
import app.pipeline as pipeline_mod
from app.services.recommendation.service import generate_recommendation
from model_service.src.stages.decision_router import route_to_disease_model
from model_service.src.stages.severity import estimate_severity, _severity_bucket
from model_service.src.stages.pest_detector import predict_pest


# ── Fixtures & Helpers ─────────────────────────────────────────────────────────

def _create_test_image_bytes(color: tuple[int, int, int] = (34, 139, 34)) -> bytes:
    img = PILImage.new("RGB", (256, 256), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class FakeBatch2Session:
    def __init__(self):
        self._predictions = {}
        self._reviews = {}
        self._counter = 1

    def rollback(self) -> None:
        pass

    def close(self) -> None:
        pass

    def commit(self) -> None:
        pass

    def flush(self) -> None:
        pass

    def refresh(self, obj) -> None:
        pass

    def add(self, obj) -> None:
        if isinstance(obj, Prediction):
            if not obj.id:
                obj.id = self._counter
                self._counter += 1
            self._predictions[obj.id] = obj
        elif isinstance(obj, ExpertReview):
            if not obj.id:
                obj.id = self._counter
                self._counter += 1
            self._reviews[obj.id] = obj
        else:
            if hasattr(obj, "id") and not obj.id:
                obj.id = self._counter
                self._counter += 1

    def get(self, model, ident):
        if hasattr(model, "__name__") and model.__name__ == "User":
            return User(id=ident, role="admin" if "admin" in str(ident) else "farmer", password_hash="pw")
        if hasattr(model, "__name__") and model.__name__ == "Prediction":
            return self._predictions.get(ident)
        if hasattr(model, "__name__") and model.__name__ == "ExpertReview":
            return self._reviews.get(ident)
        return None

    def query(self, *args, **kwargs):
        session_self = self
        model = args[0] if args else None
        is_class = isinstance(model, type)

        class FakeQuery:
            def __init__(self, items=None):
                if items is not None:
                    self._items = items
                elif is_class and getattr(model, "__name__", "") == "Prediction":
                    self._items = list(session_self._predictions.values())
                elif is_class and getattr(model, "__name__", "") == "ExpertReview":
                    self._items = list(session_self._reviews.values())
                else:
                    self._items = []

            def filter(self, *f_args, **f_kwargs):
                return self

            def group_by(self, *g_args, **g_kwargs):
                return self

            def order_by(self, *o_args, **o_kwargs):
                return self

            def limit(self, n):
                return FakeQuery(self._items[:n])

            def offset(self, n):
                return FakeQuery(self._items[n:])

            def scalar(self):
                return len(self._items)

            def count(self):
                return len(self._items)

            def all(self):
                return list(self._items)

            def first(self):
                return self._items[0] if self._items else None

        return FakeQuery()


fake_session = FakeBatch2Session()


@pytest.fixture(autouse=True)
def batch2_overrides(monkeypatch):
    monkeypatch.setattr("app.main.initialize_database", lambda: None)
    app.dependency_overrides[get_session] = lambda: fake_session
    app.dependency_overrides[get_current_user] = lambda: "farmer-1"
    yield
    app.dependency_overrides.pop(get_session, None)
    app.dependency_overrides.pop(get_current_user, None)


# ── 1. Unsupported Crop Gate Tests ─────────────────────────────────────────────

def test_decision_router_unrecognised_crop():
    """
    When an unsupported crop like 'Wheat' is passed to route_to_disease_model,
    it must mark crop.status and status.decision_routing as unsupported_crop,
    and suppress disease model invocation.
    """
    config = {
        "thresholds": {"crop_confidence": 0.60},
        "models": {
            "disease_models": {
                "Tomato": {"path": "models/tomato.pt"},
                "Cotton": {"path": "models/cotton.pt"},
            }
        }
    }
    ctx = {
        "crop": {"label": "Wheat", "confidence": 0.95},
        "disease": {},
        "status": {"crop_identification": "completed"},
        "notes": [],
    }
    result = route_to_disease_model(ctx, config)

    assert result["status"]["decision_routing"] == "unsupported_crop"
    assert result["crop"]["status"] == "unsupported_crop"
    assert result["disease"]["label"] == "Unsupported Crop"
    assert result["disease"]["confidence"] == 0.0
    assert result["disease"]["is_uncertain"] is True
    assert result["disease"]["model_used"] == "none"
    assert any("Wheat" in note and "not supported" in note.lower() for note in result["notes"])


def test_decision_router_low_confidence_crop():
    """
    When crop confidence is below the threshold, decision router must gate
    the disease model and label as unsupported_crop.
    """
    config = {
        "thresholds": {"crop_confidence": 0.60},
        "models": {
            "disease_models": {
                "Tomato": {"path": "models/tomato.pt"},
            }
        }
    }
    ctx = {
        "crop": {"label": "Tomato", "confidence": 0.42},
        "disease": {},
        "status": {"crop_identification": "completed"},
        "notes": [],
    }
    result = route_to_disease_model(ctx, config)

    assert result["status"]["decision_routing"] == "unsupported_crop"
    assert result["crop"]["status"] == "unsupported_crop"
    assert result["disease"]["label"] == "Unsupported Crop / Indeterminate"
    assert result["disease"]["confidence"] == 0.0
    assert result["disease"]["is_uncertain"] is True


def test_decision_router_supported_crop():
    """
    When a valid supported crop with high confidence is passed,
    it must route to the corresponding crop disease model.
    """
    config = {
        "thresholds": {"crop_confidence": 0.60},
        "models": {
            "disease_models": {
                "Tomato": {"path": "models/tomato.pt"},
                "Cotton": {"path": "models/cotton.pt"},
            }
        }
    }
    ctx = {
        "crop": {"label": "Tomato", "confidence": 0.92},
        "disease": {},
        "status": {"crop_identification": "completed"},
        "notes": [],
    }
    result = route_to_disease_model(ctx, config)

    assert result["status"]["decision_routing"] == "completed"
    assert result["disease"]["model_used"] == "models/tomato.pt"
    assert result["crop"].get("status") != "unsupported_crop"


# ── 2. Severity Reliability & Healthy Leaf Tests ──────────────────────────────

def test_severity_bucket_thresholds():
    """
    Verify unified severity buckets across the system:
    Healthy (0%), Mild (< 20%), Moderate (20% - 50%), Severe (> 50%).
    """
    assert _severity_bucket(0.0) == "Healthy"
    assert _severity_bucket(-1.0) == "Healthy"
    assert _severity_bucket(5.0) == "Mild"
    assert _severity_bucket(19.9) == "Mild"
    assert _severity_bucket(20.0) == "Moderate"
    assert _severity_bucket(35.0) == "Moderate"
    assert _severity_bucket(50.0) == "Moderate"
    assert _severity_bucket(50.1) == "Severe"
    assert _severity_bucket(85.0) == "Severe"


def test_severity_skips_unsupported_crop():
    """
    When decision routing determined an unsupported crop,
    severity estimation must skip execution cleanly and mark bucket 'N/A' with 0.0%.
    """
    ctx = {
        "status": {"preprocessing": "completed", "decision_routing": "unsupported_crop"},
        "crop": {"status": "unsupported_crop", "label": "Rice"},
        "severity": {},
        "notes": [],
    }
    result = estimate_severity(ctx)

    assert result["status"]["severity"] == "skipped_unsupported_crop"
    assert result["severity"]["percent"] == 0.0
    assert result["severity"]["bucket"] == "N/A"
    assert result["severity"]["affected_area"] == 0.0


def test_severity_healthy_leaf_noise_suppression():
    """
    When disease label is 'Healthy' and CV segmentation detects low false positive
    noise (< 15%), foliar damage must be suppressed to 0.0% and bucket 'Healthy'.
    """
    # Create a solid green leaf image
    leaf_img = np.zeros((100, 100, 3), dtype=np.uint8)
    leaf_img[:, :] = (35, 140, 40)  # BGR green

    ctx = {
        "disease": {"label": "Healthy", "confidence": 0.98},
        "image": {"leaf_crop": leaf_img},
        "severity": {},
        "status": {"preprocessing": "completed"},
        "notes": [],
    }
    result = estimate_severity(ctx)

    assert result["severity"]["percent"] == 0.0
    assert result["severity"]["bucket"] == "Healthy"
    assert result["severity"]["affected_area"] == 0.0


# ── 3. Pest Status & Fallback Bug Elimination ──────────────────────────────────

def test_pest_detector_unavailable_when_weights_missing():
    """
    When the pest detection model cannot be loaded, pest_classification
    must report available=False and status='unavailable'.
    """
    config = {"models": {"pest_classifier": {"path": "non_existent_weights.pt"}}}
    ctx = {
        "status": {"preprocessing": "completed"},
        "image": {"leaf_crop": np.zeros((100, 100, 3), dtype=np.uint8)},
        "notes": [],
    }
    result = predict_pest(ctx, config)

    assert result["status"]["pest_detection"] == "unavailable"
    assert result["pest_classification"]["available"] is False
    assert result["pest_classification"]["status"] == "unavailable"
    assert result["pests"] == []


def test_pest_detector_no_pests_detected_clean_leaf(monkeypatch):
    """
    Ensure the line 67 bug (fallback to raw predictions when no pests meet threshold)
    is eliminated: clean leaves must return empty pests list and 'no_pests_detected'.
    """
    class MockResult:
        def __init__(self):
            import torch
            self.probs = type("Probs", (), {"data": torch.tensor([0.15, 0.22])})()
            self.names = {0: "Aphids", 1: "Whitefly"}

    class MockYOLO:
        def predict(self, **kwargs):
            return [MockResult()]

    import model_service.src.stages.pest_detector as pest_detector_mod
    monkeypatch.setattr(pest_detector_mod, "load_yolo", lambda path: MockYOLO())

    config = {"models": {"pest_classifier": {"path": "mock_pests.pt"}}}
    ctx = {
        "status": {"preprocessing": "completed"},
        "image": {"leaf_crop": np.zeros((100, 100, 3), dtype=np.uint8)},
        "notes": [],
    }
    result = predict_pest(ctx, config)

    assert result["status"]["pest_detection"] == "completed"
    assert result["pest_classification"]["available"] is True
    assert result["pest_classification"]["status"] == "no_pests_detected"
    assert result["pests"] == []  # MUST NOT fall back to low-confidence predictions!


def test_pest_detector_pest_detected_when_above_threshold(monkeypatch):
    """
    When pest confidence exceeds 0.40 threshold, pest_detected is returned
    with the filtered list.
    """
    class MockResult:
        def __init__(self):
            import torch
            self.probs = type("Probs", (), {"data": torch.tensor([0.78, 0.12])})()
            self.names = {0: "Aphids", 1: "Whitefly"}

    class MockYOLO:
        def predict(self, **kwargs):
            return [MockResult()]

    import model_service.src.stages.pest_detector as pest_detector_mod
    monkeypatch.setattr(pest_detector_mod, "load_yolo", lambda path: MockYOLO())

    config = {"models": {"pest_classifier": {"path": "mock_pests.pt"}}}
    ctx = {
        "status": {"preprocessing": "completed"},
        "image": {"leaf_crop": np.zeros((100, 100, 3), dtype=np.uint8)},
        "notes": [],
    }
    result = predict_pest(ctx, config)

    assert result["status"]["pest_detection"] == "completed"
    assert result["pest_classification"]["status"] == "pest_detected"
    assert len(result["pests"]) == 1
    assert result["pests"][0]["label"] == "Aphids"
    assert result["pests"][0]["confidence"] == pytest.approx(0.78, 0.01)


# ── 4. Masked Advisory for Unsupported Crops ──────────────────────────────────

def test_recommendation_masks_unsupported_crop():
    """
    When an unsupported crop is submitted, recommendation service must generate
    a safe non-chemical advisory and set is_masked=True.
    """
    ctx = {
        "crop": {"label": "Sugarcane", "confidence": 0.90, "status": "unsupported_crop"},
        "disease": {"label": "Unsupported Crop", "confidence": 0.0, "is_uncertain": True},
        "severity": {"percent": 0.0, "bucket": "Healthy"},
        "pests": [],
        "pest_classification": {"available": True, "status": "no_pests_detected"},
        "weather": {},
        "status": {"decision_routing": "unsupported_crop", "preprocessing": "completed"},
        "language": "en",
        "notes": [],
    }

    result_ctx = generate_recommendation(ctx)
    rec = result_ctx["recommendation"]

    assert rec.get("is_masked") is True
    assert "no automated chemical treatment is recommended" in rec.get("treatment", "").lower()
    assert rec.get("pesticide") == "None (Consult specialist)"
    assert (
        "specialist" in rec.get("immediate_action", "").lower()
        or "kvk" in rec.get("immediate_action", "").lower()
        or "extension" in rec.get("immediate_action", "").lower()
    )


# ── 5. End-to-End Predict Flow for Unsupported Crop ────────────────────────────

def test_predict_endpoint_unsupported_crop_escalates_to_expert(monkeypatch):
    """
    Verify full /predict endpoint behavior on unsupported crop:
    - Disease is marked Unsupported Crop
    - mask_advisory is True
    - Expert review is queued as pending
    - Status is pending_expert_review
    """
    async def mock_run_pipeline(context, image_bytes, filename="upload.jpg", content_type="image/jpeg"):
        context["crop"] = {"label": "Wheat", "confidence": 0.88, "status": "unsupported_crop"}
        context["disease"] = {
            "label": "Unsupported Crop",
            "confidence": 0.0,
            "is_uncertain": True,
            "model_used": "none",
        }
        context["severity"] = {"percent": 0.0, "bucket": "N/A"}
        context["pests"] = []
        context["pest_classification"] = {"available": True, "status": "no_pests_detected"}
        context["status"]["preprocessing"] = "completed"
        context["status"]["crop_identification"] = "completed"
        context["status"]["decision_routing"] = "unsupported_crop"
        context["status"]["disease_classification"] = "completed"
        context["status"]["severity"] = "skipped_unsupported_crop"
        context["status"]["pest_detection"] = "completed"
        context["status"]["pipeline"] = "completed"
        context["recommendation"] = {
            "immediate_action": "Consult local agronomist or KVK.",
            "treatment": "No chemical treatments are recommended for unsupported crops.",
            "is_masked": True,
        }
        return context

    monkeypatch.setattr(pipeline_mod, "run_pipeline", mock_run_pipeline)

    valid_img = _create_test_image_bytes()
    client = TestClient(app)
    resp = client.post(
        "/predict",
        headers={"X-User-ID": "farmer-1"},
        files={"file": ("wheat_leaf.jpg", valid_img, "image/jpeg")},
        data={"location": "Punjab", "lat": "30.9010", "lon": "75.8573"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["crop"]["label"] == "Wheat"
    assert data["crop"]["status"] == "unsupported_crop"
    assert data["disease"]["label"] == "Unsupported Crop"
    assert data["status"]["expert_review"] == "pending"
    assert data["status"]["mask_advisory"] is True
    assert data["recommendation"]["is_masked"] is True
