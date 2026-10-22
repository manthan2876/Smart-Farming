"""Pytest configuration and test bootstrap for Smart Farming backend test suite."""

from __future__ import annotations

import atexit
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure backend root and backend/src are the primary import locations
TESTS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = TESTS_DIR.parent
REPO_ROOT = BACKEND_DIR.parent

# Put backend/src FIRST so `import app` resolves to backend/src/app
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "src"))

_TEST_RUNTIME_ROOT = Path(tempfile.mkdtemp(prefix="smart-farming-tests-"))
atexit.register(shutil.rmtree, _TEST_RUNTIME_ROOT, ignore_errors=True)
_TEST_ENV_FILE = _TEST_RUNTIME_ROOT / ".env.test"
_TEST_ENV_FILE.touch()

# Enforce test environment configuration
os.environ["ENV_FILE"] = str(_TEST_ENV_FILE)
os.environ["PYTHON_DOTENV_DISABLED"] = "true"
os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-32-bytes-long-for-testing-only"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-32-bytes-long-for-testing-only"
os.environ["CRON_SECRET"] = "test-cron-secret-32-chars-long"
os.environ["REQUIRE_REDIS"] = "false"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_RUNTIME_ROOT / 'test.db'}"
os.environ["STORAGE_BACKEND"] = "local"
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = ""
os.environ["SUPABASE_ANON_KEY"] = ""
os.environ["SUPABASE_JWT_SECRET"] = ""
os.environ["UPSTASH_REDIS_URL"] = ""
os.environ["UPSTASH_REDIS_REST_URL"] = ""
os.environ["UPSTASH_REDIS_REST_TOKEN"] = ""
os.environ["QSTASH_URL"] = ""
os.environ["QSTASH_TOKEN"] = ""
os.environ["QSTASH_CURRENT_SIGNING_KEY"] = ""
os.environ["QSTASH_NEXT_SIGNING_KEY"] = ""
os.environ["AI_SERVICE_URL"] = "http://127.0.0.1:8765"
os.environ["GATEWAY_API_KEY"] = ""
os.environ["OPENWEATHER_API"] = ""
os.environ["GROQ_API_KEY"] = ""

for _name in ("DATA_ROOT", "UPLOAD_ROOT", "PROCESSED_ROOT", "AUDIO_ROOT"):
    os.environ[_name] = str(_TEST_RUNTIME_ROOT / _name.lower())


@pytest.fixture(autouse=True)
def isolate_model_registry_files(monkeypatch, tmp_path_factory):
    from app.api.endpoints import model_registry

    runtime_dir = tmp_path_factory.mktemp("model-registry-runtime")
    config_path = runtime_dir / "config.yaml"
    registry_path = runtime_dir / "model_registry.json"
    shutil.copyfile(BACKEND_DIR / "config.yaml", config_path)
    shutil.copyfile(BACKEND_DIR / "model_registry.json", registry_path)
    monkeypatch.setattr(model_registry, "_CONFIG_PATH", config_path)
    monkeypatch.setattr(model_registry, "_REGISTRY_PATH", registry_path)
