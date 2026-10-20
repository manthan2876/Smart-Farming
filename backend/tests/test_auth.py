from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.core import Base, get_session
from app.api import (
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
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


def test_password_hash_round_trip() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert password_hash != "correct horse battery staple"
    assert verify_password("correct horse battery staple", password_hash)
    assert not verify_password("wrong password", password_hash)


def test_access_and_refresh_tokens_have_separate_types() -> None:
    tokens = create_token_pair("farmer-1")

    assert decode_token(tokens["access_token"]) == "farmer-1"
    assert decode_token(tokens["refresh_token"], expected_type="refresh") == "farmer-1"

    try:
        decode_token(tokens["refresh_token"])
    except ValueError:
        pass
    else:
        raise AssertionError(
            "A refresh token must not authenticate as an access token."
        )


def test_decode_invalid_token() -> None:
    try:
        decode_token("invalid.token.payload")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid token should raise ValueError.")


def test_guest_login_endpoint(client) -> None:
    resp = client.post("/auth/guest")
    assert resp.status_code == 200
    data = resp.json()
    assert "tokens" in data
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]
    assert data["user"]["name"] == "Guest Farmer"
    assert data["user"]["role"] == "farmer"
    assert data["user"]["id"].startswith("guest_")


