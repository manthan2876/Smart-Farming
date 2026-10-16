from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import require_admin_role
from app.core import get_session
from app.models.user import User

class MockAdminSession:
    def __init__(self):
        self.users = {
            "admin-1": User(id="admin-1", name="Admin One", email="admin1@farm.com", role="admin", password_hash="pw"),
            "admin-2": User(id="admin-2", name="Admin Two", email="admin2@farm.com", role="admin", password_hash="pw"),
            "farmer-1": User(id="farmer-1", name="Farmer Joe", email="joe@farm.com", role="farmer", password_hash="pw"),
        }

    def add(self, obj):
        pass

    def refresh(self, obj):
        pass

    def rollback(self):
        pass

    def commit(self):
        pass

    def close(self):
        pass

    def get(self, model, ident):
        if hasattr(model, "__name__") and model.__name__ == "User":
            return self.users.get(ident)
        return None

    def query(self, *args):
        session_self = self
        class QueryMock:
            def __init__(self, items):
                self._items = items

            def filter(self, *filter_args, **kwargs):
                return self

            def order_by(self, *args):
                return self

            def offset(self, n):
                return self

            def limit(self, n):
                return self

            def count(self):
                return len(self._items)

            def scalar(self):
                # Used for counting active admins
                admins = [u for u in session_self.users.values() if u.role == "admin"]
                return len(admins)

            def all(self):
                return list(self._items)

        return QueryMock(self.users.values())

@pytest.fixture
def admin_client():
    mock_session = MockAdminSession()
    old_session = app.dependency_overrides.get(get_session)
    old_admin_role = app.dependency_overrides.get(require_admin_role)

    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[require_admin_role] = lambda: "admin-1"
    client = TestClient(app)
    yield client, mock_session

    if old_session is not None:
        app.dependency_overrides[get_session] = old_session
    else:
        app.dependency_overrides.pop(get_session, None)

    if old_admin_role is not None:
        app.dependency_overrides[require_admin_role] = old_admin_role
    else:
        app.dependency_overrides.pop(require_admin_role, None)

def test_list_admin_users(admin_client):
    client, _ = admin_client
    res = client.get("/admin/users")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "users" in data
    assert data["total"] == 3

def test_update_user_role_success(admin_client):
    client, session = admin_client
    res = client.patch(
        "/admin/users/farmer-1/role",
        json={"role": "expert", "reason": "Certified agronomist onboarded"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["new_role"] == "expert"
    assert session.users["farmer-1"].role == "expert"

def test_update_user_role_invalid_role(admin_client):
    client, _ = admin_client
    res = client.patch(
        "/admin/users/farmer-1/role",
        json={"role": "invalid_super_role"},
    )
    assert res.status_code == 422

def test_admin_self_demotion_guard(admin_client):
    client, _ = admin_client
    # caller is admin-1, attempting to demote admin-1 to farmer
    res = client.patch(
        "/admin/users/admin-1/role",
        json={"role": "farmer"},
    )
    assert res.status_code == 400
    assert "cannot demote their own account" in res.json()["detail"].lower()

def test_last_admin_demotion_guard(admin_client):
    client, session = admin_client
    # Demote admin-2 first so only 1 admin remains
    session.users["admin-2"].role = "farmer"
    # Now try to demote admin-1 using another caller
    app.dependency_overrides[require_admin_role] = lambda: "some-other-caller"
    res = client.patch(
        "/admin/users/admin-1/role",
        json={"role": "farmer"},
    )
    assert res.status_code == 400
    assert "last remaining administrator" in res.json()["detail"].lower()

