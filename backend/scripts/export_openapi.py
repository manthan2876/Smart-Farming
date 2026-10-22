from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "ai_service"))
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "src"))

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", "openapi-schema-generation-secret-key")
os.environ.setdefault("JWT_SECRET_KEY", "openapi-schema-generation-jwt-secret")
os.environ.setdefault("CRON_SECRET", "openapi-schema-generation-cron-secret")
os.environ.setdefault("REQUIRE_REDIS", "false")

from app.main import app


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the FastAPI OpenAPI contract.")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "Docs" / "openapi.json",
    )
    output = parser.parse_args().output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
