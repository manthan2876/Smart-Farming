# Smart Farming — Deployment Guide

**Project:** AI-Powered Smart Farming  
**Version:** 1.0  
**Date:** September 2026  
**Status:** Active / Production Reference  

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Development Setup (Without Docker)](#3-development-setup-without-docker)
   - 3.1 [Backend (FastAPI)](#31-backend-fastapi)
   - 3.2 [ARQ Worker](#32-arq-worker)
   - 3.3 [Frontend (React)](#33-frontend-react)
4. [Docker Compose — Full Stack (Self-Hosted)](#4-docker-compose--full-stack-self-hosted)
   - 4.1 [Directory Structure](#41-directory-structure)
   - 4.2 [Environment File](#42-environment-file)
   - 4.3 [docker-compose.yml](#43-docker-composeyml)
5. [Dockerfiles](#5-dockerfiles)
   - 5.1 [Backend Dockerfile](#51-backend-dockerfile)
   - 5.2 [Frontend Dockerfile](#52-frontend-dockerfile)
6. [Nginx Configuration](#6-nginx-configuration)
7. [Database Setup & Migrations](#7-database-setup--migrations)
8. [MinIO Provisioning (Self-Hosted)](#8-minio-provisioning-self-hosted)
9. [ML Model Placement](#9-ml-model-placement)
10. [Production Cloud Deployment (Vercel & Google Cloud Run)](#10-production-cloud-deployment-vercel--google-cloud-run)
    - 10.1 [Overview & Serverless Zero-Idle Strategy](#101-overview--serverless-zero-idle-strategy)
    - 10.2 [Google Cloud Storage (GCS) Provisioning & HMAC Keys](#102-google-cloud-storage-gcs-provisioning--hmac-keys)
    - 10.3 [Supabase PostgreSQL Database](#103-supabase-postgresql-database)
    - 10.4 [Upstash Serverless Redis REST Provisioning](#104-upstash-serverless-redis-rest-provisioning)
    - 10.5 [Cloud Run Service #2: inference-service](#105-cloud-run-service-2-inference-service)
    - 10.6 [Cloud Run Service #1: smart-farming-backend](#106-cloud-run-service-1-smart-farming-backend)
    - 10.7 [Vercel Frontend Deployment (smart-farming-dashboard)](#107-vercel-frontend-deployment-smart-farming-dashboard)
    - 10.8 [Automated Continuous Deployment from GitHub](#108-automated-continuous-deployment-from-github)
11. [Production Checklist](#11-production-checklist)
12. [Monitoring & Operations](#12-monitoring--operations)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Architecture Overview

The Smart Farming platform supports two deployment targets depending on your infrastructure requirements:

### Target A: Serverless Cloud Production (Active Live Architecture)
A decoupled, zero-idle-cost cloud architecture deployed on Google Cloud Platform, Vercel, Supabase, and Upstash:

```
                            ┌────────────────────────┐
                            │    Farmer / Client     │
                            └───────────┬────────────┘
                                        │ HTTPS
                            ┌───────────▼────────────┐
                            │   Vercel Edge Network  │
                            │ React + Vite SPA (CDN) │
                            └───────────┬────────────┘
                                        │ HTTPS /api/
                            ┌───────────▼────────────────────────┐
                            │   Cloud Run Service #1: Backend    │
                            │   (FastAPI · 512MiB · Public)      │
                            │   REQUIRE_REDIS=False (Sync Exec)  │
                            └──┬───────────┬───────────┬─────────┤
           GCP OIDC HTTPS Auth │           │ S3 HMAC   │ SSL     │ HTTPS Token
               ┌───────────────┘           │ XML API   │         │
    ┌──────────▼───────────────┐   ┌───────▼──────┐  ┌─▼───────┐ ┌▼──────────────┐
    │ Cloud Run Service #2:    │   │ Google Cloud │  │ Supabase│ │ Upstash       │
    │ inference-service        │   │ Storage (GCS)│  │ Postgres│ │ Redis REST    │
    │ (PyTorch CPU · 2GiB)     │   │ Bucket: data │  │ Pooler  │ │ Serverless    │
    │ Private Ingress          │   └──────────────┘  └─────────┘ └───────────────┘
    └──────────────────────────┘
```

| Component | Cloud Provider | Specifications | Ingress / Access |
|---|---|---|---|
| **Frontend** | Vercel Edge | React 18 + Vite SPA, Tailwind CSS | Public HTTPS (`*.vercel.app`) |
| **API Gateway** | Google Cloud Run (Service #1) | FastAPI, Python 3.11, 1 vCPU, 512 MiB RAM | Public HTTPS (`--allow-unauthenticated`) |
| **ML Inference** | Google Cloud Run (Service #2) | FastAPI + PyTorch CPU, 2 vCPU, 2 GiB RAM | Private HTTPS (`--no-allow-unauthenticated`, GCP OIDC) |
| **Object Storage** | Google Cloud Storage (GCS) | Multi-regional bucket (`smart-farming-data`) | S3 HMAC XML API (`signature_version="s3"`) |
| **Database** | Supabase PostgreSQL | Managed PostgreSQL 15+ with SSL | Encrypted external SSL (`sslmode=require`) |
| **Serverless Cache** | Upstash Redis REST | Serverless Redis (HTTPS Token Auth) | Outbound HTTPS REST (`sf:*` namespace) |
| **External AI** | Hugging Face & OpenWeather | Qwen3-4B Agronomist LLM & Weather API | Outbound HTTPS |

---

### Target B: Self-Hosted Docker Compose (Local Dev / Single VM)
A monolithic container stack with local MinIO object storage and Redis-backed ARQ workers:

```
                         ┌──────────────────────┐
                         │   Browser / Client   │
                         └────────┬─────────────┘
                                  │ HTTPS :443
                         ┌────────▼─────────────┐
                         │   Nginx (Frontend)   │
                         │  React SPA + Proxy   │
                         └────────┬─────────────┘
                    /api/ │                │ /ws/
                 ┌─────────▼────┐  ┌──────▼──────────┐
                 │  FastAPI     │  │  WebSocket      │
                 │  Backend     │  │  (same process) │
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

## 10. Production Cloud Deployment (Vercel & Google Cloud Run)

This section documents the live serverless production architecture deployed on **Google Cloud Platform (Cloud Run & Cloud Storage)**, **Vercel**, and **Supabase Managed PostgreSQL**.

---

### 10.1 Overview & Serverless Zero-Idle Strategy

In production, the platform is decoupled into two independent microservices and two managed cloud services:

```
                            ┌────────────────────────┐
                            │    Farmer / Client     │
                            └───────────┬────────────┘
                                        │ HTTPS
                            ┌───────────▼────────────┐
                            │   Vercel Edge Network  │
                            │ React + Vite SPA (CDN) │
                            └───────────┬────────────┘
                                        │ HTTPS /api/
                            ┌───────────▼────────────────────────┐
                            │   Cloud Run Service #1: Backend    │
                            │   (FastAPI · 512MiB · Public)      │
                            │   REQUIRE_REDIS=False (Sync Exec)  │
                            └──┬───────────┬───────────┬─────────┤
           GCP OIDC HTTPS Auth │           │ S3 HMAC   │ SSL     │ HTTPS Token
               ┌───────────────┘           │ XML API   │         │
    ┌──────────▼───────────────┐   ┌───────▼──────┐  ┌─▼───────┐ ┌▼──────────────┐
    │ Cloud Run Service #2:    │   │ Google Cloud │  │ Supabase│ │ Upstash       │
    │ inference-service        │   │ Storage (GCS)│  │ Postgres│ │ Redis REST    │
    │ (PyTorch CPU · 2GiB)     │   │ Bucket: data │  │ Pooler  │ │ Serverless    │
    │ Private Ingress          │   └──────────────┘  └─────────┘ └───────────────┘
    └──────────────────────────┘
```

#### Why Decoupled Microservices?
- **Memory & Resource Separation:** Heavy PyTorch and YOLO model weights (~1.5 GB in RAM) require a 2 GiB / 2 vCPU container. Serving all standard API requests (auth, weather, farm profiles, admin metrics) from a lightweight 512 MiB container keeps cold starts fast and resource usage minimal.
- **Independent Scaling:** The API gateway can scale rapidly for high HTTP traffic, while the heavier inference service scales strictly according to ML compute demand.

#### The Redis Scale-to-Zero Rationale
- Standard ARQ workers run an infinite polling loop on Redis (`BLPOP`). On Cloud Run, active CPU threads prevent instances from ever scaling down to 0, running continuously 24 hours a day, 7 days a week.
- Continuous 24/7 execution of even 1 instance burns through the entire monthly Google Cloud Run Always Free tier (~180,000 vCPU-seconds) in **under 2.5 days**.
- By configuring **`REQUIRE_REDIS=False`**, the API gateway processes predictions **synchronously**:
  1. The API receives the image upload and writes it to Google Cloud Storage.
  2. It immediately invokes Cloud Run Service #2 (`inference-service`) via HTTPS with GCP OIDC Identity Tokens.
  3. The result is saved to Supabase PostgreSQL and returned in the HTTP response.
- When there are no user requests, **both Cloud Run services scale to 0 instances**, providing true **$0 idle hosting cost**.

---

### 10.2 Google Cloud Storage (GCS) Provisioning & HMAC Keys

Google Cloud Storage stores raw leaf scans, processed bounding boxes, Grad-CAM heatmaps, and TTS audio files.

#### Step 1: Create the GCS Bucket
Using Google Cloud Console or `gcloud`:

```bash
gcloud storage buckets create gs://smart-farming-data \
  --project=<YOUR_GCP_PROJECT_ID> \
  --location=us-central1 \
  --default-storage-class=STANDARD \
  --uniform-bucket-level-access
```

#### Step 2: Generate S3 Interoperability HMAC Keys
1. In Google Cloud Console, navigate to **Cloud Storage** → **Settings** → **Interoperability**.
2. Click **Create a key** for your user account or service account.
3. Save the **Access Key** (`<YOUR_GCS_HMAC_ACCESS_KEY>`) and **Secret** (`<YOUR_GCS_HMAC_SECRET_KEY>`).

#### Step 3: Signature Version Configuration
> [!IMPORTANT]
> Google Cloud Storage's S3 XML API requires **SigV2** (`signature_version="s3"`). AWS SigV4 chunked payload signing fails on GCS with `SignatureDoesNotMatch`.
> The backend `src/app/core/storage.py` automatically applies `signature_version="s3"` whenever `STORAGE_BACKEND=gcs` or `AWS_ENDPOINT_URL` contains `storage.googleapis.com`.

#### Step 4: Verify GCS Connectivity
Run the verification script from the backend directory:

```bash
cd backend
python scripts/verify_gcs_storage.py
```

Expected output:
```
[GCS Test] Uploading test object... SUCCESS
[GCS Test] Generating Presigned URL... SUCCESS
[GCS Test] Verifying HTTP GET from Presigned URL... HTTP 200 OK
[GCS Test] Deleting test object... SUCCESS
All GCS tests passed!
```

---

### 10.3 Supabase PostgreSQL Database

Supabase provides a managed PostgreSQL 15+ database with automated backups, point-in-time recovery, and an integrated connection pooler (Supavisor).

1. **Provision Project:** In Supabase Dashboard, create a new project and select the closest AWS region to your Cloud Run deployment (e.g., `ap-south-1` Mumbai or `us-east-1` N. Virginia).
2. **Retrieve Connection String (Pooler - Session Mode):**
   Go to **Project Settings** → **Database** → **Connection string** → **URI**. Select **Session Mode** (port `5432`):
   ```
   postgresql://postgres.<PROJECT_REF>:<DB_PASSWORD>@aws-0-<REGION>.pooler.supabase.com:5432/postgres?sslmode=require
   ```
   > **Note on Special Characters:** If your database password contains characters such as `@`, `:`, or `/`, ensure it is URL-encoded (e.g. `@` becomes `%40`) in the `DATABASE_URL` DSN string.
   >
   > **Session Pooler Port (`5432`):** Always use port `5432` for backend migrations and SQLAlchemy pooling. The Supabase pooler provides seamless IPv4 and IPv6 compatibility across all cloud container runtimes and local developer machines.

3. **Initialize Schema & Migrations:**
   Run migrations and schema initialization against Supabase:
   ```bash
   cd backend
   DATABASE_URL="postgresql://postgres.<PROJECT_REF>:<DB_PASSWORD>@aws-0-<REGION>.pooler.supabase.com:5432/postgres?sslmode=require" \
   python -m app.core.init_db
   ```
   Or migrate directly from an existing PostgreSQL database:
   ```bash
   python backend/scripts/migrate_render_to_supabase.py \
     --source "postgresql://<SOURCE_USER>:<SOURCE_PASSWORD>@<SOURCE_HOST>/<SOURCE_DB>?sslmode=require" \
     --target "postgresql://postgres.<PROJECT_REF>:<DB_PASSWORD>@aws-0-<REGION>.pooler.supabase.com:5432/postgres?sslmode=require"
   ```

---

### 10.4 Upstash Serverless Redis REST Provisioning

Upstash provides a zero-idle, pay-per-request serverless Redis database accessible directly over HTTPS REST without keeping long-lived TCP connections open.

#### Step 1: Create Database in Upstash Console
1. Navigate to the [Upstash Console](https://console.upstash.com) and sign in.
2. Click **Create Database**.
3. Configure settings:
   - **Name:** `smart-farming-redis`
   - **Type:** Serverless Redis
   - **Region:** Select a region with low latency to your Cloud Run deployment (e.g., `us-central1` or nearest zone).
   - **TLS:** Enabled (default).
4. Click **Create**. The free tier provides 500,000 commands/month and 256 MB storage.

#### Step 2: Retrieve REST API Keys
1. On your database dashboard, scroll to the **REST API** section.
2. Select the **.env** tab to view your credentials:
   ```dotenv
   UPSTASH_REDIS_REST_URL="https://<database-name>.upstash.io"
   UPSTASH_REDIS_REST_TOKEN="<bearer-token>"
   ```

#### Step 3: Verify Connection via CLI / PowerShell
Test your Upstash database directly from your local terminal:

```powershell
$URL = "https://<database-name>.upstash.io"
$TOKEN = "<bearer-token>"

# Test SET
Invoke-RestMethod -Uri "$URL/set/smart_farming_test/connected" -Headers @{ Authorization = "Bearer $TOKEN" } -Method Post

# Test GET
Invoke-RestMethod -Uri "$URL/get/smart_farming_test" -Headers @{ Authorization = "Bearer $TOKEN" }
# Expected result: connected
```

#### Step 4: Verify Python Integration Features
Run the project verification script to validate all 5 platform integrations:
```bash
cd backend
python scripts/verify_upstash_features.py
```
This verifies:
1. REST client connectivity and ping.
2. Phrase-level translation caching (`sf:trans:*`).
3. SHA-256 prediction image deduplication (`sf:dedup:*`).
4. 30-min weather response caching (`sf:weather:*`) and lazy cron locks (`sf:cron:last_weather_eval`).
5. Dynamic ML threshold sync (`sf:config:thresholds`).

---

### 10.5 Cloud Run Service #2: `inference-service`

The inference microservice loads the 7 model checkpoints and runs PyTorch CPU inference on demand.

#### System Dependencies & Dockerfile
The inference service requires Debian OpenCV and X11 libraries:
```dockerfile
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libxcb1 libx11-6 libxext6 libxrender1 curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

COPY . .
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### Deploy Command
Deploy with **private ingress** (`--no-allow-unauthenticated`) so only authorized GCP services can call it:

```bash
gcloud run deploy inference-service \
  --source . \
  --region us-central1 \
  --platform managed \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 3 \
  --timeout 120 \
  --no-allow-unauthenticated
```

The service will output its private URL:
`https://inference-service-<PROJECT_HASH>.<REGION>.run.app`

---

### 10.6 Cloud Run Service #1: `smart-farming-backend`

The public API gateway coordinates authentication, database queries, weather enrichment, LLM recommendations, and inference forwarding.

#### Step 1: Grant IAM Invoker Permissions to Service #1
To allow the backend to invoke the private `inference-service`, grant the Cloud Run Invoker role to its service account:

```bash
# Get Google Cloud Project Number
PROJECT_NUM=$(gcloud projects describe <YOUR_GCP_PROJECT_ID> --format='value(projectNumber)')

# Grant roles/run.invoker to the default compute service account
gcloud run services add-iam-policy-binding inference-service \
  --region=us-central1 \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/run.invoker"
```

#### Step 2: Ensure Model Registry is Packaged
In `backend/Dockerfile`, ensure `model_registry.json` is included:
```dockerfile
COPY model_registry.json .
```
When `MODEL_SERVER_URL` is set, `GET /admin/models/health` reads accuracy metrics and versions from `model_registry.json` without needing heavy `.pth` checkpoint files inside this container.

#### Step 3: Deploy Command
```bash
gcloud run deploy smart-farming-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --allow-unauthenticated \
  --set-env-vars="\
ENVIRONMENT=production,\
DEBUG=False,\
REQUIRE_REDIS=False,\
STORAGE_BACKEND=gcs,\
AWS_ACCESS_KEY_ID=<YOUR_GCS_HMAC_ACCESS_KEY>,\
AWS_SECRET_ACCESS_KEY=<YOUR_GCS_HMAC_SECRET_KEY>,\
AWS_REGION=auto,\
AWS_S3_BUCKET=smart-farming-data,\
AWS_ENDPOINT_URL=https://storage.googleapis.com,\
MODEL_SERVER_URL=https://inference-service-<PROJECT_HASH>.<REGION>.run.app,\
DATABASE_URL=postgresql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>/<DB_NAME>?sslmode=require,\
UPSTASH_REDIS_REST_URL=https://<YOUR_UPSTASH_DB_NAME>.upstash.io,\
UPSTASH_REDIS_REST_TOKEN=<YOUR_UPSTASH_REST_TOKEN>,\
JWT_SECRET_KEY=<YOUR_JWT_SECRET_KEY>,\
HF_TOKEN=<YOUR_HF_TOKEN>,\
OPENWEATHER_API=<YOUR_OPENWEATHER_API_KEY>,\
CORS_ORIGINS=https://smart-farming-dashboard.vercel.app,http://localhost:5173"
```

Verify service health:
```bash
curl https://smart-farming-backend-<PROJECT_HASH>.<REGION>.run.app/health
# {"status":"ok","database":"connected","models":"ok"}
```

---

### 10.7 Vercel Frontend Deployment (`smart-farming-dashboard`)

The React SPA is deployed on Vercel's global Edge Network.

#### Step 1: SPA Rewrites (`frontend/vercel.json`)
To prevent `404 Not Found` errors when refreshing deep URLs (e.g., `/dashboard`, `/predict/123`), create `frontend/vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

#### Step 2: Linux Case-Sensitivity Verification
Vercel builds run on Linux. Verify all TypeScript file imports match the exact file casing on disk (e.g. `import Sidebar from "./Sidebar";` matching `src/components/Sidebar.tsx`).

#### Step 3: Configure Project Settings in Vercel
1. Import repository `manthan2876/Smart-Farming` in Vercel.
2. Configure build settings:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. Configure Environment Variables in Vercel:
   | Variable | Value |
   |---|---|
   | `VITE_API_URL` | `https://smart-farming-backend-<PROJECT_HASH>.<REGION>.run.app` |
   | `VITE_GOOGLE_MAPS_API_KEY` | `<YOUR_GOOGLE_MAPS_API_KEY>` |
   | `VITE_GOOGLE_MAPS_MAP_ID` | `DEMO_MAP_ID` |
4. Click **Deploy**.

---

### 10.8 Automated Continuous Deployment from GitHub

To automatically deploy new code on every `git push origin main`:

#### Setting Up Cloud Run GitHub Integration via Cloud Build:
1. In Google Cloud Console, navigate to **Cloud Run**.
2. Select `smart-farming-backend` and click **Set up continuous deployment** (or **Edit & Deploy New Revision** → Deploy from repository).
3. Connect your GitHub account and select repository `manthan2876/Smart-Farming`.
4. Set branch: `^main$`.
5. Select Build Configuration:
   - **Build Type:** Dockerfile
   - **Source location:** `/backend/Dockerfile`
6. Click **Save**. Google Cloud creates an automated Cloud Build trigger. Every push to `main` now automatically triggers a Docker build and rolls out a new revision with zero downtime.
7. Repeat the same setup for `inference-service` with source location `/inference_service/Dockerfile`.

---

## 11. Production Checklist

Work through this checklist before going live.

### Security

- [ ] **Change `SECRET_KEY` & `JWT_SECRET_KEY`** — Generate random 256-bit hex keys:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] **Set `ENVIRONMENT=production`** and **`DEBUG=False`** in the backend environment.
- [ ] **Set `CORS_ORIGINS`** to your exact frontend domain(s) (e.g. `https://smart-farming-dashboard.vercel.app`).
- [ ] **Secure Ingress on Inference Service** — Ensure `--no-allow-unauthenticated` is set on `inference-service`.
- [ ] **Verify `.gitignore`** — Ensure all `.env`, `.pem`, and credentials files are untracked.

### Database

- [ ] Use **Supabase Managed PostgreSQL** (Session Pooler port `5432`) with SSL (`sslmode=require`).
- [ ] Run **`python -m app.core.init_db`** / **`alembic upgrade head`** before traffic switch.
- [ ] Verify automated PostgreSQL backups in Supabase dashboard.

### Serverless Cache & Execution Mode

- [ ] **Cloud Run Production:** Confirm **`REQUIRE_REDIS=False`** so services scale down to 0 instances when idle.
- [ ] **Upstash Redis REST:** Configure **`UPSTASH_REDIS_REST_URL`** and **`UPSTASH_REDIS_REST_TOKEN`** for serverless caching.
- [ ] Run **`python scripts/verify_upstash_features.py`** to confirm all 5 features pass (translation caching, deduplication, weather caching, cron locks, dynamic threshold sync).
- [ ] **Docker Compose / VM:** Set **`REQUIRE_REDIS=True`** and ensure the `worker` container is healthy.

### Object Storage

- [ ] Google Cloud Storage bucket `smart-farming-data` created in `us-central1`.
- [ ] GCS HMAC keys active with `STORAGE_BACKEND=gcs` and `signature_version="s3"`.
- [ ] Verified upload, read, and signed URL generation via `scripts/verify_gcs_storage.py`.

### External API Keys

- [ ] **`HF_TOKEN`** — Hugging Face token for Qwen3-4B Agronomist LLM recommendations.
- [ ] **`OPENWEATHER_API`** — OpenWeatherMap key for live ambient weather data.
- [ ] **`VITE_GOOGLE_MAPS_API_KEY`** — Google Maps JS API key for interactive farm geo-boundaries.

### Frontend (Vercel)

- [ ] `frontend/vercel.json` SPA rewrite rule present.
- [ ] `VITE_API_URL` points to live Cloud Run backend URL.
- [ ] Production build succeeds without TypeScript errors (`tsc -b && vite build`).

---

## 12. Monitoring & Operations

### 12.1 Viewing Logs

#### Cloud Run Logs (Production)
```bash
# Stream logs from the main backend
gcloud run services logs tail smart-farming-backend --region=us-central1

# Stream logs from the inference microservice
gcloud run services logs tail inference-service --region=us-central1
```

#### Docker Compose Logs (Self-Hosted)
```bash
# All services, follow mode
docker compose logs -f

# Specific service, last 100 lines
docker compose logs --tail=100 backend
docker compose logs --tail=100 worker
docker compose logs --tail=100 frontend
```

---

### 12.2 Updating the Application

#### Google Cloud Run
Pushes to `main` will automatically build and deploy if GitHub continuous deployment is configured (see [Section 10.8](#108-automated-continuous-deployment-from-github)).
To manually trigger a deployment:
```bash
# Deploy Backend
cd backend
gcloud run deploy smart-farming-backend --source . --region us-central1

# Deploy Inference
cd ../inference_service
gcloud run deploy inference-service --source . --region us-central1
```

#### Docker Compose
```bash
git pull origin main
docker compose build
docker compose up -d
docker compose ps
```

---

## 13. Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `SignatureDoesNotMatch` on GCS upload | AWS SigV4 chunking used on GCS XML API | Set `STORAGE_BACKEND=gcs` or configure `signature_version="s3"` in botocore client. |
| `ImportError: libGL.so.1` or `libxcb.so.1` in inference service | Missing Debian system libraries in Docker image | Add `libgl1 libglib2.0-0 libxcb1 libx11-6 libxext6 libxrender1` to `apt-get install` in Dockerfile. |
| Cloud Run container terminated with exit code `137` (OOM) | Memory limit exceeded during PyTorch model loading | Increase memory allocation to at least `2Gi` on `inference-service`. |
| `403 Forbidden` calling `inference-service` from backend | Missing IAM invoker permission | Add `roles/run.invoker` binding for the compute service account on `inference-service`. |
| Vercel returns `404 Not Found` on page refresh | Missing SPA client-side routing rewrites | Add `frontend/vercel.json` with rewrite rule `{"source": "/(.*)", "destination": "/index.html"}`. |
| `Cannot find module './SideBar'` during Vercel build | Case-sensitivity mismatch between Git/Linux and Windows | Fix filename or import casing (e.g., `Sidebar.tsx` vs `SideBar.tsx`). |
| Cloud Run instance never scales to 0 | Persistent Redis polling active | Set `REQUIRE_REDIS=False` to switch to serverless synchronous execution. |
| `relation "X" does not exist` on backend start | Database migrations not applied | Run `alembic upgrade head` pointing to `DATABASE_URL`. |
| CORS error in browser | `CORS_ORIGINS` mismatch | Ensure `CORS_ORIGINS` matches the Vercel domain exactly (e.g. `https://smart-farming-dashboard.vercel.app` with no trailing slash). |
| `HF_TOKEN` error in LLM endpoints | Token missing or invalid | Set a valid `HF_TOKEN` from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens). |
| `UpstashRedisError: Unauthorized` | Invalid `UPSTASH_REDIS_REST_TOKEN` | Copy the bearer token from the Upstash REST API `.env` tab and update Cloud Run env vars. |
| Translations falling back to synchronous / slow UI | Upstash credentials missing or unreachable | Verify `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` are set so pre-cached translations serve in <20ms. |

---

*AI-Powered Smart Farming — Documentation*  
*Last Updated: September 2026*

