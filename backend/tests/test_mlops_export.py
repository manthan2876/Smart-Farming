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
