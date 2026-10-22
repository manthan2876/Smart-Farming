# FastAPI backend

The backend provides the versioned HTTP API, authentication, database access, media authorization, and orchestration of the AI service. It uses synchronous SQLAlchemy sessions; synchronous route handlers are run by FastAPI in its thread pool.

## Local development

```bash
cd backend
uv sync --extra dev
cp .env.example .env
uv run uvicorn app.main:app --app-dir src --reload
```

Set local database, storage, and AI-service values in `.env`. Never use production credentials in local development.

## Tests and migrations

```bash
uv run pytest tests/
uv run alembic upgrade head
```

Schema changes must be made through Alembic migrations. The application does not create demo accounts automatically; use `seed_users.py` only when the required `SEED_*_PASSWORD` environment variables are set.

## Production

Render deployment is configured by [`../render.yaml`](../render.yaml). The service runs Gunicorn with Uvicorn workers, hides interactive API docs in production, and requires explicit `CORS_ORIGINS` configuration. Production secrets belong in the hosting provider's secret manager.