# Smart Farming — Deployment Guide

**Project:** AI-Powered Smart Farming  
**Version:** 2.1 (Monorepo & Cloud Production Architecture)  
**Date:** 19 October 2026  
**Status:** Active / Production Reference  

---

## Table of Contents

1. [Architecture & Deployment Targets](#1-architecture--deployment-targets)
   - 1.1 [Target A: Serverless Cloud Production (Active Live Architecture)](#11-target-a-serverless-cloud-production-active-live-architecture)
   - 1.2 [Target B: Self-Hosted Docker Compose (Local Dev / Single VM)](#12-target-b-self-hosted-docker-compose-local-dev--single-vm)
2. [Prerequisites & Development Environment](#2-prerequisites--development-environment)
3. [Local Development Setup (Without Docker)](#3-local-development-setup-without-docker)
   - 3.1 [Backend Service (FastAPI)](#31-backend-service-fastapi)
   - 3.2 [AI Microservice (Local PyTorch / Gradio)](#32-ai-microservice-local-pytorch--gradio)
   - 3.3 [Frontend Dashboard (React + Vite)](#33-frontend-dashboard-react--vite)
   - 3.4 [Mobile Client (Flutter)](#34-mobile-client-flutter)
4. [Database Provisioning & Alembic Migrations](#4-database-provisioning--alembic-migrations)
5. [Production Cloud Deployment Step-by-Step](#5-production-cloud-deployment-step-by-step)
   - 5.1 [Backend Web Service on Render (`render.yaml`)](#51-backend-web-service-on-render-renderyaml)
   - 5.2 [Unified AI Microservice on Hugging Face Spaces](#52-unified-ai-microservice-on-hugging-face-spaces)
   - 5.3 [Supabase Object Storage & PostgreSQL Setup](#53-supabase-object-storage--postgresql-setup)
   - 5.4 [Upstash Serverless Redis REST & QStash Configuration](#54-upstash-serverless-redis-rest--qstash-configuration)
   - 5.5 [Vercel Frontend Deployment (`frontend/`)](#55-vercel-frontend-deployment-frontend)
   - 5.6 [Automated External Keepalive via `cron-jobs.org`](#56-automated-external-keepalive-via-cron-jobsorg)
6. [CI/CD Automation (GitHub Actions)](#6-cicd-automation-github-actions)
7. [Self-Hosted Docker Compose Stack](#7-self-hosted-docker-compose-stack)
8. [Production Operational Checklist](#8-production-operational-checklist)
9. [Troubleshooting & Diagnostics](#9-troubleshooting--diagnostics)

---

## 1. Architecture & Deployment Targets

The Smart Farming platform supports two primary deployment topologies:

### 1.1 Target A: Serverless Cloud Production (Active Live Architecture)

A modern, highly decoupled, and cost-effective multi-cloud architecture:

```
                            ┌────────────────────────┐
                            │    Farmer / Client     │
                            └───────────┬────────────┘
                                        │ HTTPS
                     ┌──────────────────┴──────────────────┐
                     │                                     │
          ┌──────────▼────────────┐             ┌──────────▼────────────┐
          │   Vercel Edge Network │             │  Flutter Mobile App   │
          │ React + Vite SPA (CDN)│             │ (Android / iOS Build) │
          └──────────┬────────────┘             └──────────┬────────────┘
                     │                                     │
                     └──────────────────┬──────────────────┘
                                        │ HTTPS REST / WebSocket
                            ┌───────────▼────────────────────────┐
                            │   Render Web Service (Backend)     │
                            │   (Python 3.11 · render.yaml)      │
                            │   REQUIRE_REDIS=False (Sync Exec)  │
                            └──┬───────────┬───────────┬─────────┤
            AI_SERVICE_URL     │           │ Signed    │ SSL     │ HTTPS REST
            (HTTP REST)        │           │ URLs      │ Port    │ Token Auth
                ┌──────────────┘           │           │ 5432    │
     ┌──────────▼───────────────┐   ┌──────▼───────┐ ┌─▼───────┐ ┌▼──────────────┐
     │ Hugging Face Spaces      │   │ Supabase     │ │ Supabase│ │ Upstash       │
     │ Maharsh8805/smart-farming│   │ Object Store │ │ Postgres│ │ Redis REST    │
     │ Port 7860 · Gradio + API │   │ Bucket: data │ │ Pooler  │ │ Serverless    │
     └──────────────────────────┘   └──────────────┘ └─────────┘ └───────────────┘
```

| Component | Provider / Platform | Specifications | Public URL / Access |
|---|---|---|---|
| **API Gateway & Backend** | **Render** Web Service | Python 3.11, Uvicorn, Render Blueprint ([`render.yaml`](file:///home/manthan/Projects/Smart-Farming/render.yaml)) | `https://smart-farming-backend.onrender.com` |
| **Unified AI Microservice** | **Hugging Face Spaces** | ZeroGPU / CPU, FastAPI + Gradio 5.16+, Port `7860` | `https://maharsh8805-smart-farming-ai.hf.space` |
| **Web Dashboard** | **Vercel** Edge Network | React 18 + Vite SPA, Tailwind CSS | `https://smart-farming-dashboard.vercel.app` |
| **Mobile Application** | **Flutter** (Android/iOS) | Dart, BLoC, SQLite offline cache | Standalone native APK / IPA |
| **Relational Database** | **Supabase** Managed PostgreSQL | PostgreSQL 15+ via Session Pooler (port `5432`, SSL require) | `db.<project-ref>.supabase.co:5432` |
| **Object Storage** | **Supabase** Object Storage | S3-compatible bucket (`smart-farming-data-dev`), 15-min signed URLs | Supabase REST Storage API |
| **Serverless Redis** | **Upstash** Redis REST | Serverless Redis (HTTPS Token Auth, `sf:*` namespace) | `https://<db>.upstash.io` |
| **Scheduled Crons** | **Upstash** QStash | Serverless webhook delivery (`/api/v1/internal-cron`) | QStash Cloud Dispatcher |
| **External Heartbeat** | **cron-jobs.org** | 10-minute automated health pings | Keepalive HTTP GET |

---

### 1.2 Target B: Self-Hosted Docker Compose (Local Dev / Single VM)

A consolidated single-server deployment using Docker Compose:

| Container | Technology | Host Port | Purpose |
|---|---|---|---|
| `backend` | FastAPI + Uvicorn | `8000` | API Gateway & Sync Pipeline |
| `worker` | Python ARQ Worker | — | Async queue processor (when `REQUIRE_REDIS=True`) |
| `frontend`| Nginx + Built React SPA | `80`, `443` | Reverse proxy and static web hosting |
| `postgres`| PostgreSQL 15 Alpine | `5432` | Local relational database |
| `redis` | Redis 7 Alpine | `6379` | Local job queue and pub/sub broker |
| `minio` | MinIO S3-Compatible Storage | `9000`, `9001` | Local object storage server |

---

## 2. Prerequisites & Development Environment

### Required Tooling

| Tool | Minimum Version | Installation / Notes |
|---|---|---|
| **Python** | 3.11+ | Recommended: `pyenv` or `conda` |
| **Node.js** | 18 LTS+ | Recommended: `nvm` (`node -v` $\ge$ 18.0) |
| **Flutter SDK** | 3.19+ | Required only for mobile development (`flutter doctor`) |
| **Git** | 2.40+ | With Git LFS installed (`git lfs install`) |
| **PostgreSQL Client** | 15+ | `psql` for database inspection and migrations |

---

## 3. Local Development Setup (Without Docker)

### 3.1 Backend Service (FastAPI)

1. **Create and activate a virtual environment:**
   ```bash
   cd backend
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Configure local `.env`:**
   ```bash
   cp .env.example .env
   ```
   Key local development settings:
   ```dotenv
   ENVIRONMENT=development
   DEBUG=True
   DATABASE_URL=sqlite:///./dev_database.db
   STORAGE_BACKEND=local
   REQUIRE_REDIS=False
   AI_SERVICE_URL=https://maharsh8805-smart-farming-ai.hf.space
   ```

4. **Initialize database schema:**
   ```bash
   python -m app.core.init_db
   ```

5. **Start backend development server:**
   ```bash
   uvicorn src.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   Interactive Swagger docs will be available at: `http://127.0.0.1:8000/docs`

---

### 3.2 AI Microservice (Local PyTorch / Gradio)

To run the AI microservice locally instead of connecting to Hugging Face Spaces:

1. **Set up virtual environment:**
   ```bash
   cd ai_service
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the dual Gradio + FastAPI service:**
   ```bash
   python app.py
   ```
   The interactive Gradio UI will bind to `http://localhost:7860`.

---

### 3.3 Frontend Dashboard (React + Vite)

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   Ensure:
   ```dotenv
   VITE_API_URL=http://localhost:8000
   ```

3. **Start Vite development server:**
   ```bash
   npm run dev
   ```
   Web interface available at: `http://localhost:5173`

---

### 3.4 Mobile Client (Flutter)

1. **Verify Flutter toolchain:**
   ```bash
   cd mobile
   flutter doctor
   ```

2. **Fetch packages:**
   ```bash
   flutter pub get
   ```

3. **Run on connected emulator or device:**
   ```bash
   flutter run --dart-define-from-file=.env
   ```

---

## 4. Database Provisioning & Alembic Migrations

The platform uses versioned Alembic migrations to ensure schema consistency across environments.

### 4.1 Running Migrations Locally

```bash
cd backend
# Run all pending migrations
alembic upgrade head

# Inspect current revision
alembic current

# Create a new migration after modifying SQLAlchemy models
alembic revision --autogenerate -m "describe_changes"
```

### 4.2 Production Migrations via GitHub Actions

Migrations to the production Supabase database are automatically executed using the workflow [`.github/workflows/db_migration.yml`](file:///home/manthan/Projects/Smart-Farming/.github/workflows/db_migration.yml).

To trigger a migration manually:
1. Navigate to **Actions** in GitHub.
2. Select **Run Database Migrations**.
3. Click **Run workflow** against the `main` branch.

---

## 5. Production Cloud Deployment Step-by-Step

### 5.1 Backend Web Service on Render (`render.yaml`)

The backend is configured as a Render Blueprint service.

1. **Connect Repository to Render:**
   - Sign in to the [Render Dashboard](https://dashboard.render.com).
   - Select **Blueprints** $\to$ **New Blueprint Instance**.
   - Connect the `Smart-Farming` repository. Render automatically reads [`render.yaml`](file:///home/manthan/Projects/Smart-Farming/render.yaml):
     ```yaml
     services:
       - type: web
         name: smart-farming-backend
         runtime: python
         rootDir: backend
         plan: free
         buildCommand: pip install -r requirements.txt
         startCommand: uvicorn src.app.main:app --host 0.0.0.0 --port $PORT
         healthCheckPath: /health
         buildFilter:
           paths:
             - backend/**
     ```

2. **Configure Environment Variables in Render Dashboard:**
   Add the following secrets under **Environment**:
   ```dotenv
   ENVIRONMENT=production
   DEBUG=False
   REQUIRE_REDIS=False
   STORAGE_BACKEND=supabase
   AI_SERVICE_URL=https://maharsh8805-smart-farming-ai.hf.space
   DATABASE_URL=postgresql://postgres.<PROJECT_REF>:<PASSWORD>@aws-0-<REGION>.pooler.supabase.com:5432/postgres?sslmode=require
   SUPABASE_URL=https://<PROJECT_REF>.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=<SERVICE_ROLE_SECRET_KEY>
   SUPABASE_BUCKET=smart-farming-data-dev
   UPSTASH_REDIS_REST_URL=https://<DB>.upstash.io
   UPSTASH_REDIS_REST_TOKEN=<UPSTASH_REST_BEARER_TOKEN>
   JWT_SECRET_KEY=<SECURE_RANDOM_SECRET>
   OPENWEATHER_API=<OPENWEATHERMAP_API_KEY>
   GROQ_API_KEY=<GROQ_API_KEY>
   CORS_ORIGINS=https://smart-farming-dashboard.vercel.app,http://localhost:5173
   ```

---

### 5.2 Unified AI Microservice on Hugging Face Spaces

The AI microservice is deployed as a Docker / Python Space on Hugging Face (`Maharsh8805/smart-farming-ai`).

#### Automated Deployment via GitHub Actions
Whenever code inside `ai_service/**` is pushed to `main`, [`.github/workflows/deploy_ai_service.yml`](file:///home/manthan/Projects/Smart-Farming/.github/workflows/deploy_ai_service.yml) executes:
1. Clones the Hugging Face Space repository.
2. Synchronizes files from `ai_service/`.
3. Verifies port binding configuration (`7860`).
4. Configures Git LFS for large `.pth` and `.pt` model weights.
5. Pushes changes directly to Hugging Face, triggering an automatic rebuild.

#### Manual Deployment via Script
You can also trigger deployment locally:
```bash
cd ai_service
export HF_TOKEN="hf_your_personal_access_token"
bash deploy.sh
```

> [!IMPORTANT]
> Hugging Face Spaces container runtime requires the server to bind strictly to port `7860`. Both `ai_service/app.py` and `ai_service/main.py` explicitly bind to `0.0.0.0:7860`.

---

### 5.3 Supabase Object Storage & PostgreSQL Setup

1. **Create Supabase Project:**
   - Create a project on [Supabase](https://supabase.com).
   - Select your preferred AWS region (e.g., `ap-south-1` Mumbai or `us-east-1`).

2. **Storage Bucket Provisioning:**
   - Go to **Storage** $\to$ **New Bucket**.
   - **Bucket Name:** `smart-farming-data-dev` (or production bucket name).
   - **Public Bucket:** Leave *unchecked* (private). Media access is protected via 15-minute time-bounded signed URLs generated by `SupabaseStorageBackend`.
   - **Allowed MIME types:** `image/jpeg, image/png, image/webp, audio/mpeg, audio/wav`.

3. **Database Connection (Session Pooler):**
   - In Supabase, navigate to **Project Settings** $\to$ **Database** $\to$ **Connection string**.
   - Copy the URI under **Session Pooler** (Port `5432`):
     ```
     postgresql://postgres.<REF>:<PASSWORD>@aws-0-<REGION>.pooler.supabase.com:5432/postgres?sslmode=require
     ```

---

### 5.4 Upstash Serverless Redis REST & QStash Configuration

1. **Serverless Redis:**
   - Create a database in [Upstash Console](https://console.upstash.com) (e.g., `smart-farming-redis`).
   - Copy `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` into your Render backend environment variables.

2. **QStash Scheduled Webhook (Weather Risk):**
   - Create a scheduled job in Upstash QStash:
     - **Destination:** `https://smart-farming-backend.onrender.com/api/v1/internal-cron/weather-risk`
     - **Cron Schedule:** `*/30 * * * *` (Every 30 minutes)
     - **Header:** `x-cron-secret: <YOUR_CRON_SECRET>`

---

### 5.5 Vercel Frontend Deployment (`frontend/`)

1. **Import Repository in Vercel:**
   - Sign in to [Vercel](https://vercel.com) and import `Smart-Farming`.
   - **Root Directory:** Select `frontend`.
   - **Framework Preset:** Vite.

2. **Configure Environment Variables:**
   - `VITE_API_URL` = `https://smart-farming-backend.onrender.com`
   - `VITE_GOOGLE_MAPS_API_KEY` = `<YOUR_GOOGLE_MAPS_API_KEY>`

3. **SPA Routing Configuration (`frontend/vercel.json`):**
   Ensures deep links (e.g., `/scan`, `/history`, `/admin`) resolve to `index.html`:
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

---

### 5.6 Automated External Keepalive via `cron-jobs.org`

To prevent free-tier containers on Render and Hugging Face Spaces from going to sleep during business hours:

1. Create a free account at [cron-jobs.org](https://cron-jobs.org).
2. Configure **Cronjob #1 (Backend Keepalive):**
   - **URL:** `https://smart-farming-backend.onrender.com/health`
   - **Interval:** Every 10 minutes
   - **Method:** `GET`
3. Configure **Cronjob #2 (AI Microservice Keepalive):**
   - **URL:** `https://maharsh8805-smart-farming-ai.hf.space/`
   - **Interval:** Every 10 minutes
   - **Method:** `GET`

This zero-cost solution guarantees near-zero cold starts for agricultural users without consuming compute credits.

---

## 6. CI/CD Automation (GitHub Actions)

The repository maintains two specialized GitHub Actions workflows in `.github/workflows/`:

```
.github/workflows/
├── deploy_ai_service.yml    ← Automatically updates Hugging Face Space on ai_service/** commits
└── db_migration.yml         ← Executes Alembic database migrations against Supabase
```

### GitHub Repository Secrets Required

| Secret Name | Purpose |
|---|---|
| `HF_TOKEN` | Hugging Face API token with write access to `Maharsh8805/smart-farming-ai` |
| `DATABASE_URL` | Supabase Session Pooler DSN used by Alembic in `db_migration.yml` |

---

## 7. Self-Hosted Docker Compose Stack

For private on-premise deployments or air-gapped field servers:

1. **Directory Structure:**
   ```
   Smart-Farming/
   ├── docker-compose.yml
   ├── backend/
   ├── frontend/
   └── ai_service/
   ```

2. **Launch Stack:**
   ```bash
   docker compose up -d --build
   ```

3. **Verify running containers:**
   ```bash
   docker compose ps
   ```

---

## 8. Production Operational Checklist

- [ ] `DEBUG=False` set in backend environment variables.
- [ ] Strong, random `SECRET_KEY` and `JWT_SECRET_KEY` configured.
- [ ] Supabase database password contains URL-encoded special characters.
- [ ] Supabase Object Storage bucket `smart-farming-data-dev` created and private.
- [ ] Hugging Face Space binds strictly to port `7860`.
- [ ] Render build filter correctly monitors `backend/**`.
- [ ] `CORS_ORIGINS` includes the production Vercel frontend URL.
- [ ] `cron-jobs.org` pings active and returning `200 OK`.
- [ ] Alembic migrations at `head` (`alembic current`).

---

## 9. Troubleshooting & Diagnostics

### Error: Address already in use (`Errno 98` / Port `7861`) on Hugging Face Spaces
- **Cause:** Gradio defaulted to port `7861` because another process was detected or port wasn't explicitly bounded.
- **Resolution:** In both `ai_service/app.py` and `ai_service/main.py`, enforce `server_port=7860` and `port=7860`.

### Supabase SSL Connection Refused
- **Cause:** Connecting to direct port `6543` without SSL or through an IPv6-only network.
- **Resolution:** Always use the Session Pooler URI on port `5432` with `?sslmode=require`.

### Subroute 404 on AI Microservice
- **Cause:** Legacy tunnel URLs or incorrect subpaths.
- **Resolution:** Verify that `AI_SERVICE_URL` points to `https://maharsh8805-smart-farming-ai.hf.space`. The backend Pydantic model validator will automatically derive `/vision`, `/translation`, `/advisory`, and `/tts`.

---

*AI-Powered Smart Farming — Deployment Guide*  
*Last Updated: 19 October 2026*  
*Maintained by the Smart Farming Engineering Team*
