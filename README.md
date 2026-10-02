# 🌾 Smart Farming — AI-Powered Crop Disease Diagnosis & Precision Agronomy

> Enterprise-grade, distributed AI platform for rapid crop disease diagnosis, pest detection, treatment recommendations, multilingual voice advisories, and precision agronomy management.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript)](https://typescriptlang.org)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?logo=flutter)](https://flutter.dev)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.6%20CPU-EE4C2C?logo=pytorch)](https://pytorch.org)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-00FFFF?logo=ultralytics)](https://ultralytics.com)
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run-4285F4?logo=googlecloud)](https://cloud.google.com/run)
[![Supabase](https://img.shields.io/badge/Prod%20DB-Supabase%20PostgreSQL-3ECF8E?logo=supabase)](https://supabase.com)
[![Aiven](https://img.shields.io/badge/Dev%20DB-Aiven%20PostgreSQL-FF3554?logo=aiven)](https://aiven.io)
[![Upstash](https://img.shields.io/badge/Queue%20%26%20Cache-Upstash%20Redis%20%26%20QStash-00E599?logo=redis)](https://upstash.com)
[![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel)](https://vercel.com)

**Project:** AI-Powered Smart Farming  
**Version:** 2.3  
**Date:** 02 October 2026  
**Status:** Active / Production Ready  

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Multi-Environment Database Architecture](#multi-environment-database-architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Diagnostic Pipeline](#diagnostic-pipeline)
- [Quick Start](#quick-start)
  - [1-Click Unified Runner (Recommended)](#1-click-unified-runner-recommended)
  - [Manual Service Startup](#manual-service-startup)
  - [Mobile App (Flutter)](#mobile-app-flutter)
- [Database Management & Migration Tools](#database-management--migration-tools)
- [Background Workers & Asynchronous Tasks (ARQ + QStash)](#background-workers--asynchronous-tasks-arq--qstash)
- [Authentication & Security](#authentication--security)
- [Environment Configuration](#environment-configuration)
- [Mobile Environment Configuration](#mobile-environment-configuration)
- [Key API Endpoints](#key-api-endpoints)
- [User Roles & Workflows](#user-roles--workflows)
- [Production Deployment & CI/CD](#production-deployment--cicd)
- [Running Tests](#running-tests)
- [Documentation Index](#documentation-index)

---

## Overview

**Smart Farming** is a production-grade, distributed computer vision and precision agronomy platform. When a farmer captures or uploads a leaf photograph, the platform executes an end-to-end automated diagnostic and advisory workflow:

1. **Leaf Validation & Preprocessing** — OpenCV evaluates image sharpness (Laplacian variance), illumination, and leaf presence.
2. **Crop Identification** — EfficientNet-B0 classifies the crop species (`Cotton`, `Groundnut`, `Pepper Bell`, `Potato`, `Tomato`).
3. **Decision Routing** — Dynamically dispatches the validated leaf to the crop-specific disease classifier.
4. **Disease Classification** — Dedicated per-crop EfficientNet-B2 models classify diseases with confidence and uncertainty scores.
5. **Severity Estimation** — Adaptive HSV thresholding estimates affected surface area percentage and severity tier (`Healthy`, `Low`, `Medium`, `High`).
6. **Pest Detection** — Ultralytics YOLOv8 identifies agricultural pest infestations.
7. **Visual Evidence (Grad-CAM)** — Generates activation attention heatmaps overlaid on the original leaf for farmer and expert inspection.
8. **Real-Time Weather Context** — Fetches live meteorological conditions (temperature, humidity, rainfall) via OpenWeather API.
9. **LLM Agronomy Advisory** — Google Gemini 2.5 Flash (with Hugging Face Qwen fallback) synthesizes diagnosis, weather, and farm telemetry into organic, chemical, and preventive treatment plans.
10. **Multilingual Voice & Audio** — Localized into English, Hindi, and Gujarati with Google Cloud Text-to-Speech (TTS) audio narration.
11. **Human-in-the-Loop Triage** — Sub-threshold (<70% confidence) diagnoses are routed to an Agronomist Expert Queue for review and MLOps retraining candidate collection.
12. **Asynchronous Processing & Scheduled Crons** — Background tasks run via ARQ workers with Upstash Redis queues and serverless cron schedules orchestrated via Upstash QStash.

---

## System Architecture

The platform operates as a decoupled microservices architecture designed for fault tolerance and zero-downtime scalability:

```
                                  ┌────────────────────────────────────────┐
                                  │           Vercel CDN Edge              │
                                  │      React 18 + Vite SPA Frontend      │
                                  └──────────────────┬─────────────────────┘
                                                     │ HTTPS / REST
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Google Cloud Run: smart-farming-backend                                 │
│                                         (FastAPI API Gateway)                                           │
│                                                                                                         │
│  ├── JWT Authentication (Argon2id + Password Reset Tokens with SMTP)                                    │
│  ├── Weather Service (OpenWeather API)                                                                  │
│  ├── LLM Advisory Engine (Google Gemini 2.5 Flash / Hugging Face Qwen Fallback)                         │
│  ├── Google Cloud Translation (Write-time async translation) & Google Cloud TTS Audio                   │
│  ├── Storage Abstraction (Google Cloud Storage / AWS S3 with 15-minute Presigned URLs)                  │
│  ├── ARQ Job Enqueuer & In-process Serverless Fallback                                                  │
│  └── Notifications & Triage Alerts Engine (Auto-mark read on scan navigation)                           │
└───┬───────────────────────────────┬────────────────────────────────┬───────────────────────────────┬────┘
    │ HTTP / Multipart              │ Database Connection            │ Redis Protocol (TLS)          │ S3 / HMAC API
    ▼                               ▼                                ▼                               ▼
┌─────────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐
│ Google Cloud Run        │   │ Cloud PostgreSQL          │   │ Upstash Cloud Redis       │   │ Google Cloud Storage      │
│ inference-service       │   │                           │   │ & Serverless QStash       │   │ Bucket: smart-farming-data│
│ (Port 8001)             │   │ • Prod: Supabase Cloud    │   │                           │   │                           │
│                         │   │   (Session Pooler: 5432)  │   │ • ARQ Job Queue           │   │ • uploads/ (Raw Leaf)     │
│ • OpenCV Preprocessor   │   │ • Dev: Aiven Cloud        │   │ • Sub-15ms REST Cache     │   │ • processed/ (Grad-CAM)   │
│ • EfficientNet-B0 Crop  │   │   (SSL Mode: Require)     │   │ • Scheduled Cron Webhooks │   │ • audio/ (TTS Narration)  │
│ • EfficientNet-B2 Dis.  │   │                           │   │ • Rate Limiting & Dedup   │   │ • Presigned URL Streaming │
│ • YOLOv8 Pest Detector  │   │ • Predictions & Images    │   │                           │   │                           │
│ • Grad-CAM Visualizer   │   │ • Farms, Plots, Users     │   │ ┌───────────────────────┐ │   │                           │
│ • In-Memory Pre-warming │   │ • Translations & Alerts   │   │ │ ARQ Background Worker │ │   │                           │
└─────────────────────────┘   └───────────────────────────┘   │ │ (Async Translation/ML)│ │   └───────────────────────────┘
                                                              │ └───────────────────────┘ │
                                                              └───────────────────────────┘
```

---

## Multi-Environment Database Architecture

Smart Farming maintains strict separation between Development and Production environments:

| Environment | Provider | Endpoint / Usage | Connection Model |
|---|---|---|---|
| **Development** | **Aiven Cloud PostgreSQL** | `pg-xxx.aivencloud.com:25049/defaultdb` | SSL mode require, lightweight pool (size: 5, overflow: 5) |
| **Local Fallback**| **SQLite** | `sqlite:///./dev_database.db` | Offline local development without cloud network access |
| **Production** | **Supabase Cloud PostgreSQL** | `aws-0-xxx.pooler.supabase.com:5432/postgres` | Session Pooler (port 5432 for transactional DDL migrations) |

### Key Migration Principles:
1. **Alembic Single Source of Truth**: `Base.metadata.create_all` is strictly removed from production paths. All schema DDL must go through versioned Alembic revisions (`alembic upgrade head`).
2. **User Data Protection**: Production user records (`users`, `farms`, `predictions`, `images`, `alerts`, etc.) are never overwritten by automated CI/CD pipelines.
3. **Reference Data Allow-List**: Only safe, static reference tables defined in `REFERENCE_TABLES` can be synced via the optional `--sync-reference` flag.
4. **PostgreSQL Sequence Auto-Sync**: Inserting records with explicit primary keys in PostgreSQL does not advance underlying serial sequences. Our sync tools automatically advance all PostgreSQL sequences to `MAX(id)` to prevent `UniqueViolation` duplicate key collisions.

---

## Tech Stack

| Layer | Technologies & Services | Details |
|---|---|---|
| **Frontend (Web)** | React 18, TypeScript 5.6, Vite 6, Tailwind CSS, Lucide Icons | High-performance dashboard, interactive Grad-CAM viewer, multilingual UI |
| **Mobile App** | Flutter 3.x (Dart), `flutter_map`, `latlong2`, `shared_preferences`, `flutter_tts` | Farmer-only native Android app with center-crosshair GIS boundary drawing, Supabase Remote Config, JWT auth, offline scan queue |
| **Backend Gateway** | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic | RESTful API gateway, RBAC, background job orchestration |
| **Model Microservice** | PyTorch 2.6 (CPU-optimised), timm, Ultralytics YOLOv8, OpenCV | Pure inference server, in-memory model pre-warming, Grad-CAM generation |
| **Job Queue & Scheduling** | ARQ, Upstash Redis (TLS `rediss://`), Upstash QStash | Asynchronous translation workers, pipeline tasks, serverless cron jobs |
| **Database** | Aiven PostgreSQL (Dev) & Supabase PostgreSQL (Prod) | Managed cloud PostgreSQL instances with connection pooling & SSL |
| **Remote Config** | Supabase `public.app_config` table via PostgREST | Farmer app backend URL discovery without app rebuilds; read-only via anon RLS policy |
| **Caching & Dedup** | Upstash Serverless Redis REST | Sub-15ms translation hit caching, SHA-256 image deduplication, rate limiting |
| **Object Storage** | Google Cloud Storage (GCS) / AWS S3 S3-compatible API | Raw leaves, Grad-CAM heatmaps, TTS audio narration with presigned URLs |
| **Generative AI** | Google Gemini 2.5 Flash (`google-genai`), Qwen3-4B-Instruct | Context-aware agronomic advisory generation |
| **Translation & TTS** | Google Cloud Translation API, Google Cloud Text-to-Speech | Dynamic Hindi (`hi`) and Gujarati (`gu`) translations and voice generation |
| **Email Service** | SMTP / TLS (Gmail / SendGrid compatible) | Password reset email tokens and security notifications |
| **Hosting & CI/CD** | Google Cloud Run, Vercel, GitHub Actions | Containerized microservices, edge frontend, gated migration workflows |

---

## Repository Structure

```
Smart-Farming/
├── start_all.bat                           # 1-Click unified launcher for all local services
├── start_all_with_mobile.bat              # Unified launcher including Flutter mobile hot-reload
├── scripts/
│   ├── start_all.ps1                       # Unified non-blocking service orchestrator + ARQ watchdog
│   ├── start_backend.bat                   # Standalone Backend starter
│   ├── start_model_server.bat              # Standalone Model Server starter
│   ├── start_worker.bat                    # Standalone ARQ Worker starter
│   ├── start_frontend.bat                  # Standalone Frontend starter
│   ├── start_mobile.bat                    # Standalone Flutter Web starter
│   └── stop_all.bat                        # Clean shutdown utility
│
├── backend/                                # FastAPI API Gateway & Business Core (Server 1)
│   ├── src/app/
│   │   ├── main.py                         # Application entrypoint & middleware configuration
│   │   ├── worker.py                       # ARQ worker definition (process_prediction, translate_entity)
│   │   ├── pipeline.py                     # Diagnostic pipeline coordinator
│   │   ├── api/
│   │   │   ├── deps.py                     # Auth dependency injection (Argon2id, JWT guards)
│   │   │   └── endpoints/                  # Modular REST routers
│   │   │       ├── auth.py                 # Signup, login, password reset, refresh
│   │   │       ├── predict.py              # Leaf upload, prediction invocation, rescan
│   │   │       ├── farm.py                 # Farm & plot CRUD with GeoJSON polygon validation
│   │   │       ├── expert.py               # Agronomist review queue & audit submissions
│   │   │       ├── alerts.py               # Notifications & read-status management
│   │   │       ├── history.py              # Diagnostic timeline & historical scans
│   │   │       ├── weather.py              # OpenWeather metrics & forecasts
│   │   │       ├── crops.py                # Supported crop species & pathogen catalog
│   │   │       ├── tts.py                  # Audio generation & asset streaming
│   │   │       ├── admin.py                # Admin telemetry & user management
│   │   │       ├── translation.py          # Entity translation overlay
│   │   │       └── mlops.py                # Retraining candidate export & registry
│   │   ├── core/                           # Session pooling, settings, arq pool, storage clients
│   │   ├── models/                         # SQLAlchemy declarative schema models (13 tables)
│   │   ├── schemas/                        # Pydantic validation schemas
│   │   ├── services/                       # Integrations (Gemini, Weather, TTS, Translation)
│   │   └── crud/                           # Database repository queries
│   ├── scripts/                            # Database & migration utilities
│   │   ├── migrate_to_prod.py              # Dev/Prod migration, schema upgrade, reference sync
│   │   ├── sync_prod_to_local.py           # Matches Dev DB to Prod DB (local use only)
│   │   ├── reset_sequences.py              # Resets PostgreSQL auto-increment sequences to MAX(id)
│   │   ├── setup_qstash_schedules.py       # Configures Upstash QStash cron schedules
│   │   ├── verify_qstash_and_events.py     # Validates QStash webhook event delivery
│   │   ├── verify_upstash_features.py      # Tests Upstash Redis connection & caching
│   │   ├── test_smtp.py                    # Validates email sending & SMTP credentials
│   │   └── verify_gcs_storage.py           # Validates GCS HMAC connectivity & upload
│   ├── alembic/                            # Versioned database migrations
│   ├── seed_users.py                       # Seeds initial Admin, Expert, and Farmer accounts
│   ├── requirements.txt                    # Backend dependencies
│   └── Dockerfile                          # Cloud Run container definition for backend
│
├── model_service/                          # Dedicated Vision Inference Microservice (Server 2)
│   ├── src/
│   │   ├── loader.py                       # Model checkpoint loader with defensive fallbacks
│   │   ├── pipeline.py                     # Multi-stage computer vision orchestrator
│   │   └── stages/                         # Discrete vision pipeline stages
│   │       ├── preprocessing.py            # Laplacian blur, brightness, leaf detection
│   │       ├── crop_identifier.py          # EfficientNet-B0 crop classifier
│   │       ├── decision_router.py          # Dynamic routing to crop-specific disease model
│   │       ├── disease_classifier.py       # EfficientNet-B2 disease diagnosis
│   │       ├── severity.py                 # HSV mask affected-area estimation
│   │       └── pest_detector.py            # YOLOv8 pest detection stage
│   ├── models/                             # Pretrained PyTorch & YOLO weight checkpoints
│   ├── config.yaml                         # Confidence thresholds & model architecture specs
│   ├── main.py                             # Inference server with in-memory model pre-warming
│   ├── requirements.txt
│   └── Dockerfile                          # CPU-optimised Cloud Run container definition
│
├── frontend/                               # React 18 + Vite Web Application (Server 3)
│   ├── src/
│   │   ├── pages/                          # Application pages
│   │   │   ├── DashboardPage.tsx           # Telemetry & quick action hub
│   │   │   ├── ScanPage.tsx                # Drag-and-drop diagnostic leaf capture
│   │   │   ├── PredictionResultPage.tsx    # Diagnosis report, Grad-CAM viewer, audio player
│   │   │   ├── AlertsPage.tsx              # Notifications with scan link & auto-read
│   │   │   ├── ExpertQueuePage.tsx         # Agronomist triage desk
│   │   │   ├── ExpertReviewPage.tsx        # Side-by-side diagnostic verification interface
│   │   │   ├── HistoryPage.tsx             # Longitudinal scan records
│   │   │   ├── LoginPage.tsx               # Authentication interface
│   │   │   └── ResetPasswordPage.tsx       # Email token-based password reset interface
│   │   ├── components/                     # Reusable UI component library
│   │   ├── api/                            # Typed HTTP client modules
│   │   ├── context/                        # AuthContext & LanguageContext
│   │   └── i18n/                           # Localised dictionaries (EN, HI, GU)
│   ├── package.json
│   └── vite.config.ts
│
├── mobile/                                 # Flutter Native Mobile App (Farmer-only, Android)
│   ├── lib/
│   │   ├── main.dart                       # App entry — loads RemoteConfig then runApp()
│   │   ├── screens/
│   │   │   ├── auth/
│   │   │   │   ├── auth_wrapper.dart       # Token validation & auto-login logic
│   │   │   │   └── login_screen.dart       # Login & registration (no server URL input)
│   │   │   ├── shell/
│   │   │   │   └── farmer_shell.dart       # 5-tab bottom nav (Today/Farm/Scan/Alerts/History)
│   │   │   ├── map/
│   │   │   │   └── field_boundary_screen.dart  # Center-crosshair GIS boundary drawing + magnetic snapping
│   │   │   ├── farm/
│   │   │   │   ├── farm_screen.dart        # Farm & plot list, launch boundary drawing
│   │   │   │   └── widgets/
│   │   │   │       └── farm_satellite_card.dart  # Satellite map thumbnail of farm boundary
│   │   │   ├── scan/
│   │   │   │   ├── create_prediction_sheet.dart  # Camera/gallery, plot selector, offline queue
│   │   │   │   ├── processing_sheet.dart          # WebSocket live progress + polling fallback
│   │   │   │   └── result_detail_sheet.dart       # Full result: TTS, feedback, translations
│   │   │   ├── today/today_screen.dart     # Dashboard: weather widget, recent alerts
│   │   │   ├── alerts/alerts_screen.dart   # Alert inbox with unread badge
│   │   │   ├── history/history_screen.dart # Paginated scan history
│   │   │   ├── weather/weather_screen.dart # Current conditions with km/h wind & TTS advisory
│   │   │   └── settings/settings_screen.dart  # Language preference, password change
│   │   ├── services/
│   │   │   ├── api_service.dart            # JWT REST client, locked backend URL (no manual override)
│   │   │   ├── remote_config_service.dart  # Supabase app_config fetch + SharedPreferences cache
│   │   │   ├── sync_service.dart           # Offline scan queue with exponential backoff retry
│   │   │   └── tts_service.dart            # Google Cloud TTS with on-device flutter_tts fallback
│   │   ├── models/
│   │   │   └── prediction.dart             # Prediction.fromJson(), localized text & audio helpers
│   │   ├── providers/
│   │   │   └── locale_provider.dart        # EN / HI / GU locale state
│   │   ├── utils/
│   │   │   ├── app_logger.dart             # Tagged mobile logger
│   │   │   └── geo_math.dart               # Geodesic distance, point-on-segment snap, polygon area
│   │   ├── theme/app_theme.dart            # Material 3 design tokens (AppColors, AppTheme)
│   │   └── i18n/app_translations.dart      # EN / HI / GU string keys
│   ├── .env.example                        # Mobile env template (API_BASE_URL, SUPABASE_*)
│   └── pubspec.yaml                        # Flutter dependencies (flutter_map, latlong2, etc.)
│
├── .github/workflows/
│   └── db_migration.yml                    # CI/CD: Automated Alembic prod migrations with approval gate
├── Docs/                                   # Architecture, API, & deployment specifications
└── README.md
```

---

## Diagnostic Pipeline

```
  Step 1: Input Capture
    Farmer uploads a leaf photo via web or mobile (.jpg, .png, .webp).
           │
           ▼
  Step 2: Backend Gateway (Port 8000)
    • Computes SHA-256 hash of image bytes.
    • Checks Upstash Redis REST for deduplication (<15ms).
    • Saves raw leaf to Google Cloud Storage (uploads/{hash}.jpg).
           │
           ▼
  Step 3: Vision Microservice (Port 8001)
    • Preprocessing: OpenCV verifies blur score, brightness, and green leaf presence.
    • Crop ID: EfficientNet-B0 predicts species (e.g., Tomato).
    • Router: Dispatches to the Tomato EfficientNet-B2 disease classifier.
    • Disease Diagnosis: Predicts disease (e.g., Early Blight) + confidence percentage.
    • Severity Mask: HSV thresholding calculates affected surface area (0–100%).
    • Pest Scan: Ultralytics YOLOv8 flags presence of agricultural pests.
    • Grad-CAM: Generates activation heatmap overlay and saves to GCS (processed/{hash}.jpg).
           │
           ▼
  Step 4: Contextual Synthesis & Background Jobs
    • Weather: Fetches live local weather via OpenWeather API.
    • LLM Advisory: Google Gemini 2.5 Flash generates organic, chemical, and preventive advice.
    • ARQ Worker / Async Queue:
      - Asynchronously translates advice into Hindi & Gujarati using Google Translation API.
      - Caches translations in Upstash Redis for sub-15ms instant retrieval.
    • Audio: Generates spoken voice advisory via Google Cloud Text-to-Speech.
           │
           ▼
  Step 5: Delivery & Triage
    • Returns structured JSON to frontend.
    • Sub-70% confidence diagnoses automatically enter the Agronomist Expert Queue.
    • Generates notification alert in the farmer's alerts inbox.
```

---

## Quick Start

### 1-Click Unified Runner (Recommended)

To launch all 4 services concurrently in unified streaming mode with colored logs:

```cmd
.\start_all.bat
```

This starts:
- **Backend API Gateway** $\to$ `http://127.0.0.1:8000` (Swagger docs at `/docs`)
- **Model Inference Server** $\to$ `http://127.0.0.1:8001` (Pre-loads models into RAM)
- **Frontend Dashboard** $\to$ `http://localhost:5173`
- **ARQ Worker** $\to$ Connected to Upstash Redis queue with auto-watchdog

*Press `Ctrl+C` to stop all services cleanly.*

---

### Manual Service Startup

#### 1. Model Inference Microservice (Server 2)
```powershell
cd model_service
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

#### 2. Backend Gateway Server (Server 1)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database and API keys
alembic upgrade head
python seed_users.py  # Seeds default admin, expert, farmer accounts
uvicorn src.app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 3. ARQ Background Worker
```powershell
cd backend
.\.venv\Scripts\activate
arq src.app.worker.WorkerSettings
```

#### 4. Frontend Dashboard (Server 3)
```powershell
cd frontend
npm install
npm run dev
```

---

### Mobile App (Flutter)

The Flutter mobile app targets Android (API 21+) and is exclusively for the **farmer** role. The backend URL is fetched dynamically from Supabase Remote Config — no hardcoded URL, no in-app settings dialog.

#### Prerequisites
- Flutter SDK 3.x installed (`flutter doctor` should show ✅ Android toolchain)
- Android device or emulator connected (`flutter devices`)
- `mobile/.env` configured with your Supabase and backend keys

#### Setup `mobile/.env`
```env
# Compile-time fallback backend URL (used if Supabase remote config unavailable)
API_BASE_URL=https://smart-farming-backend-17713614069.us-central1.run.app

# Supabase Remote Config
SUPABASE_URL=https://<YOUR_PROJECT_REF>.supabase.co
SUPABASE_ANON_KEY=<YOUR_SUPABASE_ANON_KEY>
```

#### Run on Device
```powershell
cd mobile
flutter pub get
flutter run -d <DEVICE_ID> --dart-define-from-file=.env
```

#### Build APK
```powershell
cd mobile
flutter build apk --debug --dart-define-from-file=.env
# Install to connected device:
adb install -r build\app\outputs\flutter-apk\app-debug.apk
```

> **Remote Config:** At startup, the app queries `SUPABASE_URL/rest/v1/app_config?key=eq.api_base_url` using the `SUPABASE_ANON_KEY`. The result is cached in `SharedPreferences` for offline use. URL fallback order: Supabase → cached → `API_BASE_URL` → `http://127.0.0.1:8000`.

---

## Database Management & Migration Tools

The `backend/scripts/` directory provides comprehensive database synchronization and migration tools:

### 1. Production Migration CLI (`migrate_to_prod.py`)
Used for interactive or CI-driven schema migrations between Aiven (Dev) and Supabase (Prod):

```powershell
# Interactive menu:
python backend/scripts/migrate_to_prod.py

# Check database connectivity and compare row counts:
python backend/scripts/migrate_to_prod.py --check

# Apply Alembic schema migrations to Production (Supabase):
python backend/scripts/migrate_to_prod.py --schema-only --yes

# Apply schema migrations to Development (Aiven):
python backend/scripts/migrate_to_prod.py --dev-only --yes

# Upsert safe reference tables from Dev to Prod (Dev wins on conflict):
python backend/scripts/migrate_to_prod.py --sync-reference --yes
```

### 2. Match Dev to Production (`sync_prod_to_local.py`)
A dedicated local tool to mirror Production (Supabase) data down into Development (Aiven or local SQLite):

```powershell
# Sync Prod data into Dev (Aiven Cloud):
python backend/scripts/sync_prod_to_local.py --yes

# Sync Prod data into local SQLite dev_database.db:
python backend/scripts/sync_prod_to_local.py --sqlite --yes
```
*(Blocked from executing inside GitHub Actions CI/CD for safety).*

### 3. PostgreSQL Sequence Reset (`reset_sequences.py`)
Fixes primary key sequence desynchronization on any target PostgreSQL database:

```powershell
python backend/scripts/reset_sequences.py
```

---

## Background Workers & Asynchronous Tasks (ARQ + QStash)

### ARQ Redis Worker (`backend/src/app/worker.py`)
- Offloads heavy or long-running I/O tasks (batch translations, rescan processing, MLOps exports) from the main FastAPI event loop.
- Features resilient connection handling with 15s connection timeouts, 10 retries, and exponential backoff to handle idle cloud socket disconnects over public networks.
- In-process fallback: if Redis is unavailable, background tasks execute in a managed thread pool with Upstash REST string caching.

### Upstash QStash Crons (`backend/scripts/setup_qstash_schedules.py`)
- Serverless recurring schedules trigger periodic webhooks without requiring always-on cron servers:
  - Daily weather alert scans for user farms.
  - Periodic follow-up rescan reminders for active infections.
- Verify active schedules with:
  ```powershell
  python backend/scripts/verify_qstash_and_events.py
  ```

---

## Authentication & Security

- **Password Hashing**: Encrypted using **Argon2id** (Version 19, 64 MB memory cost, 3 iterations, 4 parallel threads) via `pwdlib[argon2]`.
- **JWT Authentication**: HS256 signed access tokens (30 minutes) and refresh tokens (30 days).
- **Password Reset Flow**: Ephemeral, single-use reset tokens with expiry transmitted via SMTP email (TLS).
- **Role-Based Access Control (RBAC)**:
  - `farmer` — Upload scans, view personalized dashboard, listen to audio advisories, view notifications.
  - `expert` — Access Expert Review Queue, verify Grad-CAM heatmaps, override diagnoses, provide agronomist notes.
  - `admin` — System metrics, user role management, MLOps candidate dataset exports.

---

## Environment Configuration

Configure these parameters in `backend/.env` (see [`backend/.env.example`](backend/.env.example)):

| Key | Description | Example / Default |
|---|---|---|
| `ENVIRONMENT` | Deployment environment | `development` / `production` |
| `DEBUG` | Enable debug logs | `True` / `False` |
| `DATABASE_URL` | Dev Database (Aiven PostgreSQL or SQLite) | `postgres://avnadmin:...@pg-xxx.aivencloud.com:25049/defaultdb?sslmode=require` |
| `PROD_DATABASE_URL` | Prod Database (Supabase Session Pooler) | `postgresql://postgres.xxx:...@aws-0-xxx.pooler.supabase.com:5432/postgres?sslmode=require` |
| `JWT_SECRET_KEY` | HMAC SHA-256 signing secret for JWT tokens | 64-character random hex string |
| `REQUIRE_REDIS` | Toggle Redis queue mode | `False` (Upstash Cloud) / `True` (Local Docker) |
| `UPSTASH_REDIS_URL` | Upstash Cloud Redis TLS endpoint for ARQ | `rediss://default:TOKEN@xxx.upstash.io:6379` |
| `UPSTASH_REDIS_REST_URL` | Upstash Serverless REST endpoint | `https://xxx.upstash.io` |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash REST Bearer token | `[YOUR-TOKEN]` |
| `QSTASH_URL` | Upstash QStash API endpoint | `https://qstash-us-east-1.upstash.io/v2` |
| `QSTASH_TOKEN` | Upstash QStash authentication token | `[YOUR-QSTASH-TOKEN]` |
| `MODEL_SERVER_URL` | URL of dedicated Model Inference Microservice | `http://127.0.0.1:8001` or Cloud Run URL |
| `MODEL_SERVER_TIMEOUT` | Read timeout for vision inference (seconds) | `120` |
| `STORAGE_BACKEND` | Active object storage provider | `gcs`, `s3`, or `local` |
| `AWS_ACCESS_KEY_ID` | GCS HMAC Access Key or AWS S3 Key | `GOOG1E...` |
| `AWS_SECRET_ACCESS_KEY` | GCS HMAC Secret Key or AWS S3 Secret | `[YOUR-SECRET-KEY]` |
| `AWS_ENDPOINT_URL` | Custom S3 endpoint (for GCS compatibility) | `https://storage.googleapis.com` |
| `AWS_S3_BUCKET` | Cloud bucket name | `smart-farming-data` |
| `GEMINI_API_KEY` | Google Gemini API key for treatment advisories | `[YOUR-GEMINI-KEY]` |
| `OPENWEATHER_API` | OpenWeather API key for meteorological metrics | `[YOUR-OPENWEATHER-KEY]` |
| `GOOGLE_TTS_API_KEY` | Google Cloud Text-to-Speech API key | `[YOUR-TTS-KEY]` |
| `GOOGLE_TRANSLATION_API_KEY` | Google Cloud Translation API key | `[YOUR-TRANSLATE-KEY]` |
| `SMTP_HOST` | SMTP server for password reset emails | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP username / sender email | `your_email@gmail.com` |
| `SMTP_PASSWORD` | SMTP app password | `[APP-PASSWORD]` |
| `SMTP_TLS` | Enable TLS encryption | `True` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `http://localhost:5173,https://your-domain.vercel.app` |

---

## Mobile Environment Configuration

Configure these in `mobile/.env` (passed via `--dart-define-from-file=.env` at build time):

| Variable | Description | Example |
|---|---|---|
| `API_BASE_URL` | Compile-time fallback backend URL. Used only if Supabase Remote Config and cache are both unavailable. | `https://smart-farming-backend-17713614069.us-central1.run.app` |
| `SUPABASE_URL` | Supabase project URL — used by `RemoteConfigService` to query the `app_config` table. | `https://ntqevjzjhntkilmknrfh.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anonymous (public) key. Required for PostgREST REST queries. RLS restricts to SELECT only. | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |

> **Security note:** No user or developer can view or change the backend URL from inside the app. The `RemoteConfigService` reads the URL from Supabase `app_config` at startup; the result is cached in `SharedPreferences`. All in-app server settings UI has been permanently removed.

---

## Key API Endpoints

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Auth** | `POST` | `/api/v1/auth/register` | Register new user account |
| | `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT access & refresh tokens |
| | `POST` | `/api/v1/auth/forgot-password` | Request password reset email with secure token |
| | `POST` | `/api/v1/auth/reset-password` | Set new password using email token |
| | `POST` | `/api/v1/auth/refresh` | Refresh expired access token |
| **Diagnostics** | `POST` | `/api/v1/predict` | Upload leaf image, invoke vision microservice, synthesize advice |
| | `GET` | `/api/v1/predictions/{id}` | Retrieve diagnosis details, Grad-CAM URLs, auto-mark alert read |
| | `POST` | `/api/v1/predictions/{id}/rescan` | Submit follow-up treatment progress scan |
| **Farm & Plots** | `GET` | `/api/v1/farm` | Get farm details with all plots and multilingual overlays |
| | `PUT` | `/api/v1/farm` | Create/update farm with name, location, GeoJSON boundary |
| | `POST` | `/api/v1/farm/plots` | Create a new plot with optional GeoJSON geometry |
| | `PUT` | `/api/v1/farm/plots/{id}` | Update plot details or boundary |
| | `DELETE` | `/api/v1/farm/plots/{id}` | Remove a plot |
| **Alerts** | `GET` | `/api/v1/alerts` | Get user notifications and triage advisories |
| | `POST` | `/api/v1/alerts/{id}/read` | Mark individual alert as read |
| **Expert Triage** | `GET` | `/api/v1/expert/queue` | List low-confidence diagnoses pending agronomist triage |
| | `GET` | `/api/v1/expert/reviews/{id}` | Get review case with presigned raw leaf and Grad-CAM URLs |
| | `POST` | `/api/v1/expert/reviews/{id}` | Approve, override, or request rescan with agronomist guidance |
| **Telemetry** | `GET` | `/api/v1/weather` | Fetch live meteorological metrics for farm coordinates |
| | `GET` | `/api/v1/crops` | Catalog of supported crop species, pathogens, and symptoms |
| | `GET` | `/api/v1/history` | Longitudinal diagnostic timeline for authenticated user |
| | `GET` | `/api/v1/admin/metrics` | System health, model inference latencies, triage counts |

---

## User Roles & Workflows

### 🧑‍🌾 Farmer
- Submits leaf photographs via mobile camera or desktop file upload.
- Views instant diagnostic breakdowns: disease name, confidence score, severity percentage, and pest warnings.
- Interacts with the Grad-CAM visual evidence slider to inspect model focus areas.
- Listens to audio treatment advisories in their native language (English, Hindi, Gujarati).
- Receives automated alerts when specialist agronomists verify or adjust a treatment plan.
- Navigating to a scan directly from the notifications inbox automatically marks the alert as read.

### 🌿 Expert (Field Agronomist)
- Reviews low-confidence (<70%) or safety-flagged cases in the Expert Review Queue.
- Inspects side-by-side visual evidence: original high-resolution leaf vs. AI Grad-CAM activation heatmap.
- Verifies model accuracy, overrides diagnosis or severity when appropriate, and enters bespoke treatment dosage instructions.
- Flags problematic samples to the dataset retraining candidate pool for continuous model improvement.

### 🛠️ Administrator
- Monitors real-time pipeline telemetry, throughput, and error rates via Cloud Run logs.
- Manages user accounts and role assignments.
- Audits expert review turnaround times and agreement rates.
- Triggers MLOps dataset candidate exports for offline training cycles.

---

## Production Deployment & CI/CD

### Automated Database Migrations (`.github/workflows/db_migration.yml`)
- Triggered on `push` to `main` when changes touch `backend/alembic/**` or `backend/scripts/migrate_to_prod.py`.
- **Gated Execution**: Protected by a GitHub `production` environment approval gate requiring manual reviewer authorization before touching the production database.
- **Strict DDL Path**: Executes `migrate_to_prod.py --schema-only --yes` to apply Alembic migrations against Supabase Session Pooler (port 5432).
- **Opt-In Reference Sync**: Manual `workflow_dispatch` trigger allows optionally syncing safe allow-listed reference tables.

### Hosting Services:
- **API Gateway**: Google Cloud Run (`us-central1`) via Cloud Build.
- **Vision Microservice**: Google Cloud Run (`us-central1`) with CPU optimization.
- **Frontend Dashboard**: Vercel Edge Network.
- **Database**: Supabase Cloud PostgreSQL.
- **Storage**: Google Cloud Storage (`smart-farming-data`).

---

## Running Tests

Execute backend test suites:
```powershell
cd backend
.\.venv\Scripts\activate
python -m pytest tests/ -v
```

Execute frontend build verification:
```powershell
cd frontend
npm run build
```

Execute mobile static analysis and unit tests:
```powershell
cd mobile
flutter analyze
flutter test
```

---

## Documentation Index

Comprehensive documentation is available in the [`Docs/`](Docs/) directory:

- [Architecture & System Design](Docs/Architecture.md) — Technical specification of all layers, contracts, and services.
- [API Specification](Docs/API_Specification.md) — OpenAPI / REST endpoint schemas, request parameters, and response structures.
- [Deployment Guide](Docs/Deployment_Guide.md) — Cloud Run, Vercel, Supabase, and Upstash deployment runbooks.
- [Configuration Reference](Docs/Config_Reference.md) — Complete environment variable and `config.yaml` dictionary, including mobile Flutter variables.
- [Authentication & Roles](Docs/Auth_Roles.md) — RBAC matrix, token lifecycle, and session security models.
- [Model Cards](Docs/Model_Cards.md) — Model metrics, architecture benchmarks, datasets, and limitations.
- [MLOps & Retraining Loop](Docs/MLOps_Retraining.md) — Feedback ingestion, dataset candidate curation, and model promotion.
- [UI / UX Design System](Docs/UI_UX_Spec.md) — Design tokens, component states, mobile boundary drawing UI, and accessibility standards.
- [Functionality Status](Docs/functionality-status.md) — Implementation status, gap analysis, and improvement roadmap.

---

*AI-Powered Smart Farming Platform*  
*Last Updated: 02 October 2026*
