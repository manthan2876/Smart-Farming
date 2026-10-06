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


class FakeSession:
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

    def scalar(self, stmt=None):
        if self._predictions:
            return self._predictions.get(55) or list(self._predictions.values())[-1]
        return None

    def scalars(self, stmt=None):
        class FakeScalars:
            def __init__(self, items):
                self._items = items
            def all(self):
                return self._items
            def first(self):
                return self._items[0] if self._items else None
            def __iter__(self):
                return iter(self._items)
        return FakeScalars(list(self._reviews.values()))

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

            def filter(self, *args, **kwargs):
                return self

            def group_by(self, *args, **kwargs):
                return self

            def order_by(self, *args, **kwargs):
                return self

            def limit(self, *args, **kwargs):
                return self

            def offset(self, *args, **kwargs):
                return self

            def scalar(self):
                return len(self._items)

            def all(self):
                return self._items

            def first(self):
                return self._items[0] if self._items else None

        return FakeQuery()


fake_db = FakeSession()


@pytest.fixture(autouse=True)
def override_test_db():
    orig = app.dependency_overrides.get(get_session)
    app.dependency_overrides[get_session] = lambda: fake_db
    yield
    if orig is not None:
        app.dependency_overrides[get_session] = orig
    else:
        app.dependency_overrides.pop(get_session, None)



def _create_test_image_bytes(format="JPEG", color=(0, 200, 0), size=(100, 100)) -> bytes:
    img = PILImage.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


# ── 1. Input Validation Rejection Tests ───────────────────────────────────────

def test_rejection_unsupported_media_type():
    """Verify rejection of non-image MIME types and bad extensions with HTTP 415."""
    client = TestClient(app)
    resp = client.post(
        "/predict",
        headers={"X-User-ID": "farmer-1"},
        files={"file": ("notes.txt", b"Hello world, this is a plain text file.", "text/plain")},
    )
    assert resp.status_code == 415
    assert "Upload a JPEG, PNG, or WebP image" in resp.json()["detail"]


def test_rejection_corrupted_image_bytes():
    """Verify rejection of corrupted / random binary bytes with HTTP 400."""
    client = TestClient(app)
    corrupted_bytes = b"GIF89a corrupted invalid random stream of binary data \x00\xff\xee\xdd"
    resp = client.post(
        "/predict",
        headers={"X-User-ID": "farmer-1"},
        files={"file": ("leaf.jpg", corrupted_bytes, "image/jpeg")},
    )
    assert resp.status_code == 400
    assert "not a valid or readable image" in resp.json()["detail"]


def test_rejection_oversized_file(monkeypatch):
    """Verify rejection of files exceeding the 10 MB limit with HTTP 413."""
    client = TestClient(app)
    import app.api.endpoints.predict as predict_mod
    monkeypatch.setattr(predict_mod, "_MAX_UPLOAD_BYTES", 1024)

    large_image = _create_test_image_bytes(size=(200, 200))
    assert len(large_image) > 1024

    resp = client.post(
        "/predict",
        headers={"X-User-ID": "farmer-1"},
        files={"file": ("huge_leaf.jpg", large_image, "image/jpeg")},
    )
    assert resp.status_code == 413
    assert "exceeds the 10 MB upload limit" in resp.json()["detail"]


# ── 2. Computer Vision Preprocessing Quality Rejection Tests ──────────────────

def test_preprocessing_quality_rejection_blur():
    """
    Verify that an overly blurred image fails preprocessing with failed_blur
    and includes an explicit, helpful farmer-facing note.
    """
    from model_service.src.stages.preprocessing import OpenCVPreprocessorService

    # Uniform solid color has 0 Laplacian variance
    blurred_im = np.full((100, 100, 3), 128, dtype=np.uint8)

    preprocessor = OpenCVPreprocessorService({"thresholds": {"blur_var_threshold": 50.0}})
    ctx = {
        "image_bgr": blurred_im,
        "image": {},
        "status": {},
        "notes": [],
    }

    result = preprocessor.process(ctx)
    assert result["status"]["preprocessing"] in ["failed_blur", "failed_no_leaf"]
    assert result["image"]["leaf_detected"] is False
    assert len(result["notes"]) > 0
    # Must never output a confident disease diagnosis for a failed image
    assert result.get("disease", {}).get("label") is None


def test_preprocessing_quality_rejection_bad_lighting():
    """
    Verify that extreme darkness or overexposure fails preprocessing with failed_lighting.
    """
    from model_service.src.stages.preprocessing import OpenCVPreprocessorService

    dark_im = np.full((100, 100, 3), 10, dtype=np.uint8)

    preprocessor = OpenCVPreprocessorService({
        "thresholds": {"min_brightness": 40.0, "max_brightness": 240.0}
    })
    ctx = {
        "image_bgr": dark_im,
        "image": {},
        "status": {},
        "notes": [],
    }

    result = preprocessor.process(ctx)
    assert result["status"]["preprocessing"] == "failed_lighting"
    assert result["image"]["leaf_detected"] is False
    assert any("lighting" in n.lower() for n in result["notes"])


