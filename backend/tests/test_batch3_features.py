from __future__ import annotations

import io
import sys
from datetime import datetime, timezone
from pathlib import Path
import pytest
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
from app.context import create_context
from app.models import User, Prediction
from app.models.farm import Farm
from app.models.plot import Plot
from app.services.prediction_job import calculate_treatment_progress
from app.services.recommendation.service import generate_recommendation, _build_prompt


def _create_test_image_bytes(color: tuple[int, int, int] = (34, 139, 34)) -> bytes:
    img = PILImage.new("RGB", (256, 256), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class FakeBatch3Prediction:
    def __init__(
        self,
        id: int = 1,
        disease: str = "Tomato Early Blight",
        severity_pct: float = 30.0,
        severity_bucket: str = "moderate",
        created_at: datetime | None = None,
    ):
        self.id = id
        self.created_at = created_at or datetime.now(timezone.utc)
        self.result = {
            "disease": {"label": disease, "confidence": 0.88},
            "severity": {"percent": severity_pct, "bucket": severity_bucket},
            "image": {"raw_path": "data/uploads/1.jpg", "processed_path": "data/processed/1.png"},
        }


# ── 1. Treatment Progress Calculation Tests ────────────────────────────────────

def test_calculate_treatment_progress_improving():
    parent = FakeBatch3Prediction(id=10, severity_pct=35.0, severity_bucket="moderate")
    res = calculate_treatment_progress(
        parent_pred=parent,
        current_disease="Tomato Early Blight",
        current_sev_pct=15.0,
        current_bucket="mild",
    )
    assert res["status"] == "improving"
    assert res["parent_prediction_id"] == 10
    assert res["parent_severity_pct"] == 35.0
    assert res["current_severity_pct"] == 15.0
    assert res["severity_delta"] == -20.0
    assert "decreased by 20.0%" in res["message"]
    assert "responding positively" in res["message"]


def test_calculate_treatment_progress_worsening():
    parent = FakeBatch3Prediction(id=11, severity_pct=10.0, severity_bucket="mild")
    res = calculate_treatment_progress(
        parent_pred=parent,
        current_disease="Tomato Early Blight",
        current_sev_pct=28.0,
        current_bucket="moderate",
    )
    assert res["status"] == "worsening"
    assert res["parent_prediction_id"] == 11
    assert res["severity_delta"] == 18.0
    assert "increased by 18.0%" in res["message"]
    assert "review treatment dosage" in res["message"]


def test_calculate_treatment_progress_stable():
    parent = FakeBatch3Prediction(id=12, severity_pct=20.0, severity_bucket="mild")
    res = calculate_treatment_progress(
        parent_pred=parent,
        current_disease="Tomato Early Blight",
        current_sev_pct=21.5,
        current_bucket="mild",
    )
    assert res["status"] == "stable"
    assert res["parent_prediction_id"] == 12
    assert res["severity_delta"] == 1.5
    assert "remains stable" in res["message"]


def test_calculate_treatment_progress_resolved():
    parent = FakeBatch3Prediction(id=13, severity_pct=25.0, severity_bucket="moderate")
    res = calculate_treatment_progress(
        parent_pred=parent,
        current_disease="Tomato Early Blight",
        current_sev_pct=0.0,
        current_bucket="none",
    )
    assert res["status"] == "resolved"
    assert res["current_severity_pct"] == 0.0
    assert "resolved" in res["message"]


def test_calculate_treatment_progress_disease_shift():
    parent = FakeBatch3Prediction(
        id=14,
        disease="Tomato Early Blight",
        severity_pct=20.0,
        severity_bucket="mild",
    )
    res = calculate_treatment_progress(
        parent_pred=parent,
        current_disease="Tomato Late Blight",
        current_sev_pct=10.0,
        current_bucket="mild",
    )
    assert "Tomato Late Blight" in res["message"]
    assert "Tomato Early Blight" in res["message"]


# ── 2. Farm-Aware Advice Tests ────────────────────────────────────────────────

def test_create_context_with_farm_and_plot():
    farm = {"id": 1, "name": "Sunrise Valley", "total_area_acres": 15.0}
    plot = {"id": 2, "name": "East Tomato Block", "crop_type": "Tomato", "area_acres": 2.5}
    ctx = create_context(
        image_path="data/uploads/leaf.jpg",
        farm=farm,
        plot=plot,
    )
    assert ctx["farm"]["name"] == "Sunrise Valley"
    assert ctx["plot"]["name"] == "East Tomato Block"
    assert ctx["plot"]["area_acres"] == 2.5


def test_prompt_building_includes_plot_calibration():
    farm = {"name": "Green Plains", "total_area_acres": 20.0}
    plot = {"name": "Plot Alpha", "crop_type": "Cotton", "area_acres": 4.0}
    context = {
        "crop": "Cotton",
        "disease": "Cotton Bacterial Blight",
        "severity": "moderate",
        "severity_pct": 22.0,
        "location": "Surat, Gujarat",
        "weather": {"temperature_celsius": 30.0, "humidity_percent": 75},
        "farm": farm,
        "plot": plot,
    }
    prompt = _build_prompt(context)
    assert "Plot Alpha" in prompt
    assert "4.0" in prompt
    assert "Green Plains" in prompt
    assert "calibrate chemical dilution, spray tank volumes" in prompt


def test_fallback_recommendation_scales_to_plot_area():
    from unittest.mock import patch
    farm = {"name": "Kisan Farm", "total_area_acres": 10.0}
    plot = {"name": "West Patch", "crop_type": "Tomato", "area_acres": 3.0}
    context = {
        "crop": "Tomato",
        "disease": "Tomato Early Blight",
        "severity": "moderate",
        "severity_pct": 25.0,
        "farm": farm,
        "plot": plot,
    }
    with patch("app.services.recommendation.service._get_hf_client", side_effect=RuntimeError("HF offline for test")):
        res_ctx = generate_recommendation(context)
    rec = res_ctx.get("recommendation", {})
    assert rec.get("is_fallback") is True
    assert rec.get("farm_aware") is True
    assert rec.get("plot_name") == "West Patch"
    assert rec.get("plot_area_acres") == 3.0
    # Fallback immediate_action calibrates spray volume to 3.0 acres
    action = rec.get("immediate_action", "")
    assert "3.0 acre(s)" in action


# ── 3. History Pagination & Header Tests ──────────────────────────────────────

class FakeHistoryQuery:
    def __init__(self, items):
        self._items = items

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def count(self):
        return len(self._items)

    def offset(self, off):
        self._items = self._items[off:]
        return self

    def limit(self, lim):
        self._items = self._items[:lim]
        return self

    def all(self):
        return self._items


class FakeHistorySession:
    def __init__(self, predictions):
        self._predictions = predictions

    def query(self, model):
        return FakeHistoryQuery(list(self._predictions))

    def rollback(self):
        pass

    def close(self):
        pass


def test_history_endpoint_pagination_headers():
    fake_user = User(
        id="usr-test-farmer",
        phone="+919999999999",
        role="farmer",
    )

    preds = []
    for i in range(1, 15):
        p = Prediction(
            id=i,
            user_id="usr-test-farmer",
            status="completed",
            result={
                "prediction_id": i,
                "crop": {"label": "Tomato"},
                "disease": {"label": "Tomato Early Blight"},
                "severity": {"percent": 10.0, "bucket": "mild"},
            },
            created_at=datetime.now(timezone.utc),
        )
        preds.append(p)

    fake_session = FakeHistorySession(preds)

    app.dependency_overrides[get_current_user] = lambda: "usr-test-farmer"
    app.dependency_overrides[get_session] = lambda: fake_session

    try:
        client = TestClient(app)
        resp = client.get("/history?limit=5&offset=5")
        assert resp.status_code == 200
        # Check custom pagination headers
        assert resp.headers.get("x-total-count") == "14"
        assert resp.headers.get("x-offset") == "5"
        assert resp.headers.get("x-limit") == "5"
        assert "x-total-count" in resp.headers.get("access-control-expose-headers", "").lower()

        # Check JSON body is still list of predictions for backward compatibility
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 5
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_session, None)
