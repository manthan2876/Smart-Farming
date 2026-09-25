FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code, migrations, and configuration
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY config.yaml .
COPY model_registry.json .

# Cloud Run exposes port via $PORT
EXPOSE 8080

# Start FastAPI app
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --app-dir src
