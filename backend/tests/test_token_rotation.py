from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core import Base, get_session
from app.api.deps import hash_password, create_token_pair
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.crud.refresh_token import (
    hash_token,
    store_refresh_token,
    rotate_refresh_token,
)

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
def sample_user(db_session):
    user = User(
        id="user-rotate-1",
        name="Security Tester",
        email="security@example.com",
        phone="+919876543210",
        password_hash=hash_password("SecPass123!"),
        language="English",
        role="farmer",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_token_rotation_crud(db_session, sample_user):
    """Test CRUD level rotation: issuing, rotating, and verifying state transitions."""
    tokens = create_token_pair(sample_user.id)
    raw_rt = tokens["refresh_token"]

    record = store_refresh_token(db_session, sample_user.id, raw_rt)
    assert record.user_id == sample_user.id
    assert record.revoked is False
    assert record.replaced_by_hash is None

    # Rotate token
    new_tokens = create_token_pair(sample_user.id)
    new_rt = new_tokens["refresh_token"]
    rotated_rec = rotate_refresh_token(db_session, raw_rt, new_rt)
    assert rotated_rec is not None
    assert rotated_rec.user_id == sample_user.id
    assert rotated_rec.token_hash == hash_token(new_rt)
    assert rotated_rec.revoked is False

    # Verify old record is revoked and linked to new token hash
    db_session.refresh(record)
    assert record.revoked is True
    assert record.replaced_by_hash == hash_token(new_rt)


def test_token_reuse_detection_revokes_all(db_session, sample_user):
    """Test that reusing an already rotated/revoked token triggers theft detection and revokes all user tokens."""
    tokens = create_token_pair(sample_user.id)
    raw_rt = tokens["refresh_token"]
    store_refresh_token(db_session, sample_user.id, raw_rt)

    # Legit rotation
    new_tokens = create_token_pair(sample_user.id)
    new_rt = new_tokens["refresh_token"]
    rotate_refresh_token(db_session, raw_rt, new_rt)

    # Attacker tries to replay the old raw_rt
    with pytest.raises(Exception) as excinfo:
        another_tokens = create_token_pair(sample_user.id)
        rotate_refresh_token(db_session, raw_rt, another_tokens["refresh_token"])
    assert "reuse" in str(excinfo.value.detail).lower() or "compromised" in str(excinfo.value.detail).lower()

    # Theft detection should have revoked the legitimate new token too
    legit_record = db_session.query(RefreshToken).filter(RefreshToken.token_hash == hash_token(new_rt)).first()
    assert legit_record is not None
    assert legit_record.revoked is True


def test_auth_refresh_endpoint(client, db_session, sample_user):
    """Test POST /auth/refresh rotates token via JSON body."""
    tokens = create_token_pair(sample_user.id)
    raw_rt = tokens["refresh_token"]

    store_refresh_token(db_session, sample_user.id, raw_rt)
    db_session.commit()

    # Call endpoint
    resp = client.post("/auth/refresh", json={"refresh_token": raw_rt})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != raw_rt


def test_auth_logout_endpoint_revokes(client, db_session, sample_user):
    """Test POST /auth/logout revokes refresh token."""
    tokens = create_token_pair(sample_user.id)
    raw_rt = tokens["refresh_token"]

    store_refresh_token(db_session, sample_user.id, raw_rt)
    db_session.commit()

    # Logout
    resp = client.post("/auth/logout", json={"refresh_token": raw_rt})
    assert resp.status_code == 200

    # Ensure token is now revoked
    db_session.expire_all()
    rec = db_session.query(RefreshToken).filter(RefreshToken.token_hash == hash_token(raw_rt)).first()
    assert rec is not None
    assert rec.revoked is True

    # Trying to refresh with the logged-out token should fail
    refresh_resp = client.post("/auth/refresh", json={"refresh_token": raw_rt})
    assert refresh_resp.status_code == 401
