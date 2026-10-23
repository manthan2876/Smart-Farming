from __future__ import annotations

import io
import zipfile
import json
import pytest
from datetime import datetime, timezone
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image as PILImage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core import Base, get_session
from app.api.deps import hash_password, create_token
from app.models.user import User
from app.models.prediction import Prediction
from app.models.dataset import DatasetCandidate
from app.api.endpoints.mlops import _split_for_entity, DatasetExportSplit, CandidateStatusEnum

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setattr("app.main.initialize_database", lambda: None)
    monkeypatch.setattr("app.api.endpoints.tts.sync_existing_audio_to_storage", lambda: {})
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_session():
        yield db_session

    original_override = app.dependency_overrides.get(get_session)
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    if original_override is not None:
        app.dependency_overrides[get_session] = original_override
    else:
        app.dependency_overrides.pop(get_session, None)


@pytest.fixture
def admin_user(db_session):
    admin = User(
        id="admin-mlops-1",
        name="MLOps Admin",
        email="admin@agri.org",
        phone="+919876543299",
        password_hash=hash_password("AdminPass123!"),
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    token = create_token(admin.id, "access", timedelta(hours=1))
    return {"user": admin, "token": token}


from datetime import timedelta

def test_spatial_split_determinism():
    """Verify that images from the same plot_id are strictly assigned to the same split."""
    split_cfg = DatasetExportSplit(train=70, val=15, test=15)
    
    # 100 queries for the same plot must always yield identical split
    plot_split_1 = _split_for_entity("plot_42", split_cfg)
    for _ in range(50):
        assert _split_for_entity("plot_42", split_cfg) == plot_split_1

    # Different plots can distribute across train/val/test
    splits = {_split_for_entity(f"plot_{i}", split_cfg) for i in range(100)}
    assert "train" in splits
    assert len(splits) >= 2


def test_export_defaults_to_approved_only(client, admin_user, db_session, tmp_path, monkeypatch):
    """Test that omitting status filter strictly exports 'added_to_dataset' and ignores 'pending_review'."""
    monkeypatch.setattr("app.core.paths.settings.BACKEND_ROOT", tmp_path)
    monkeypatch.setattr("app.core.paths.settings.DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr("app.core.paths.settings.UPLOAD_ROOT", tmp_path / "data" / "uploads")

    # Create test image file on disk
    img_dir = tmp_path / "data" / "uploads"
    img_dir.mkdir(parents=True, exist_ok=True)
    img_file = img_dir / "sample_leaf.jpg"
    
    # Write valid JPEG
    pil_img = PILImage.new("RGB", (200, 200), color="green")
    pil_img.save(img_file, format="JPEG")

    # Create 1 approved candidate and 1 pending_review candidate
    pred_approved = Prediction(
        user_id=admin_user["user"].id,
        raw_path=f"data/uploads/{img_file.name}",
        crop="Tomato",
        disease="Early Blight",
        status="completed",
        plot_id=101,
        result={"disease": {"label": "Early Blight"}},
    )
    pred_pending = Prediction(
        user_id=admin_user["user"].id,
        raw_path=f"data/uploads/{img_file.name}",
        crop="Tomato",
        disease="Late Blight",
        status="completed",
        plot_id=102,
        result={"disease": {"label": "Late Blight"}},
    )
    db_session.add_all([pred_approved, pred_pending])
    db_session.commit()

    cand_approved = DatasetCandidate(
        prediction_id=pred_approved.id,
        source="expert_correction",
        original_label="Healthy",
        corrected_label="Early Blight",
        image_path=f"data/uploads/{img_file.name}",
        status="added_to_dataset",
    )
    cand_pending = DatasetCandidate(
        prediction_id=pred_pending.id,
        source="expert_correction",
        original_label="Early Blight",
        corrected_label="Late Blight",
        image_path=f"data/uploads/{img_file.name}",
        status="pending_review",
    )
    db_session.add_all([cand_approved, cand_pending])
    db_session.commit()

    headers = {"Authorization": f"Bearer {admin_user['token']}"}
    payload = {
        "filters": {
            "expert": True,
            "farmer": True,
            # status omitted: should default to 'added_to_dataset'
        },
        "split": {"train": 70, "val": 15, "test": 15},
        "format": "PyTorch Folder",
        "imageTarget": "raw",
        "include_replay_buffer": False,
    }

    resp = client.post("/admin/dataset/export?download=true", json=payload, headers=headers)
    assert resp.status_code == 200

    # Inspect zip contents
    zip_bytes = io.BytesIO(resp.content)
    with zipfile.ZipFile(zip_bytes, "r") as zf:
        metadata_raw = zf.read("metadata.json")
        meta = json.loads(metadata_raw)
        
        # Must only contain the approved candidate, NOT the pending one
        assert meta["provenance"]["total_candidates"] == 1
        assert meta["candidates"][0]["id"] == cand_approved.id
        assert meta["candidates"][0]["status"] == "added_to_dataset"
        
        # Verify EXIF is clean
        img_names = [n for n in zf.namelist() if n.endswith(".jpg")]
        assert len(img_names) >= 1
        with PILImage.open(io.BytesIO(zf.read(img_names[0]))) as exported_img:
            assert len(exported_img.getexif()) == 0

        # Verify class support warning triggered (only 1 sample for Early_Blight)
        assert len(meta["provenance"]["warnings"]) >= 1
        assert "minimum recommended" in meta["provenance"]["warnings"][0]


def test_split_percentages_validation(client, admin_user):
    """Test that split percentages not totaling 100 are rejected with 422."""
    headers = {"Authorization": f"Bearer {admin_user['token']}"}
    payload = {
        "split": {"train": 70, "val": 20, "test": 20},  # 110% != 100%
        "format": "PyTorch Folder",
    }
    resp = client.post("/admin/dataset/export", json=payload, headers=headers)
    assert resp.status_code == 422
    assert "total 100" in resp.text


def test_dataset_summary_and_aliases(client, admin_user, db_session):
    """Test that GET /admin/dataset/summary and GET /admin/mlops/summary return accurate telemetry."""
    # Seed candidates with unique predictions
    pred1 = Prediction(
        user_id=admin_user["user"].id,
        raw_path="data/uploads/leaf1.jpg",
        crop="Cotton",
        disease="Bacterial Blight",
        status="completed",
        result={"disease": {"label": "Bacterial Blight"}},
    )
    pred2 = Prediction(
        user_id=admin_user["user"].id,
        raw_path="data/uploads/leaf2.jpg",
        crop="Cotton",
        disease="Bacterial Blight",
        status="completed",
        result={"disease": {"label": "Bacterial Blight"}},
    )
    db_session.add_all([pred1, pred2])
    db_session.commit()

    cand1 = DatasetCandidate(
        prediction_id=pred1.id,
        source="expert_correction",
        original_label="Healthy",
        corrected_label="Bacterial Blight",
        image_path="data/uploads/leaf1.jpg",
        status="added_to_dataset",
    )
    cand2 = DatasetCandidate(
        prediction_id=pred2.id,
        source="farmer_confirmation",
        original_label="Bacterial Blight",
        corrected_label="Bacterial Blight",
        image_path="data/uploads/leaf2.jpg",
        status="pending_review",
    )
    db_session.add_all([cand1, cand2])
    db_session.commit()

    headers = {"Authorization": f"Bearer {admin_user['token']}"}

    # Canonical dataset summary
    resp1 = client.get("/admin/dataset/summary", headers=headers)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["total"] == 2
    assert data1["expert_overridden"] == 1
    assert data1["farmer_confirmed"] == 1
    assert data1["by_status"]["added_to_dataset"] == 1
    assert data1["by_status"]["pending_review"] == 1
    assert any(c["crop"] == "Cotton" for c in data1["by_crop"])

    # MLOps alias summary
    resp2 = client.get("/api/v1/admin/mlops/summary", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["total"] == 2


def test_mlops_export_alias_and_runs_tracking(client, admin_user, db_session, tmp_path, monkeypatch):
    """Test POST /api/v1/admin/mlops/export, MlopsRun persistence, and GET /admin/mlops/runs."""
    monkeypatch.setattr("app.core.paths.settings.BACKEND_ROOT", tmp_path)
    monkeypatch.setattr("app.core.paths.settings.DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr("app.core.paths.settings.UPLOAD_ROOT", tmp_path / "data" / "uploads")

    img_dir = tmp_path / "data" / "uploads"
    img_dir.mkdir(parents=True, exist_ok=True)
    img_file = img_dir / "cotton_leaf.jpg"
    PILImage.new("RGB", (100, 100), color="blue").save(img_file, format="JPEG")

    pred = Prediction(
        user_id=admin_user["user"].id,
        raw_path=f"data/uploads/{img_file.name}",
        crop="Cotton",
        disease="Curl Virus",
        status="completed",
        plot_id=202,
        result={"disease": {"label": "Curl Virus"}},
    )
    db_session.add(pred)
    db_session.commit()

    cand = DatasetCandidate(
        prediction_id=pred.id,
        source="expert_correction",
        original_label="Healthy",
        corrected_label="Curl Virus",
        image_path=f"data/uploads/{img_file.name}",
        status="added_to_dataset",
    )
    db_session.add(cand)
    db_session.commit()

    headers = {"Authorization": f"Bearer {admin_user['token']}"}
    payload = {
        "filters": {"expert": True, "farmer": True, "crop": "Cotton", "status": "all"},
        "split": {"train": 80, "val": 10, "test": 10},
        "format": "PyTorch Folder",
        "imageTarget": "raw",
        "include_replay_buffer": False,
    }

    # Call /api/v1/admin/mlops/export alias with download=true
    resp = client.post("/api/v1/admin/mlops/export?download=true", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"

    # Verify MlopsRun was recorded in database and accessible via GET /admin/mlops/runs
    runs_resp = client.get("/admin/mlops/runs", headers=headers)
    assert runs_resp.status_code == 200
    runs_data = runs_resp.json()
    assert len(runs_data["runs"]) >= 1
    latest_run = runs_data["runs"][0]
    assert latest_run["status"] == "completed"
    assert "Cotton" in json.dumps(latest_run["dataset_export_config"])


def test_export_remote_storage_returns_signed_url(client, admin_user, db_session, tmp_path, monkeypatch):
    """Test that when STORAGE_BACKEND=supabase, POST /admin/dataset/export returns JSON with download_url."""
    monkeypatch.setattr("app.core.paths.settings.BACKEND_ROOT", tmp_path)
    monkeypatch.setattr("app.core.paths.settings.DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr("app.core.paths.settings.UPLOAD_ROOT", tmp_path / "data" / "uploads")
    monkeypatch.setattr("app.api.endpoints.mlops.settings.STORAGE_BACKEND", "supabase")

    # Mock storage
    class MockStorage:
        def save(self, data, key, content_type=None):
            return key
        def get_url(self, key, expires_in=3600):
            return f"https://mock-supabase.storage.co/{key}?token=mock-token"

    monkeypatch.setattr("app.core.storage.get_storage", lambda: MockStorage())

    img_dir = tmp_path / "data" / "uploads"
    img_dir.mkdir(parents=True, exist_ok=True)
    img_file = img_dir / "leaf.jpg"
    PILImage.new("RGB", (64, 64), color="yellow").save(img_file, format="JPEG")

    pred = Prediction(
        user_id=admin_user["user"].id,
        raw_path=f"data/uploads/{img_file.name}",
        crop="Tomato",
        disease="Early Blight",
        status="completed",
        plot_id=303,
        result={"disease": {"label": "Early Blight"}},
    )
    db_session.add(pred)
    db_session.commit()

    cand = DatasetCandidate(
        prediction_id=pred.id,
        source="expert_correction",
        original_label="Healthy",
        corrected_label="Early Blight",
        image_path=f"data/uploads/{img_file.name}",
        status="added_to_dataset",
    )
    db_session.add(cand)
    db_session.commit()

    headers = {"Authorization": f"Bearer {admin_user['token']}"}
    payload = {
        "split": {"train": 70, "val": 15, "test": 15},
        "format": "PyTorch Folder",
        "imageTarget": "raw",
        "include_replay_buffer": False,
    }

    resp = client.post("/admin/dataset/export", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/json"
    data = resp.json()
    assert data["status"] == "success"
    assert "download_url" in data
    assert "https://mock-supabase.storage.co/exports/dataset_export_" in data["download_url"]
    assert data["candidates_count"] == 1


def test_export_handles_uploads_prefix_and_missing_images(client, admin_user, db_session, tmp_path, monkeypatch):
    """Test that candidate image paths starting with uploads/ or missing on disk do not raise 422."""
    monkeypatch.setattr("app.core.paths.settings.BACKEND_ROOT", tmp_path)
    monkeypatch.setattr("app.core.paths.settings.DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr("app.core.paths.settings.UPLOAD_ROOT", tmp_path / "data" / "uploads")

    pred = Prediction(
        user_id=admin_user["user"].id,
        raw_path="uploads/20261023_test_leaf.jpg",
        crop="Tomato",
        disease="Early Blight",
        status="completed",
        plot_id=404,
        result={"disease": {"label": "Early Blight"}},
    )
    db_session.add(pred)
    db_session.commit()

    cand = DatasetCandidate(
        prediction_id=pred.id,
        source="farmer_confirmation",
        original_label="Early Blight",
        corrected_label="Early Blight",
        image_path="uploads/20261023_test_leaf.jpg",
        status="pending_review",
    )
    db_session.add(cand)
    db_session.commit()

    headers = {"Authorization": f"Bearer {admin_user['token']}"}
    payload = {
        "filters": {"expert": True, "farmer": True, "status": "all"},
        "split": {"train": 70, "val": 15, "test": 15},
        "format": "PyTorch Folder",
        "imageTarget": "raw",
        "include_replay_buffer": False,
    }

    # Must succeed (200) with download=true and not throw 422
    resp = client.post("/admin/dataset/export?download=true", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"


def test_export_status_any_normalization_and_alias(client, admin_user, db_session, tmp_path, monkeypatch):
    """Test that filters.status='Any' normalizes to CandidateStatusEnum.ALL and image_target alias works."""
    monkeypatch.setattr("app.core.paths.settings.BACKEND_ROOT", tmp_path)
    monkeypatch.setattr("app.core.paths.settings.DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr("app.core.paths.settings.UPLOAD_ROOT", tmp_path / "data" / "uploads")

    pred = Prediction(
        user_id=admin_user["user"].id,
        raw_path="uploads/test_any.jpg",
        crop="Cotton",
        disease="Bacterial Blight",
        status="completed",
        plot_id=505,
        result={"disease": {"label": "Bacterial Blight"}},
    )
    db_session.add(pred)
    db_session.commit()

    cand = DatasetCandidate(
        prediction_id=pred.id,
        source="expert_correction",
        original_label="Bacterial Blight",
        corrected_label="Bacterial Blight",
        image_path="uploads/test_any.jpg",
        status="pending_review",
    )
    db_session.add(cand)
    db_session.commit()

    headers = {"Authorization": f"Bearer {admin_user['token']}"}
    payload = {
        "filters": {"expert": True, "farmer": True, "status": "Any"},
        "split": {"train": 80, "val": 10, "test": 10},
        "format": "PyTorch Folder",
        "image_target": "preprocessed",
        "include_replay_buffer": False,
    }

    resp = client.post("/admin/dataset/export?download=true", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"




