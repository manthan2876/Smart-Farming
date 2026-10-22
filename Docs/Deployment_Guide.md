# Smart Farming — Deployment Guide

- **Project:** AI-Powered Smart Farming
- **Version:** 2.2 (Monorepo, Cloud Production Architecture & Vercel Analytics)
- **Date:** 22 October 2026
- **Status:** Active / Operator reference; verify provider settings before production deployment

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
                            │   (Python 3.12 · Gunicorn/Uvicorn) │
                            │   REQUIRE_REDIS=False (Sync Exec)  │
                            └──┬───────────┬───────────┬─────────┤
            AI_SERVICE_URL     │           │ Signed    │ SSL     │ HTTPS REST
            (HTTP REST)        │           │ URLs      │ Port    │ Token Auth
                ┌──────────────┘           │           │ 5432    │
     ┌──────────▼───────────────┐   ┌──────▼───────┐ ┌─▼───────┐ ┌▼──────────────┐
     │ Hugging Face Spaces      │   │ Supabase     │ │ Supabase│ │ Upstash       │
     │ Maharsh8805/smart-farm-ai│   │ Object Store │ │ Postgres│ │ Redis REST    │
     │ Port 7860 · Gradio + API │   │ Bucket: data │ │ Pooler  │ │ Serverless    │
     └──────────────────────────┘   └──────────────┘ └─────────┘ └───────────────┘
```

| Component | Provider / Platform | Specifications | Public URL / Access |
|---|---|---|---|
| **API Gateway & Backend** | **Render** Web Service | Python 3.12, Gunicorn + Uvicorn worker, Render Blueprint (`render.yaml`) | `https://smart-farming-backend.onrender.com` |
| **Unified AI Microservice** | **Hugging Face Spaces** | ZeroGPU / CPU, FastAPI + Gradio 5.16+, Port `7860` | `https://maharsh8805-smart-farming-ai.hf.space` |
| **Web Dashboard** | **Vercel** Edge Network | React 19 + Vite 8 SPA, Tailwind CSS 4 | `https://smart-farming-dashboard.vercel.app` |
| **Mobile Application** | **Flutter** (Android/iOS) | Dart, ChangeNotifier/InheritedNotifier state, SQLite offline queue | Standalone native APK / IPA |
| **Relational Database** | **Supabase** Managed PostgreSQL | PostgreSQL 15+ via Session Pooler (port `5432`, SSL require) | `db.<project-ref>.supabase.co:5432` |
| **Object Storage** | **Supabase** Object Storage | S3-compatible bucket (`smart-farming-data-dev`), 15-min signed URLs | Supabase REST Storage API |
| **Serverless Redis** | **Upstash** Redis REST | Serverless Redis (HTTPS Token Auth, `sf:*` namespace) | `https://<db>.upstash.io` |
| **Scheduled Crons** | **Upstash** QStash | Serverless webhook delivery (`/api/v1/internal-cron`) | QStash Cloud Dispatcher |
| **External Heartbeat** | **cron-jobs.org** | 10-minute automated health pings | Keepalive HTTP GET |

---

### 1.2 Target B: Self-Hosted Docker Compose (Local Dev / Single VM)

A local two-service development stack using the repository's `compose.yaml`:

| Container | Technology | Host Port | Purpose |
|---|---|---|---|
| `backend` | FastAPI + Gunicorn/Uvicorn worker | `8000` | API and SQLite-backed local development |
| `frontend` | Non-root Nginx + built React SPA | `8080` | Static web hosting |

The Compose stack does not provision PostgreSQL, Redis, an ARQ worker, or MinIO. Configure those services separately when validating production-like integrations.

---

## 2. Prerequisites & Development Environment

### Required Tooling

| Tool | Minimum Version | Installation / Notes |
|---|---|---|
| **Python** | 3.12+ | Recommended: `pyenv` or `conda` (Python 3.12 matched in CI & Render) |
| **Node.js** | 20 LTS+ | Recommended: `nvm` (`node -v` $\ge$ 20.0) |
| **Flutter SDK** | 3.24+ | Required only for mobile development (`flutter doctor`) |
| **Git** | 2.40+ | With Git LFS installed (`git lfs install`) |
| **PostgreSQL Client** | 15+ | `psql` for database inspection and migrations |

---

## 3. Local Development Setup (Without Docker)

