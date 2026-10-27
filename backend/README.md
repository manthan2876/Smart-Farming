# FastAPI Backend Gateway

The backend provides the versioned REST API (`/api/v1` canonical with unversioned compatibility aliases), Argon2id authentication with JWT and refresh token rotation, PostgreSQL database access via SQLAlchemy 2.0 and Alembic, secure time-bounded media authorization (Supabase Object Storage signed URLs), and orchestration of the Hugging Face Spaces AI inference microservice. It uses synchronous SQLAlchemy sessions; synchronous route handlers run safely in FastAPI's thread pool to prevent event loop starvation.

## Local Development

```bash
cd backend
uv sync --extra dev
cp .env.example .env
uv run uvicorn app.main:app --app-dir src --reload
```

Set local database (`DATABASE_URL`), storage (`STORAGE_BACKEND=local`), and AI-service values in `.env`. Never use production credentials in local development.

## Tests, Migrations & OpenAPI Contract

```bash
# Run pytest suite (unit, service, security, and contract tests)
uv run pytest tests/

# Apply versioned database migrations
uv run alembic upgrade head

# Export checked-in OpenAPI contract snapshot to Docs/openapi.json
uv run python scripts/export_openapi.py
```

Schema changes must be made through versioned Alembic migrations. The application does not create demo accounts automatically; use `seed_users.py` only when the required `SEED_*_PASSWORD` environment variables are set.

## Security & CodeQL Hardening

The backend adheres to strict zero-alert GitHub Advanced Security CodeQL standards:
- **Log Injection (CWE-117)**: All user/entity identifiers and request parameters are sanitized via `sanitize_for_log` before entering application logs.
- **SSRF (CWE-918)**: Strict URL boundary validation and path sanitizers for remote media fetching.
- **Path Injection (CWE-22 / CWE-73)**: Local storage and cache file paths are validated against directory traversal attacks.
- **Stack Trace Exposure (CWE-209)**: Exceptions are masked with opaque error IDs; raw stack traces are suppressed in HTTP responses.
- **Sensitive Data Logging (CWE-532)**: Credentials, JWT tokens, and phone numbers are scrubbed from loggers.

## Production

Render deployment is configured by [`../render.yaml`](../render.yaml). The service runs Gunicorn with Uvicorn workers, hides interactive API docs in production, and requires explicit `CORS_ORIGINS` configuration. Production secrets belong in the hosting provider's secret manager.