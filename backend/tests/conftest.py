"""Pytest configuration and test bootstrap for Smart Farming backend test suite."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure backend root and backend/src are the primary import locations
TESTS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = TESTS_DIR.parent
REPO_ROOT = BACKEND_DIR.parent

# Put backend/src FIRST so `import app` resolves to backend/src/app
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "src"))

# Enforce test environment configuration
os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-32-bytes-long-for-testing-only"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-32-bytes-long-for-testing-only"
os.environ["CRON_SECRET"] = "test-cron-secret-32-chars-long"
os.environ["REQUIRE_REDIS"] = "false"