### 3.1 Backend Service (FastAPI)

1. **Create and activate a virtual environment:**
   ```bash
   cd backend
   python3.12 -m venv venv
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
   python3.12 -m venv venv
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

# Test migration reversibility (Upgrade -> Downgrade -> Upgrade)
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

### 4.2 Migration Lineage
The platform enforces a deterministic, reversible migration chain:
- **`0000_baseline.py`**: Idempotent table creation of all core models (`users`, `farms`, `plots`, `predictions`, `feedback`, `alerts`, etc.) for clean installs and CI.
- **`0001_add_feedback_review_fields.py`**: Adds expert review triage fields to `feedback`.
- **`0002_add_password_reset_tokens.py`**: Creates `password_reset_tokens` table with FK to `users.id`.
- **`0003_supabase_auth_sync.py`**: Installs hardened Supabase Auth trigger (`handle_new_user()` with `SECURITY DEFINER SET search_path = ''`, role forced strictly to `farmer`, immutable role on conflict update, `AFTER INSERT` only).

### 4.3 Production Migrations via GitHub Actions

Migrations to the production Supabase database are automatically executed using the workflow [`.github/workflows/db_migration.yml`](file:///home/manthan/Projects/Smart-Farming/.github/workflows/db_migration.yml).

**Safety & Verification Gates:**
1. **Gated on CI:** Migrations only execute after [`.github/workflows/ci.yml`](file:///home/manthan/Projects/Smart-Farming/.github/workflows/ci.yml) completes successfully via `workflow_run`.
2. **Automated `pg_dump` Backup:** Before applying DDL changes, `db_migration.yml` runs `pg_dump` and uploads a timestamped compressed backup artifact (`prod-db-backup-<sha>`) with 7-day retention for instant rollback capability.
3. **Execution Script:** Uses `backend/scripts/migrate_to_prod.py --schema-only --yes` ensuring zero accidental data loss.

To trigger a migration manually:
1. Navigate to **Actions** in GitHub.
2. Select **Migrate Database to Production**.
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
   CORS_ORIGINS=https://smart-farming-dashboard.vercel.app
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
> Hugging Face Spaces container runtime requires the server to bind strictly to port `7860`. The unified entrypoint `ai_service/app.py` explicitly binds to `0.0.0.0:7860`.

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

2. **Automated QStash Cron Registration CLI:**
   Run the idempotent schedule registration script:
   ```bash
   python backend/scripts/setup_qstash_schedules.py \
     --base-url https://smart-farming-backend-kkty.onrender.com
   ```
   This automatically registers and verifies:
   - **Job 1 (Weather Risks):**
     - **Destination:** `https://smart-farming-backend-kkty.onrender.com/api/v1/internal/cron/weather-risks`
     - **Cron Schedule:** `0 6,12,18 * * *` (3 times daily at 06:00, 12:00, 18:00 UTC)
     - **Schedule ID:** `sf-weather-risks` (idempotent, prevents duplicate job creation)
     - **Verification:** Signed `Upstash-Signature` JWT or `Authorization: Bearer <CRON_SECRET>`
   - **Job 2 (Storage Hygiene & Blob Purge):**
     - **Destination:** `https://smart-farming-backend-kkty.onrender.com/api/v1/internal/cron/purge-blobs`
     - **Cron Schedule:** `0 3 * * 0` (Weekly on Sunday at 03:00 UTC)
     - **Schedule ID:** `sf-purge-blobs`
     - **Cleanup Scope:** 1-hour unreferenced images, 30-day audio files, 7-day unflagged heatmaps

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

4. **Enable Vercel Web Analytics:**
   - In the Vercel Dashboard, select your project and click the **Analytics** tab in the header.
   - Click **Enable**.
   - The React frontend is pre-wired with `@vercel/analytics/react` in `frontend/src/App.tsx` and custom domain event dispatching in `frontend/src/lib/analytics.ts` — zero additional environment variables or external script tags are required.

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

The repository maintains four specialized GitHub Actions workflows in `.github/workflows/`:

```
.github/workflows/
├── ci.yml                     ← Primary CI: PostgreSQL 16 migration cycle, pytest (87+ tests), frontend build, mobile analyzer
├── deploy_ai_service.yml      ← Gated on CI: syncs ai_service to Hugging Face Space & polls /health
├── db_migration.yml           ← Gated on CI: automated pg_dump backup artifact + Alembic migration against Supabase Prod
└── mlops_retrain_check.yml    ← Weekly Monday drift monitor with cold-start warmup, sample gate, and issue dedup
```

