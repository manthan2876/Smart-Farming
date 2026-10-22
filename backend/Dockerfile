FROM ghcr.io/astral-sh/uv:0.13.0 AS uv

FROM python:3.12-slim AS builder

ENV VIRTUAL_ENV=/opt/venv
ENV UV_PROJECT_ENVIRONMENT=${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /bin/uv
WORKDIR /build
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project --python /usr/local/bin/python

FROM python:3.12-slim AS runtime

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --uid 10001 --create-home appuser \
    && mkdir -p /app/data \
    && chown appuser:appuser /app/data

WORKDIR /app
COPY --from=builder --chown=appuser:appuser "${VIRTUAL_ENV}" "${VIRTUAL_ENV}"
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser alembic.ini ./
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser config.yaml ./
COPY --chown=appuser:appuser model_registry.json ./

USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl --fail --silent http://127.0.0.1:${PORT:-8080}/ready || exit 1

CMD ["sh", "-c", "exec gunicorn app.main:app --workers ${WEB_CONCURRENCY:-1} --worker-class uvicorn_worker.UvicornWorker --bind 0.0.0.0:${PORT:-8080} --chdir /app/src --timeout 150 --access-logfile - --error-logfile -"]
