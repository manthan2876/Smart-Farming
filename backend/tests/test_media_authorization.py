from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_user
from app.core import get_session
from app.models.user import User
from app.models.prediction import Prediction
from app.models.image import Image

class MockMediaSession:
    def __init__(self):
        self.users = {
            "farmer-owner": User(id="farmer-owner", role="farmer", password_hash="pw"),
            "farmer-stranger": User(id="farmer-stranger", role="farmer", password_hash="pw"),
            "expert-user": User(id="expert-user", role="expert", password_hash="pw"),
            "admin-user": User(id="admin-user", role="admin", password_hash="pw"),
        }
        img1 = Image(id=201, raw_path="uploads/leaf1.jpg", processed_path="processed/leaf1.jpg")
        img2 = Image(id=202, raw_path="uploads/leaf2.jpg", processed_path="processed/leaf2.jpg")
        pred1 = Prediction(
            id=101,
            user_id="farmer-owner",
            status="pending_expert_review",
            image_id=201,
            raw_path="uploads/leaf1.jpg",
            processed_path="processed/leaf1.jpg",
            result={"stages": {"preprocessing": "completed"}},
        )
        pred2 = Prediction(
            id=102,
            user_id="farmer-owner",
            status="completed",
            image_id=202,
            raw_path="uploads/leaf2.jpg",
            processed_path="processed/leaf2.jpg",
            result={},
        )
        pred1.image = img1
        pred2.image = img2
        self.predictions = {101: pred1, 102: pred2}
        self.images = {201: img1, 202: img2}

    def rollback(self):
        pass

    def commit(self):
        pass

    def close(self):
        pass

    def get(self, model, ident):
        name = getattr(model, "__name__", "")
        if name == "User":
            return self.users.get(ident)
        if name == "Prediction":
            return self.predictions.get(ident)
        if name == "Image":
            return self.images.get(ident)
        return None


@pytest.fixture
def media_setup():
    mock_session = MockMediaSession()
    old_session = app.dependency_overrides.get(get_session)
    old_user = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_session] = lambda: mock_session
    yield mock_session

    if old_session is not None:
        app.dependency_overrides[get_session] = old_session
    else:
        app.dependency_overrides.pop(get_session, None)

    if old_user is not None:
        app.dependency_overrides[get_current_user] = old_user
    else:
        app.dependency_overrides.pop(get_current_user, None)


def test_media_auth_owner_allowed(media_setup):
    app.dependency_overrides[get_current_user] = lambda: "farmer-owner"
    client = TestClient(app)

    res = client.get("/predictions/101/media-url/raw")
    assert res.status_code == 200
    data = res.json()
    assert "url" in data
    assert "leaf1.jpg" in data["url"]


def test_media_auth_stranger_forbidden(media_setup):
    app.dependency_overrides[get_current_user] = lambda: "farmer-stranger"
    client = TestClient(app)

    res = client.get("/predictions/101/media-url/raw")
    assert res.status_code == 403
    assert "access denied" in res.json()["detail"].lower()


def test_media_auth_expert_allowed_when_pending_review(media_setup):
    app.dependency_overrides[get_current_user] = lambda: "expert-user"
    client = TestClient(app)

    # 101 is pending_expert_review -> expert can access
    res = client.get("/predictions/101/media-url/raw")
    assert res.status_code == 200

    # 102 is completed without review requested -> expert is forbidden
    res2 = client.get("/predictions/102/media-url/raw")
    assert res2.status_code == 403


def test_media_auth_admin_allowed_any(media_setup):
    app.dependency_overrides[get_current_user] = lambda: "admin-user"
    client = TestClient(app)

    # Admin can access even non-reviewed scans
    res = client.get("/predictions/102/media-url/raw")
    assert res.status_code == 200

