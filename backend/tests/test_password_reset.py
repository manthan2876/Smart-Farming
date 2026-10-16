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
from app.models.password_reset import PasswordResetToken
from app.crud.password_reset import get_valid_password_reset_token, create_password_reset_token

# Setup in-memory SQLite database
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setattr("app.main.initialize_database", lambda: None)
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
        id="user-123",
        name="Test Farmer",
        email="farmer@example.com",
        phone="+919876543210",
        password_hash=hash_password("OldPassword123"),
        language="English",
        role="farmer",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_change_password_success(client, sample_user):
    token = create_token(sample_user.id, "access", timedelta(minutes=30))
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/auth/change-password",
        json={"old_password": "OldPassword123", "new_password": "NewSecretPassword456"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    # Verify old password no longer logs in
    login_resp = client.post(
        "/auth/login",
        json={"identifier": "farmer@example.com", "password": "OldPassword123"},
    )
    assert login_resp.status_code == 401

    # Verify new password logs in successfully
    login_resp2 = client.post(
        "/auth/login",
        json={"identifier": "farmer@example.com", "password": "NewSecretPassword456"},
    )
    assert login_resp2.status_code == 200


def test_change_password_invalid_old_password(client, sample_user):
    token = create_token(sample_user.id, "access", timedelta(minutes=30))
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/auth/change-password",
        json={"old_password": "WrongPassword!", "new_password": "NewSecretPassword456"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "Current password is incorrect" in resp.json()["detail"]


def test_change_password_identical_password(client, sample_user):
    token = create_token(sample_user.id, "access", timedelta(minutes=30))
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/auth/change-password",
        json={"old_password": "OldPassword123", "new_password": "OldPassword123"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "New password cannot be the same" in resp.json()["detail"]


def test_forgot_password_anti_enumeration(client, sample_user):
    # Non-existent email
    resp1 = client.post(
        "/auth/forgot-password",
        json={"email": "nonexistent@example.com"},
    )
    assert resp1.status_code == 200
    msg1 = resp1.json()["message"]

    # Existing user email
    resp2 = client.post(
        "/auth/forgot-password",
        json={"email": sample_user.email},
    )
    assert resp2.status_code == 200
    msg2 = resp2.json()["message"]

    # Both messages must be identical to prevent user enumeration
    assert msg1 == msg2
    assert "password reset link has been sent" in msg1


def test_reset_password_full_lifecycle(client, db_session, sample_user):
    # 1. Create a reset token for the user
    raw_token = "secure-random-test-token-xyz"
    create_password_reset_token(db_session, user_id=sample_user.id, raw_token=raw_token, expires_in_minutes=15)

    # 2. Reset password using the raw token
    resp = client.post(
        "/auth/reset-password",
        json={"token": raw_token, "new_password": "BrandNewPassword789"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    # 3. Verify single-use: token cannot be reused
    resp_reuse = client.post(
        "/auth/reset-password",
        json={"token": raw_token, "new_password": "AnotherPassword999"},
    )
    assert resp_reuse.status_code == 400

    # 4. Verify login with the brand new password
    login_resp = client.post(
        "/auth/login",
        json={"identifier": sample_user.email, "password": "BrandNewPassword789"},
    )
    assert login_resp.status_code == 200


def test_reset_password_invalid_or_expired_token(client, db_session, sample_user):
    # Invalid token
    resp = client.post(
        "/auth/reset-password",
        json={"token": "non-existent-fake-token", "new_password": "ValidNewPassword123"},
    )
    assert resp.status_code == 400
    assert "invalid or has expired" in resp.json()["detail"]

    # Expired token
    raw_token = "expired-token-123"
    rec = create_password_reset_token(db_session, user_id=sample_user.id, raw_token=raw_token, expires_in_minutes=-5)
    rec.expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    db_session.add(rec)
    db_session.commit()

    resp_expired = client.post(
        "/auth/reset-password",
        json={"token": raw_token, "new_password": "ValidNewPassword123"},
    )
    assert resp_expired.status_code == 400
