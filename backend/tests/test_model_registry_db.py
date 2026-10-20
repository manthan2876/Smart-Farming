from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core import Base, get_session
from app.api.deps import hash_password, create_token
from app.models.user import User
from app.models.model_registry import ModelRegistryRecord

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
def admin_token(db_session):
    admin = User(
        id="admin_test_001",
        name="Admin Test",
        phone="9999900001",
        email="admin@smartfarming.test",
        password_hash=hash_password("admin_pass123"),
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return create_token(str(admin.id), "access", timedelta(minutes=30))


def test_list_models_db_bootstrap(client, admin_token, db_session):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/models", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["storage"] == "postgresql_database"
    assert "models" in data
    # Database table should now have bootstrapped records
    records = db_session.query(ModelRegistryRecord).all()
    assert len(records) > 0


def test_promote_model_accuracy_gate_rejection(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "model_key": "tomato_disease",
        "version": "v3.0.0",
        "arch": "efficientnet_b2",
        "val_acc": 0.80,
        "test_acc": 0.82,  # Below min_test_acc=0.85
        "min_test_acc": 0.85,
    }
    response = client.post("/admin/models/promote", json=payload, headers=headers)
    assert response.status_code == 422
    assert "Promotion rejected: test_acc" in response.json()["detail"]


def test_promote_model_macro_f1_gate_rejection(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "model_key": "tomato_disease",
        "version": "v3.0.0",
        "arch": "efficientnet_b2",
        "val_acc": 0.88,
        "test_acc": 0.90,
        "macro_f1": 0.74,  # Below min_macro_f1=0.80
        "min_test_acc": 0.85,
        "min_macro_f1": 0.80,
    }
    response = client.post("/admin/models/promote", json=payload, headers=headers)
    assert response.status_code == 422
    assert "Promotion rejected: macro_f1" in response.json()["detail"]


def test_promote_model_weak_class_recall_rejection(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "model_key": "tomato_disease",
        "version": "v3.0.0",
        "arch": "efficientnet_b2",
        "val_acc": 0.91,
        "test_acc": 0.92,
        "macro_f1": 0.85,
        "min_test_acc": 0.85,
        "min_macro_f1": 0.80,
        "min_class_recall": 0.70,
        "metrics_json": {
            "per_class_report": {
                "Tomato___healthy": {"precision": 0.95, "recall": 0.96, "f1-score": 0.95},
                "Tomato___Septoria_leaf_spot": {"precision": 0.88, "recall": 0.58, "f1-score": 0.70},  # Below 0.70
            }
        },
    }
    response = client.post("/admin/models/promote", json=payload, headers=headers)
    assert response.status_code == 422
    assert "Promotion rejected: Class recall below minimum" in response.json()["detail"]
    assert "Tomato___Septoria_leaf_spot (recall=0.58)" in response.json()["detail"]


def test_promote_model_success_and_rollback(client, admin_token, db_session):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Initial baseline model in DB
    rec_v1 = ModelRegistryRecord(
        model_key="groundnut_disease",
        version="v1.0.0",
        arch="efficientnet_b2",
        status="active",
        test_acc=0.88,
        val_acc=0.87,
        num_classes=4,
        labels_json=["Healthy", "Early_Leaf_Spot", "Late_Leaf_Spot", "Rust"],
        promoted_by="system",
        promoted_at=datetime.now(timezone.utc),
    )
    db_session.add(rec_v1)
    db_session.commit()

    # Promote v2.0.0 meeting all quality gates
    payload = {
        "model_key": "groundnut_disease",
        "version": "v2.0.0",
        "arch": "efficientnet_b2",
        "val_acc": 0.94,
        "test_acc": 0.93,
        "macro_f1": 0.91,
        "temperature": 1.12,
        "min_test_acc": 0.85,
        "min_macro_f1": 0.80,
        "min_class_recall": 0.70,
        "metrics_json": {
            "per_class_report": {
                "Healthy": {"recall": 0.95},
                "Early_Leaf_Spot": {"recall": 0.92},
                "Late_Leaf_Spot": {"recall": 0.89},
                "Rust": {"recall": 0.91},
            }
        },
        "notes": "Retrained with 70/30 spatial replay buffer and calibrated T=1.12",
    }
    response = client.post("/admin/models/promote", json=payload, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["active_version"] == "v2.0.0"

    # Verify database record updated
    active = db_session.query(ModelRegistryRecord).filter_by(model_key="groundnut_disease", status="active").first()
    assert active is not None
    assert active.version == "v2.0.0"
    assert active.temperature == 1.12
    assert active.macro_f1 == 0.91

    # Verify v1.0.0 retired
    v1_rec = db_session.query(ModelRegistryRecord).filter_by(model_key="groundnut_disease", version="v1.0.0").first()
    assert v1_rec.status == "retired"

    # Now test rollback
    rollback_resp = client.post(
        "/admin/models/rollback",
        json={"model_key": "groundnut_disease", "target_version": "v1.0.0"},
        headers=headers,
    )
    assert rollback_resp.status_code == 200
    assert rollback_resp.json()["active_version"] == "v1.0.0"

    db_session.expire_all()
    active_after = db_session.query(ModelRegistryRecord).filter_by(model_key="groundnut_disease", status="active").first()
    assert active_after.version == "v1.0.0"