### GitHub Repository Secrets & Variables

| Variable / Secret | Type | Purpose |
|---|---|---|
| `HF_TOKEN` | Secret | Hugging Face write token for deploying to Space `Maharsh8805/smart-farming-ai` |
| `PROD_DATABASE_URL` | Secret | Supabase Production Session Pooler DSN (`postgresql://...`) |
| `DEV_DATABASE_URL` | Secret | Supabase Development Session Pooler DSN |
| `ADMIN_JWT` / `ADMIN_API_KEY` | Secret | Optional token for automated MLOps drift metric polling |
| `BACKEND_URL` | Variable | Production backend base URL (`https://smart-farming-backend-kkty.onrender.com`) |

---

## 7. Backend Maintenance & Operational Scripts (`backend/scripts/`)

All maintenance utilities live in `backend/scripts/` and adhere to strict production guards:

| Script | Purpose | Usage |
|---|---|---|
| `_common.py` | Shared connection URL sanitization, environment loader, and prompt confirmation | Internal library used across scripts |
| `check_services.py` | Read-only non-destructive health checks (Database latency, Storage upload/delete, Upstash Redis ping, Supabase Auth API) | `python backend/scripts/check_services.py --env dev` |
| `migrate_to_prod.py` | Production database migration CLI used by `db_migration.yml` | `python backend/scripts/migrate_to_prod.py --schema-only --yes` |
| `setup_qstash_schedules.py` | Idempotent Upstash QStash cron registration (`sf-weather-risks`, `sf-purge-blobs`) | `python backend/scripts/setup_qstash_schedules.py` |
| `migrate_users_to_supabase_auth.py` | One-time backfill of `public.users` into Supabase Auth with pagination (>100 users) and cryptographically random passwords | `python backend/scripts/migrate_users_to_supabase_auth.py --env dev` |
| `sync_user_password.py` | Updates a user's password in both PostgreSQL Argon2 and Supabase Auth (prompts via `getpass`, no shell history leak) | `python backend/scripts/sync_user_password.py --email user@example.com --env dev` |

---

## 7. Local Docker Compose Development Stack

The Compose file provides a local frontend and API with SQLite and a persistent local-media volume. It is not a complete production stack and does not provision PostgreSQL, Redis, an ARQ worker, or the AI service.

1. **Directory Structure:**
   ```
   Smart-Farming/
   ├── compose.yaml
   ├── backend/
   ├── frontend/
   └── ai_service/
   ```

2. **Launch Stack:**
   ```bash
   docker compose up --build
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
- [ ] Vercel Web Analytics enabled under Project Settings → Analytics tab.
- [ ] `cron-jobs.org` pings active and returning `200 OK`.
- [ ] Alembic migrations at `head` (`alembic current`).

---

## 9. Troubleshooting & Diagnostics

### Error: Address already in use (`Errno 98` / Port `7861`) on Hugging Face Spaces
- **Cause:** Gradio defaulted to port `7861` because another process was detected or port wasn't explicitly bounded.
- **Resolution:** In `ai_service/app.py`, enforce `server_port=7860` and `port=7860`.

### Supabase SSL Connection Refused
- **Cause:** Connecting to direct port `6543` without SSL or through an IPv6-only network.
- **Resolution:** Always use the Session Pooler URI on port `5432` with `?sslmode=require`.

### Subroute 404 on AI Microservice
- **Cause:** Legacy tunnel URLs or incorrect subpaths.
- **Resolution:** Verify that `AI_SERVICE_URL` points to `https://maharsh8805-smart-farming-ai.hf.space`. The backend Pydantic model validator will automatically derive `/vision`, `/translation`, `/advisory`, and `/tts`.

---

*AI-Powered Smart Farming — Deployment Guide*  
*Lead Developer & Model Architect: Manthan Kuvadiya*  
*Monorepo Repository: [github.com/manthan2876/Smart-Farming](https://github.com/manthan2876/Smart-Farming)*  
*Hugging Face Space: [Maharsh8805/smart-farming-ai](https://huggingface.co/spaces/Maharsh8805/smart-farming-ai)*  
*Last Updated: 22 October 2026*
