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
from app.models.prediction import Prediction
from app.models.expertReview import ExpertReview

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
def expert_users(db_session):
    expert_a = User(
        id="expert-a-1",
        name="Expert Alice",
        email="alice@expert.org",
        phone="+919876543201",
        password_hash=hash_password("PassAlice123!"),
        role="expert",
    )
    expert_b = User(
        id="expert-b-2",
        name="Expert Bob",
        email="bob@expert.org",
        phone="+919876543202",
        password_hash=hash_password("PassBob123!"),
        role="expert",
    )
    farmer = User(
        id="farmer-john",
        name="Farmer John",
        email="john@farm.org",
        phone="+919876543203",
        password_hash=hash_password("PassJohn123!"),
        role="farmer",
    )
    db_session.add_all([expert_a, expert_b, farmer])
    db_session.commit()

    token_a = create_token(expert_a.id, "access", timedelta(hours=1))
    token_b = create_token(expert_b.id, "access", timedelta(hours=1))
    return {"a": expert_a, "b": expert_b, "token_a": token_a, "token_b": token_b, "farmer": farmer}


@pytest.fixture
def pending_review(db_session, expert_users):
    pred = Prediction(
        user_id=expert_users["farmer"].id,
        raw_path="data/uploads/leaf.jpg",
        crop="Tomato",
        disease="Early Blight",
        status="pending_expert_review",
        result={"disease": {"label": "Early Blight"}},
    )
    db_session.add(pred)
    db_session.commit()

    review = ExpertReview(
        prediction_id=pred.id,
        status="pending",
        claimed_by=None,
        claimed_at=None,
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)
    return review


def test_expert_claim_lock_and_conflict(client, pending_review, expert_users, db_session):
    """Test Expert A claims item, Expert B receives 409 conflict while lease is active."""
    headers_a = {"Authorization": f"Bearer {expert_users['token_a']}"}
    headers_b = {"Authorization": f"Bearer {expert_users['token_b']}"}

    # 1. Expert A claims
    resp_a = client.post(f"/expert/reviews/{pending_review.id}/claim", headers=headers_a)
    assert resp_a.status_code == 200
    data_a = resp_a.json()
    assert data_a["status"] == "claimed"
    assert data_a["claimed_by"] == expert_users["a"].id

    # 2. Expert B tries to claim the same review -> 409 Conflict
    resp_b = client.post(f"/expert/reviews/{pending_review.id}/claim", headers=headers_b)
    assert resp_b.status_code == 409
    assert "currently claimed by another expert" in resp_b.json()["detail"]

    # 3. Expert A releases claim
    resp_rel = client.post(f"/expert/reviews/{pending_review.id}/release", headers=headers_a)
    assert resp_rel.status_code == 200
    assert resp_rel.json()["status"] == "released"

    # 4. Expert B can now claim
    resp_b2 = client.post(f"/expert/reviews/{pending_review.id}/claim", headers=headers_b)
    assert resp_b2.status_code == 200
    assert resp_b2.json()["claimed_by"] == expert_users["b"].id


def test_claim_lease_expiration(client, pending_review, expert_users, db_session):
    """Test that after 15 minutes of inactivity, another expert can take over the claim."""
    headers_b = {"Authorization": f"Bearer {expert_users['token_b']}"}

    # Set claim by Expert A from 20 minutes ago
    db_session.refresh(pending_review)
    pending_review.claimed_by = expert_users["a"].id
    pending_review.claimed_at = datetime.now(timezone.utc) - timedelta(minutes=20)
    db_session.commit()

    # Expert B claims -> should succeed because lease expired
    resp_b = client.post(f"/expert/reviews/{pending_review.id}/claim", headers=headers_b)
    assert resp_b.status_code == 200
    assert resp_b.json()["claimed_by"] == expert_users["b"].id


def test_submit_review_conflict_guard(client, pending_review, expert_users, db_session):
    """Test that a review claimed by Expert A cannot be finalized by Expert B."""
    headers_a = {"Authorization": f"Bearer {expert_users['token_a']}"}
    headers_b = {"Authorization": f"Bearer {expert_users['token_b']}"}

    # Expert A claims
    resp_claim = client.post(f"/expert/reviews/{pending_review.id}/claim", headers=headers_a)
    assert resp_claim.status_code == 200

    # Expert B tries to submit review -> 409 Conflict
    payload = {
        "action": "Confirm AI Findings",
        "farmer_guidance": "Water regularly and isolate affected plant.",
    }
    resp_submit_b = client.post(f"/expert/reviews/{pending_review.id}", json=payload, headers=headers_b)
    assert resp_submit_b.status_code == 409
    assert "currently claimed by another expert" in resp_submit_b.json()["detail"]

    # Expert A submits review -> 200 OK
    resp_submit_a = client.post(f"/expert/reviews/{pending_review.id}", json=payload, headers=headers_a)
    assert resp_submit_a.status_code == 200
    data = resp_submit_a.json()
    assert data["status"] == "success"

    # Verify DB record is finalized and claim cleared
    db_session.expire_all()
    updated = db_session.get(ExpertReview, pending_review.id)
    assert updated.status == "verified"
    assert updated.expert_id == expert_users["a"].id
    assert updated.claimed_by is None
