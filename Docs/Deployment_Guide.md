# Smart Farming — Deployment Guide

**Project:** AI-Powered Smart Farming
**Last Updated:** September 2026

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Development Setup (Without Docker)](#3-development-setup-without-docker)
   - 3.1 [Backend (FastAPI)](#31-backend-fastapi)
   - 3.2 [ARQ Worker](#32-arq-worker)
   - 3.3 [Frontend (React)](#33-frontend-react)
4. [Docker Compose — Full Stack](#4-docker-compose--full-stack)
   - 4.1 [Directory Structure](#41-directory-structure)
   - 4.2 [Environment File](#42-environment-file)
   - 4.3 [docker-compose.yml](#43-docker-composeyml)
5. [Dockerfiles](#5-dockerfiles)
   - 5.1 [Backend Dockerfile](#51-backend-dockerfile)
   - 5.2 [Frontend Dockerfile](#52-frontend-dockerfile)
6. [Nginx Configuration](#6-nginx-configuration)
7. [Database Setup & Migrations](#7-database-setup--migrations)
8. [MinIO Provisioning](#8-minio-provisioning)
9. [ML Model Placement](#9-ml-model-placement)
10. [Production Checklist](#10-production-checklist)
11. [Monitoring & Operations](#11-monitoring--operations)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Architecture Overview

```
                         ┌─────────────────────┐
                         │   Browser / Client   │
                         └────────┬─────────────┘
                                  │ HTTPS :443
                         ┌────────▼─────────────┐
                         │   Nginx (Frontend)    │
                         │  React SPA + Proxy    │
                         └────────┬─────────────┘
                    /api/ │                │ /ws/
                 ┌─────────▼────┐  ┌──────▼──────────┐
                 │  FastAPI     │  │  WebSocket       │
                 │  Backend     │  │  (same process)  │
                 └──┬────┬──────┘  └─────────────────┘
                    │    │
          ┌─────────┘    └──────────┐
   ┌──────▼──────┐         ┌────────▼────────┐
   │ PostgreSQL  │         │   Redis (ARQ)   │
   │  :5432      │         │   :6379         │
   └─────────────┘         └────────┬────────┘
                                    │ job queue
                           ┌────────▼────────┐
                           │   ARQ Worker    │
                           │  (async tasks)  │
                           └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │  MinIO / AWS S3 │
                           │  Object Storage │
                           └─────────────────┘
```

| Component     | Technology                     | Port(s)    |
|---------------|-------------------------------|------------|
| Backend API   | FastAPI + Uvicorn (Python 3.11)| 8000       |
| ARQ Worker    | ARQ async job worker (Python) | —          |
| Frontend      | React SPA served by Nginx     | 80, 443    |
| Database      | PostgreSQL 15                 | 5432       |
| Job Queue     | Redis 7                       | 6379       |
| Object Storage| MinIO (S3-compatible)         | 9000, 9001 |
| ML Models     | PyTorch (`.pth`) / YOLO (`.pt`)| — (file mount) |

---

## 2. Prerequisites

### Development Machine

| Tool | Minimum Version | Notes |
|------|----------------|-------|
| Python | 3.11+ | Use `pyenv` or installer |
| Node.js | 18 LTS+ | Use `nvm` or installer |
| Git | 2.x+ | |
| PostgreSQL client (`psql`) | 15+ | Optional for local DB inspect |

### Production / CI Server

| Tool | Minimum Version | Notes |
|------|----------------|-------|
| Docker | 24.x+ | |
| Docker Compose | v2.x (`docker compose`) | Included with Docker Desktop |
| `mc` (MinIO Client) | Latest | For bucket provisioning |
| Certbot / Let's Encrypt | Latest | For TLS certificates |

> [!IMPORTANT]
> Ensure the production server has at least **4 GB RAM** and **20 GB disk** before starting. ML model files can be 200 MB–1 GB each.

---

## 3. Development Setup (Without Docker)

### 3.1 Backend (FastAPI)

```bash
# 1. Move into the backend directory
cd backend

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
#    Linux / macOS:
source .venv/bin/activate
#    Windows (PowerShell):
.venv\Scripts\Activate.ps1
#    Windows (CMD):
.venv\Scripts\activate.bat

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Create your local environment file
cp .env.example .env
```

Open `.env` in your editor and configure the following at minimum:

```dotenv
# .env (backend — development)

DATABASE_URL=postgresql://sfuser:sfpass@localhost:5432/smartfarming
REDIS_URL=redis://localhost:6379

# Storage: set to "local" to skip S3/MinIO during local dev
STORAGE_BACKEND=local

# Security — change these before any shared environment
SECRET_KEY=dev-secret-key-change-me
JWT_SECRET_KEY=dev-jwt-key-change-me

ENVIRONMENT=development
DEBUG=True

# Required for LLM recommendation features
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional — only needed for TTS / translation features
GOOGLE_TTS_API_KEY=
GOOGLE_TRANSLATION_API_KEY=

CORS_ORIGINS=http://localhost:5173
```

```bash
# 6. Run database migrations
alembic upgrade head

# 7. (Optional) Seed initial admin user
python seed_users.py

# 8. Start the development server
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.

---

### 3.2 ARQ Worker

Run this in a **separate terminal** alongside the backend server:

```bash
cd backend

# Activate the same virtual environment
source .venv/bin/activate          # Linux / macOS
# or
.venv\Scripts\Activate.ps1         # Windows PowerShell

# Start the async job worker
python -m arq src.app.worker.WorkerSettings
```

> [!NOTE]
> The ARQ worker processes background tasks such as image inference, report generation, and notification dispatch. The backend API will return job IDs and the worker will pick them up from Redis. Without the worker running, async endpoints will queue tasks but never execute them.

---

### 3.3 Frontend (React)

```bash
# 1. Move into the frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Create a local environment file
cp .env.example .env
```

Edit `.env`:

```dotenv
# .env (frontend — development)
VITE_API_BASE_URL=http://localhost:8000
```

```bash
# 4. Start the Vite development server
npm run dev
```

The React app will be available at `http://localhost:5173` with hot module replacement enabled.

---

## 4. Docker Compose — Full Stack

### 4.1 Directory Structure

Expected layout at the project root before running `docker compose up`:

```
Smart-Farming/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   ├── models/               ← ML model files (host-mounted, read-only)
│   │   ├── crop_identifier_v1.pth
│   │   └── ...
│   └── .env.example
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── nginx.conf                ← Nginx site config (host-mounted)
├── .env                      ← Root .env with secrets (never commit)
└── docker-compose.yml
```

---

### 4.2 Environment File

Create a `.env` file at the **project root** (next to `docker-compose.yml`). Docker Compose will auto-load it.

```dotenv
# .env (project root — NEVER commit this file)

# PostgreSQL
POSTGRES_DB=smartfarming
POSTGRES_USER=sfuser
POSTGRES_PASSWORD=sfpass

# Application secrets — generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=replace-with-random-32-plus-char-string
JWT_SECRET_KEY=replace-with-another-random-32-plus-char-string

# MinIO / S3
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_REGION=us-east-1
AWS_S3_BUCKET=smart-farming-media

# External API keys
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_TTS_API_KEY=your-google-tts-key
GOOGLE_TRANSLATION_API_KEY=your-google-translate-key

# CORS — set to your actual frontend domain in production
CORS_ORIGINS=https://yourfrontend.com
```

> [!CAUTION]
> Add `.env` to `.gitignore` immediately. Committing secrets to version control is a critical security risk.

---

### 4.3 docker-compose.yml

```yaml
version: '3.9'

services:

  # ─── Infrastructure ────────────────────────────────────────────────────────

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-smartfarming}
      POSTGRES_USER: ${POSTGRES_USER:-sfuser}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-sfpass}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-sfuser} -d ${POSTGRES_DB:-smartfarming}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - sfnet

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - sfnet

  minio:
    image: minio/minio:latest
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-minioadmin}
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"   # S3 API
      - "9001:9001"   # MinIO Web Console
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
    networks:
      - sfnet

  # ─── Application ───────────────────────────────────────────────────────────

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-sfuser}:${POSTGRES_PASSWORD:-sfpass}@postgres/${POSTGRES_DB:-smartfarming}
      REDIS_URL: redis://redis:6379
      STORAGE_BACKEND: s3
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID:-minioadmin}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY:-minioadmin}
      AWS_REGION: ${AWS_REGION:-us-east-1}
      AWS_S3_BUCKET: ${AWS_S3_BUCKET:-smart-farming-media}
      AWS_S3_ENDPOINT_URL: http://minio:9000
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      ENVIRONMENT: production
      DEBUG: "False"
      REQUIRE_REDIS: "True"
      HF_TOKEN: ${HF_TOKEN}
      GOOGLE_TTS_API_KEY: ${GOOGLE_TTS_API_KEY}
      GOOGLE_TRANSLATION_API_KEY: ${GOOGLE_TRANSLATION_API_KEY}
      CORS_ORIGINS: ${CORS_ORIGINS:-https://yourfrontend.com}
    volumes:
      - ./backend/models:/app/models:ro   # ML models — read-only mount
      - backend_data:/app/data
    command: uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --workers 2
    ports:
      - "8000:8000"
    networks:
      - sfnet

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-sfuser}:${POSTGRES_PASSWORD:-sfpass}@postgres/${POSTGRES_DB:-smartfarming}
      REDIS_URL: redis://redis:6379
      STORAGE_BACKEND: s3
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID:-minioadmin}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY:-minioadmin}
      AWS_REGION: ${AWS_REGION:-us-east-1}
      AWS_S3_BUCKET: ${AWS_S3_BUCKET:-smart-farming-media}
      AWS_S3_ENDPOINT_URL: http://minio:9000
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      ENVIRONMENT: production
      DEBUG: "False"
      HF_TOKEN: ${HF_TOKEN}
      GOOGLE_TTS_API_KEY: ${GOOGLE_TTS_API_KEY}
      GOOGLE_TRANSLATION_API_KEY: ${GOOGLE_TRANSLATION_API_KEY}
    volumes:
      - ./backend/models:/app/models:ro
      - backend_data:/app/data
    command: python -m arq src.app.worker.WorkerSettings
    networks:
      - sfnet

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_BASE_URL: https://yourfrontend.com
    restart: unless-stopped
    depends_on:
      - backend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ssl_certs:/etc/ssl/certs:ro
    networks:
      - sfnet

# ─── Volumes ─────────────────────────────────────────────────────────────────

volumes:
  postgres_data:
  minio_data:
  backend_data:
  ssl_certs:

# ─── Networks ─────────────────────────────────────────────────────────────────

networks:
  sfnet:
    driver: bridge
```

#### Starting the Stack

```bash
# First time — build images and start all services in background
docker compose up --build -d

# View logs for all services
docker compose logs -f

# View logs for a specific service
docker compose logs -f backend
docker compose logs -f worker

# Stop all services (preserves volumes)
docker compose down

# Stop and remove volumes (destructive — wipes DB and storage)
docker compose down -v
```

---

## 5. Dockerfiles

### 5.1 Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
# ──────────────────────────────────────────────
# Smart Farming — Backend Dockerfile
# ──────────────────────────────────────────────
FROM python:3.11-slim AS base

# Install system dependencies required by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create directories that will be populated by volumes
RUN mkdir -p /app/models /app/data

# Run database migrations at container startup via entrypoint
# (The CMD in docker-compose.yml overrides the default CMD below)
EXPOSE 8000

# Default command: run Alembic migrations then start the server.
# In docker-compose.yml, the backend service overrides CMD directly,
# so wrap in a shell entrypoint for migration + start:
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.app.main:app --host 0.0.0.0 --port 8000"]
```

> [!TIP]
> Running `alembic upgrade head` in the `CMD` ensures migrations apply on every container start, which is safe and idempotent. For zero-downtime deployments, run migrations as a separate one-off task before scaling the new container.

---

### 5.2 Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
# ──────────────────────────────────────────────
# Smart Farming — Frontend Dockerfile (multi-stage)
# ──────────────────────────────────────────────

# Stage 1: Build the React application
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci --prefer-offline

# Copy the rest of the source
COPY . .

# VITE_API_BASE_URL is injected at build time via --build-arg in docker-compose
ARG VITE_API_BASE_URL=https://yourfrontend.com
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build the production bundle
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:1.25-alpine AS production

# Remove the default Nginx welcome page
RUN rm -rf /usr/share/nginx/html/*

# Copy built static files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# The Nginx config is mounted at runtime via docker-compose volume
EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
```

---

## 6. Nginx Configuration

Create `nginx.conf` at the **project root** (mounted into the frontend container):

```nginx
# ──────────────────────────────────────────────
# Smart Farming — Nginx Configuration
# ──────────────────────────────────────────────

# Redirect all HTTP traffic to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # ── TLS Certificates (mounted via ssl_certs volume) ──
    ssl_certificate     /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/certs/privkey.pem;

    # Modern TLS settings
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options    nosniff always;
    add_header X-Frame-Options           SAMEORIGIN always;
    add_header Referrer-Policy           "strict-origin-when-cross-origin" always;

    # Maximum upload size (match backend setting)
    client_max_body_size 15M;

    # ── Serve React SPA ──
    root  /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets aggressively
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # ── Reverse Proxy — REST API ──
    location /api/ {
        proxy_pass         http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }

    # ── Reverse Proxy — WebSocket ──
    location /ws/ {
        proxy_pass         http://backend:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade    $http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host       $host;
        proxy_set_header   X-Real-IP  $remote_addr;
        proxy_read_timeout 3600s;   # keep WS connections alive
    }

    # ── Health check endpoint (no auth required) ──
    location /health {
        proxy_pass http://backend:8000/health;
    }
}
```

> [!NOTE]
> Replace `yourdomain.com` with your actual domain everywhere in this file. The SSL certificate files (`fullchain.pem` and `privkey.pem`) are expected inside the `ssl_certs` Docker volume. See the [TLS / Let's Encrypt](#111-tlsssl-certificates) section for how to provision them.

---

## 7. Database Setup & Migrations

### 7.1 Alembic Migrations

```bash
# Apply all pending migrations (run this before starting the backend)
alembic upgrade head

# Check current migration state
alembic current

# Show migration history
alembic history --verbose

# Generate a new migration after model changes
alembic revision --autogenerate -m "add_farm_table"

# Downgrade one step (rollback)
alembic downgrade -1

# Downgrade to a specific revision
alembic downgrade <revision_id>
```

> [!IMPORTANT]
> Always run `alembic upgrade head` **before** starting or restarting the backend in production. The backend `CMD` in the Dockerfile does this automatically, but it's worth verifying manually after a schema-changing deployment.

### 7.2 Seed Initial Data

```bash
# From the backend directory (with venv activated or inside the container)
python seed_users.py
```

To run inside a running Docker container:

```bash
docker compose exec backend python seed_users.py
```

### 7.3 Database Access (Production)

```bash
# Connect to PostgreSQL via psql (inside the container)
docker compose exec postgres psql -U sfuser -d smartfarming

# Take a manual backup
docker compose exec postgres pg_dump -U sfuser smartfarming > backup_$(date +%Y%m%d).sql

# Restore from backup
docker compose exec -T postgres psql -U sfuser smartfarming < backup_20260901.sql
```

---

## 8. MinIO Provisioning

MinIO must be provisioned with a bucket after its first start. This step is **one-time** and only needs to be repeated if the `minio_data` volume is destroyed.

### 8.1 Install MinIO Client (`mc`)

```bash
# Linux
curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/

# macOS
brew install minio/stable/mc

# Windows — download from https://dl.min.io/client/mc/release/windows-amd64/mc.exe
```

### 8.2 Provision the Bucket

```bash
# 1. Register the local MinIO instance as an alias
mc alias set local http://localhost:9000 minioadmin minioadmin

# 2. Create the media bucket
mc mb local/smart-farming-media

# 3. (Optional) Set bucket to public-read for direct media URLs
#    Skip this if you are using pre-signed URLs exclusively (recommended for production)
mc anonymous set download local/smart-farming-media

# 4. Verify the bucket exists
mc ls local/
```

### 8.3 Automated Bucket Init (CI/CD)

For automated environments, you can use the MinIO `mc` client inside the compose network:

```bash
# Run a one-off mc container to create the bucket after minio is healthy
docker compose run --rm --entrypoint sh minio -c "
  mc alias set local http://minio:9000 minioadmin minioadmin &&
  mc mb --ignore-existing local/smart-farming-media
"
```

### 8.4 Using AWS S3 Instead of MinIO

To swap MinIO for real AWS S3, update the backend environment variables:

```dotenv
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=ap-south-1
AWS_S3_BUCKET=smart-farming-media-prod
# Remove or leave blank — no custom endpoint for real AWS S3
AWS_S3_ENDPOINT_URL=
```

Remove the `minio` service from `docker-compose.yml` (or comment it out) when using AWS S3.

---

## 9. ML Model Placement

Model files must be present on the **host machine** before starting the Docker Compose stack. They are bind-mounted into the `backend` and `worker` containers as read-only.

### 9.1 Expected Directory Structure

```
backend/models/
├── crop_identifier_v1.pth          ← Crop identification model weights
├── crop_identifier_labels.json     ← Class label mapping
├── disease_Cotton.pth              ← Cotton disease classifier
├── disease_Cotton_labels.json
├── disease_Groundnut.pth           ← Groundnut disease classifier
├── disease_Groundnut_labels.json
├── disease_Pepper_Bell.pth         ← Pepper (Bell) disease classifier
├── disease_Pepper_Bell_labels.json
├── disease_Potato.pth              ← Potato disease classifier
├── disease_Potato_labels.json
├── disease_Tomato.pth              ← Tomato disease classifier
├── disease_Tomato_labels.json
└── pest_classifier/
    └── pest_classifier.pt          ← YOLO-based pest detection model
```

### 9.2 Verification

After placing model files, verify the mount is correct inside a running container:

```bash
docker compose exec backend ls -lh /app/models/
docker compose exec backend ls -lh /app/models/pest_classifier/
```

### 9.3 Notes on Model Files

- `.pth` files are standard PyTorch checkpoint files.
- `.pt` files are YOLO (Ultralytics) serialised models.
- The `models/` directory is mounted **read-only** (`:ro`) — the application never writes to it.
- Model files are **not** built into the Docker image; they are always sourced from the host. This avoids bloating the image and allows model updates without rebuilding.
- Do **not** commit large model files to Git. Use Git LFS, a shared network drive, or an S3 bucket as the model registry, and download them to `backend/models/` during your CI/CD pipeline or server provisioning step.

---

## 10. Production Checklist

Work through this checklist before going live.

### Security

- [ ] **Change `SECRET_KEY`** — Generate with:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] **Change `JWT_SECRET_KEY`** — Generate a separate value with the same command above.
- [ ] **Set `ENVIRONMENT=production`** and **`DEBUG=False`** in the backend environment.
- [ ] **Set `CORS_ORIGINS`** to your exact frontend domain (no wildcard `*` in production).
- [ ] **Change MinIO credentials** — Replace `minioadmin` / `minioadmin` with strong credentials.
- [ ] **Add `.env` to `.gitignore`** — Verify with `git status` that secrets are not tracked.
- [ ] **Enable HTTPS** — See [Section 11.1](#111-tlsssl-certificates).

### Database

- [ ] Use **PostgreSQL** (not SQLite) — confirm `DATABASE_URL` starts with `postgresql://`.
- [ ] Run **`alembic upgrade head`** before the first backend start and after every deploy.
- [ ] Schedule **automated PostgreSQL backups** (e.g., `pg_dump` via cron or a managed backup service).
- [ ] Test a **restore from backup** before go-live.

### Redis / ARQ Worker

- [ ] Set **`REQUIRE_REDIS=True`** in the backend environment so the app refuses to start without Redis.
- [ ] Ensure the **ARQ Worker** container is running and healthy (`docker compose ps`).
- [ ] Configure **automatic worker restart** — the `restart: unless-stopped` in docker-compose handles this.
- [ ] Consider using **supervisor** or **systemd** if running without Docker, to restart the worker on crash.

### Storage

- [ ] **Provision the S3 / MinIO bucket** — See [Section 8](#8-minio-provisioning).
- [ ] Set **`S3_PRESIGNED_EXPIRY_SECONDS`** to an appropriate value (e.g., `3600` for 1 hour).
- [ ] Schedule **MinIO / S3 volume backups** if using MinIO locally.

### External API Keys

- [ ] **`HF_TOKEN`** — Required for Hugging Face LLM-based crop recommendations.
- [ ] **`GOOGLE_TTS_API_KEY`** — Required for Text-to-Speech features.
- [ ] **`GOOGLE_TRANSLATION_API_KEY`** — Required for multilingual translation features.

### ML Models

- [ ] All model `.pth` / `.pt` files are present in `backend/models/` on the host.
- [ ] Verified the mount with `docker compose exec backend ls -lh /app/models/`.

### Nginx / TLS

- [ ] `nginx.conf` is in place at the project root.
- [ ] SSL certificate files are available in the `ssl_certs` volume.
- [ ] HTTP→HTTPS redirect is working.
- [ ] `client_max_body_size` is set to at least **15M** (matches any backend upload limit).

### Observability

- [ ] Set up **log rotation** for uvicorn / Nginx logs.
- [ ] Set up **health check monitoring** (e.g., UptimeRobot, Grafana, or a cron pinging `/health`).
- [ ] Review Docker container logs after first startup for any errors.

---

## 11. Monitoring & Operations

### 11.1 TLS/SSL Certificates

#### Option A — Let's Encrypt (Certbot, recommended for public servers)

```bash
# Install Certbot on the host
sudo apt install certbot

# Obtain a certificate (standalone mode — temporarily stop Nginx if running on :80)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates are saved to: /etc/letsencrypt/live/yourdomain.com/
# Copy them into the ssl_certs Docker volume:
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem \
        $(docker volume inspect sfnet_ssl_certs --format '{{.Mountpoint}}')/fullchain.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem \
        $(docker volume inspect sfnet_ssl_certs --format '{{.Mountpoint}}')/privkey.pem

# Restart the frontend container to pick up the new certs
docker compose restart frontend
```

Set up auto-renewal:

```bash
# Add to root crontab (crontab -e)
0 3 1 * * certbot renew --quiet && \
  cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /var/lib/docker/volumes/sfnet_ssl_certs/_data/ && \
  cp /etc/letsencrypt/live/yourdomain.com/privkey.pem  /var/lib/docker/volumes/sfnet_ssl_certs/_data/ && \
  docker compose -f /path/to/project/docker-compose.yml restart frontend
```

#### Option B — Self-signed (development / internal only)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout privkey.pem \
  -out fullchain.pem \
  -subj "/CN=localhost"
```

---

### 11.2 Viewing Logs

```bash
# All services, follow mode
docker compose logs -f

# Specific service, last 100 lines
docker compose logs --tail=100 backend
docker compose logs --tail=100 worker
docker compose logs --tail=100 frontend

# PostgreSQL slow query log (inside container)
docker compose exec postgres psql -U sfuser -d smartfarming \
  -c "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

---

### 11.3 Scaling the Backend

```bash
# Scale backend to 3 replicas (requires a load balancer in front)
docker compose up --scale backend=3 -d
```

For robust horizontal scaling, use Docker Swarm or Kubernetes instead of `docker compose`.

---

### 11.4 Updating the Application

```bash
# 1. Pull the latest code
git pull origin main

# 2. Rebuild images
docker compose build

# 3. Restart services with new images (migrations applied automatically in CMD)
docker compose up -d

# 4. Verify all containers are running and healthy
docker compose ps
```

---

### 11.5 ARQ Worker — Crash Recovery (Without Docker)

If running without Docker (bare-metal / VM), use one of the following to keep the worker alive:

**Using systemd:**

```ini
# /etc/systemd/system/smartfarming-worker.service
[Unit]
Description=Smart Farming ARQ Worker
After=network.target redis.service

[Service]
User=ubuntu
WorkingDirectory=/srv/smart-farming/backend
ExecStart=/srv/smart-farming/backend/.venv/bin/python -m arq src.app.worker.WorkerSettings
Restart=always
RestartSec=5
EnvironmentFile=/srv/smart-farming/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable smartfarming-worker
sudo systemctl start  smartfarming-worker
sudo systemctl status smartfarming-worker
```

---

## 12. Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `relation "X" does not exist` on backend start | Migrations not applied | Run `alembic upgrade head` or check the CMD entrypoint |
| Worker picks up no jobs | Redis not reachable from worker container | Verify `REDIS_URL` and check `docker compose ps` for Redis health |
| `S3` / MinIO `NoSuchBucket` error | Bucket not provisioned | Run the `mc mb` commands in [Section 8.2](#82-provision-the-bucket) |
| Frontend shows blank page / 404 on refresh | SPA routing not configured | Verify `try_files $uri $uri/ /index.html;` is in Nginx config |
| WebSocket connection drops immediately | Nginx not forwarding Upgrade headers | Ensure the `/ws/` location block has `Upgrade` and `Connection` headers set |
| `CORS` error in browser | `CORS_ORIGINS` mismatch | Set `CORS_ORIGINS` exactly to the frontend origin (no trailing slash) |
| ML inference returns `FileNotFoundError` | Model file missing or wrong path | Verify `backend/models/` is populated and the volume mount is correct |
| `HF_TOKEN` error in LLM endpoints | Token not set or invalid | Set a valid `HF_TOKEN` from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| Container exits immediately after start | Missing required env var | Check `docker compose logs <service>` for the exact error |
| MinIO console unreachable at `:9001` | Port not exposed or firewall rule | Verify `ports: "9001:9001"` in compose and open port in server firewall |

---

*This guide covers version 1.x of the Smart Farming deployment. For questions or issues, refer to the project repository or contact the DevOps lead.*