def test_preprocessing_quality_rejection_non_crop():
    """
    Verify that an image with no recognizable vegetation fails leaf isolation.
    """
    from model_service.src.stages.preprocessing import OpenCVPreprocessorService

    blue_im = np.zeros((100, 100, 3), dtype=np.uint8)
    blue_im[:, :, 0] = 220  # Blue channel only

    preprocessor = OpenCVPreprocessorService({"thresholds": {"min_brightness": 20.0}})
    ctx = {
        "image_bgr": blue_im,
        "image": {},
        "status": {},
        "notes": [],
    }

    result = preprocessor.process(ctx)
    assert result["status"]["preprocessing"] == "failed_no_leaf"
    assert result["image"]["leaf_detected"] is False
    assert any("no plant leaf detected" in n.lower() for n in result["notes"])


# ── 3. Near-Tie Diagnosis ("Could also be") & Escalation Tests ─────────────────

def test_near_tie_disease_detection():
    """
    Verify that a near-tie condition (runner-up confidence within margin of top 1)
    sets is_near_tie, could_also_be, and confidence_rating='near_tie'.
    """
    from model_service.src.stages.disease_classifier import evaluate_disease_prediction

    classes = ["Early Blight", "Late Blight", "Healthy"]
    probs = np.array([0.48, 0.42, 0.10], dtype=np.float32)

    res = evaluate_disease_prediction(classes, probs, threshold=0.70, near_tie_margin=0.15)

    assert res["is_near_tie"] is True
    assert res["confidence_rating"] == "near_tie"
    assert res["could_also_be"] is not None
    assert res["could_also_be"]["label"] == "Late Blight"
    assert pytest.approx(res["could_also_be"]["confidence"], 0.01) == 0.42
    assert any("Could also be" in note for note in res["notes"])


def test_near_tie_escalation_in_predict_flow(monkeypatch):
    """
    Verify that when the pipeline returns a near-tie diagnosis, the prediction
    status is escalated to pending_expert_review with explicit reason.
    """
    async def mock_run_pipeline(context, image_bytes, filename="upload.jpg", content_type="image/jpeg"):
        context["crop"] = {"label": "Tomato", "confidence": 0.95}
        context["disease"] = {
            "label": "Early Blight",
            "confidence": 0.52,
            "is_near_tie": True,
            "confidence_rating": "near_tie",
            "could_also_be": {"label": "Late Blight", "confidence": 0.46, "margin": 0.06},
        }
        context["severity"] = {"percent": 30.0, "bucket": "moderate"}
        context["status"]["preprocessing"] = "completed"
        context["status"]["crop_identification"] = "completed"
        context["status"]["disease_classification"] = "completed"
        context["status"]["severity"] = "completed"
        context["status"]["pipeline"] = "completed"
        return context

    monkeypatch.setattr(pipeline_mod, "run_pipeline", mock_run_pipeline)

    valid_img = _create_test_image_bytes()
    client = TestClient(app)
    resp = client.post(
        "/predict",
        headers={"X-User-ID": "farmer-1"},
        files={"file": ("tomato_leaf.jpg", valid_img, "image/jpeg")},
        data={"location": "Gujarat", "lat": "21.7645", "lon": "72.1519"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["disease"]["is_near_tie"] is True
    assert data["disease"]["could_also_be"]["label"] == "Late Blight"
    assert data["status"]["expert_review"] == "pending"


# ── 4. Expert Review Correction Merge Test ────────────────────────────────────

def test_expert_review_correction_merges_to_prediction():
    """
    Verify that when an agronomist reviews a scan and provides a corrected diagnosis,
    the original prediction is updated with verified status and corrected disease.
    """
    # Create an initial unverified prediction
    pred = Prediction(
        id=55,
        user_id="farmer-1",
        raw_path="data/uploads/leaf_55.jpg",
        crop="Cotton",
        crop_conf=0.95,
        disease="Leaf Curl",
        disease_conf=0.55,
        severity_pct=40.0,
        status="pending_expert_review",
        result={
            "crop": {"label": "Cotton", "confidence": 0.95},
            "disease": {"label": "Leaf Curl", "confidence": 0.55},
            "severity": {"percent": 40.0, "bucket": "moderate"},
            "status": {"pipeline": "completed", "expert_review": "pending"},
        },
    )
    fake_db._predictions[55] = pred

    # Create associated pending ExpertReview
    review = ExpertReview(
        id=10,
        prediction_id=55,
        status="pending",
    )
    review.prediction = pred
    fake_db._reviews[10] = review

    # Submit expert review
    client = TestClient(app)
    review_payload = {
        "decision": "corrected",
        "notes": "Microscopic spot examination confirms Bacterial Blight instead.",
        "corrected_disease": "Bacterial Blight",
        "corrected_severity": "45%",
        "farmer_guidance": "Apply copper oxychloride at 2.5g per litre of water.",
    }

    resp = client.post(
        "/expert/reviews/10",
        headers={"X-User-ID": "admin-1"},
        json=review_payload,
    )
    assert resp.status_code == 200

    # Fetch updated prediction from /predictions/55
    detail_resp = client.get(
        "/predictions/55",
        headers={"X-User-ID": "farmer-1"},
    )
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()

    # Verify that original scan and detail reflect the expert's corrected disease and verified badge
    assert detail_data["disease"]["label"] == "Bacterial Blight"
    assert detail_data["status"]["expert_review"] == "verified"
    assert detail_data["expert_review_data"] is not None
    assert detail_data["expert_review_data"]["decision"] == "corrected"
    assert detail_data["expert_review_data"]["corrected_disease"] == "Bacterial Blight"
    assert "copper oxychloride" in detail_data["expert_review_data"]["farmer_guidance"]
