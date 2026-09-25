# 🌾 Smart Farming — AI-Powered Crop Disease Diagnosis & Precision Agronomy

> Enterprise-grade, distributed AI platform for rapid crop disease diagnosis, pest detection, treatment recommendations, and agronomic field management.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript)](https://typescriptlang.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.6%20CPU-EE4C2C?logo=pytorch)](https://pytorch.org)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-00FFFF?logo=ultralytics)](https://ultralytics.com)
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run-4285F4?logo=googlecloud)](https://cloud.google.com/run)
[![Supabase](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E?logo=supabase)](https://supabase.com)
[![Upstash](https://img.shields.io/badge/Cache-Upstash%20Redis%20REST-00E599?logo=redis)](https://upstash.com)
[![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel)](https://vercel.com)

**Project:** AI-Powered Smart Farming  
**Version:** 2.0  
**Date:** September 2026  
**Status:** Active / Production Reference  

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Diagnostic Pipeline](#diagnostic-pipeline)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Model Inference Microservice (Server 2)](#1-model-inference-microservice-server-2)
  - [2. Backend Gateway Server (Server 1)](#2-backend-gateway-server-server-1)
  - [3. Frontend Dashboard](#3-frontend-dashboard)
- [Environment Configuration](#environment-configuration)
- [Key API Endpoints](#key-api-endpoints)
- [User Roles & Workflows](#user-roles--workflows)
- [Production Deployment](#production-deployment)
- [Running Tests](#running-tests)
- [Documentation Index](#documentation-index)

---

## Overview

**Smart Farming** is a production-ready, distributed computer vision and agronomy advisory system. A farmer captures or uploads a leaf photograph, and the system executes an automated diagnostic and advisory workflow:

1. **Leaf Validation & Preprocessing** — OpenCV evaluates image sharpness (Laplacian variance), illumination, and leaf presence.
2. **Crop Identification** — EfficientNet-B0 classifies the crop species (`Cotton`, `Groundnut`, `Pepper Bell`, `Potato`, `Tomato`).
3. **Decision Routing** — Dynamically dispatches the validated leaf to the crop-specific disease classifier.
4. **Disease Classification** — Dedicated per-crop EfficientNet-B2 models classify diseases with confidence and uncertainty scores.
5. **Severity Estimation** — Adaptive HSV thresholding estimates affected surface area percentage and severity tier (`Healthy`, `Low`, `Medium`, `High`).
6. **Pest Detection** — Ultralytics YOLOv8 classifies pest species presence.
7. **Visual Evidence** — Generates Grad-CAM visual attention heatmaps overlaid on the original leaf for farmer and expert inspection.
8. **Real-Time Weather Context** — Fetches live meteorological conditions (temperature, humidity, rainfall) via OpenWeather API.
9. **LLM Agronomy Advisory** — Google Gemini 2.5 Flash synthesizes diagnosis, weather, and farm telemetry into actionable chemical, organic, and preventive treatment plans.
10. **Multilingual Delivery & Audio** — Localized into English, Hindi, and Gujarati with Google Cloud Text-to-Speech (TTS) audio narration.
11. **Human-in-the-Loop Triage** — Sub-threshold (<70% confidence) or conflicting diagnoses are routed to an Agronomist Expert Queue for review and MLOps retraining candidate collection.

---

## System Architecture

The platform operates as a decoupled microservices architecture designed for high scalability and zero-downtime deployments:

```
                                  ┌────────────────────────────────────────┐
                                  │           Vercel CDN Edge              │
                                  │      React 18 + Vite SPA Frontend      │
                                  └──────────────────┬─────────────────────┘
                                                     │ HTTPS / REST / WS
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Google Cloud Run: smart-farming-backend                                │
│                                         (FastAPI API Gateway)                                           │
│                                                                                                         │
│  ├── JWT Authentication & RBAC (Farmer, Expert, Admin)                                                  │
│  ├── Weather Service (OpenWeather API)                                                                  │
│  ├── LLM Advisory Engine (Google Gemini 2.5 Flash / Hugging Face Qwen Fallback)                          │
│  ├── Google Cloud Translation (Write-time async translation) & Google Cloud TTS Audio                   │
│  ├── Storage Abstraction (Google Cloud Storage / AWS S3 with 15-minute Presigned URLs)                  │
│  └── Notifications & Triage Alerts Engine (Auto-mark read on scan navigation)                           │
└───┬───────────────────────────────┬────────────────────────────────┬───────────────────────────────┬────┘
    │ HTTP / Multipart              │ Database Connection            │ HTTPS REST API                │ Storage API
    ▼                               ▼                                ▼                               ▼
┌─────────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐
│ Google Cloud Run        │   │ Supabase PostgreSQL       │   │ Upstash Redis REST        │   │ Google Cloud Storage      │
│ inference-service       │   │ (Connection Pooling)      │   │ (Sub-20ms Latency)        │   │ Bucket: smart-farming-data│
│                         │   │                           │   │                           │   │                           │
│ • OpenCV Preprocessor   │   │ • Users & Farms           │   │ • Image Deduplication     │   │ • uploads/ (Raw Leaf)     │
│ • EfficientNet-B0 Crop  │   │ • Predictions & Images    │   │ • Rate Limiting           │   │ • processed/ (Grad-CAM)   │
│ • EfficientNet-B2 Dis.  │   │ • Expert Reviews          │   │ • Write-time Translations │   │ • audio/ (TTS Narration)  │
│ • YOLOv8 Pest Detector  │   │ • Alerts & Notifications  │   │ • Pipeline Cache (24h)    │   │ • Presigned URL Redirects │
│ • Grad-CAM Visualizer   │   │ • MLOps Retraining Pool   │   │                           │   │                           │
└─────────────────────────┘   └───────────────────────────┘   └───────────────────────────┘   └───────────────────────────┘
```

---

## Tech Stack

| Layer | Technologies & Services | Details |
|---|---|---|
| **Frontend** | React 18, TypeScript 5, Vite 6, Tailwind CSS, Lucide Icons | Responsive dashboard, Grad-CAM slider, multilingual i18n |
| **Backend Gateway** | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0 | REST API gateway, authentication, business orchestration |
| **Model Microservice** | PyTorch 2.6 (CPU-optimised), timm, Ultralytics YOLOv8, OpenCV | Pure inference server, in-memory model weights, Grad-CAM |
| **Database** | Supabase PostgreSQL 15 | Managed relational database with SSL & connection pooling |
| **Caching & Dedup** | Upstash Redis (Serverless REST API) | Sub-20ms dedup caching, write-time translation cache |
| **Object Storage** | Google Cloud Storage (GCS) / AWS S3 S3-compatible API | Raw leaves, Grad-CAM heatmaps, TTS audio blobs |
| **Generative AI** | Google Gemini 2.5 Flash (`google-genai`), Qwen3-4B-Instruct | Context-aware agronomic advisory generation |
| **Translation & TTS** | Google Cloud Translation API, Google Cloud Text-to-Speech | Dynamic Hindi & Gujarati translation, voice generation |
| **Hosting & Cloud** | Google Cloud Run, Vercel | Fully managed containerized microservices & edge frontend |

---

## Repository Structure

```
Smart-Farming/
├── backend/                                # FastAPI API Gateway (Server 1)
│   ├── src/app/
│   │   ├── main.py                         # Application entrypoint & static storage fallback
│   │   ├── pipeline.py                     # Pipeline orchestrator & remote vision dispatcher
│   │   ├── context.py                      # Shared pipeline context dictionary factory
│   │   ├── api/
│   │   │   ├── deps.py                     # Auth dependency injection & RBAC guards
│   │   │   └── endpoints/                  # Modular REST routers
│   │   │       ├── auth.py                 # JWT signup, login, refresh, logout
│   │   │       ├── predict.py              # Upload, inference invocation, scan detail
│   │   │       ├── expert.py               # Agronomist review queue & audit submissions
│   │   │       ├── alerts.py               # Notifications & read-status management
│   │   │       ├── history.py              # Farmer diagnosis history & timeline
│   │   │       ├── weather.py              # OpenWeather current conditions & forecast
│   │   │       ├── crops.py                # Supported crop species & catalog
│   │   │       ├── tts.py                  # Audio generation & asset streaming
│   │   │       ├── admin.py                # Administrative telemetry & user controls
│   │   │       ├── translation.py          # On-demand entity translation overlay
│   │   │       └── mlops.py                # Retraining candidate export & registry
│   │   ├── core/                           # Database engine, config settings, storage clients
│   │   ├── models/                         # SQLAlchemy declarative schema models
│   │   ├── schemas/                        # Pydantic validation schemas
│   │   ├── services/                       # Third-party integrations (Gemini, Weather, TTS)
│   │   └── crud/                           # Database repository queries
│   ├── alembic/                            # Database migration versions
│   ├── requirements.txt
│   └── Dockerfile                          # Cloud Run container definition for backend
│
├── model_service/                          # Dedicated Computer Vision Microservice (Server 2)
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
│   ├── main.py                             # Lightweight FastAPI inference runner
│   ├── requirements.txt
│   └── Dockerfile                          # CPU-optimised Cloud Run container definition
│
├── frontend/                               # React 18 + Vite Web Application
│   ├── src/
│   │   ├── pages/                          # Application view pages
│   │   │   ├── DashboardPage.tsx           # Farmer dashboard with quick telemetry
│   │   │   ├── ScanPage.tsx                # Drag-and-drop diagnostic leaf capture
│   │   │   ├── PredictionResultPage.tsx    # Diagnosis report, Grad-CAM viewer, audio player
│   │   │   ├── AlertsPage.tsx              # Notifications with scan link & auto-read
│   │   │   ├── ExpertQueuePage.tsx         # Agronomist triage desk
│   │   │   ├── ExpertReviewPage.tsx        # Side-by-side diagnostic verification interface
│   │   │   └── HistoryPage.tsx             # Longitudinal scan records
│   │   ├── components/                     # Reusable UI component library
│   │   ├── api/                            # Typed HTTP client modules
│   │   ├── context/                        # AuthContext & LanguageContext
│   │   └── i18n/                           # Localised dictionaries (EN, HI, GU)
│   ├── package.json
│   └── vite.config.ts
│
├── Docs/                                   # Architecture, API, & deployment specifications
└── README.md
```

---

## Diagnostic Pipeline

```
  Step 1: Input
    Farmer captures or uploads a leaf image (.jpg, .png, .webp).
           │
           ▼
  Step 2: Backend Gateway (`smart-farming-backend`)
    • Computes SHA-256 hash of image bytes.
    • Checks Upstash Redis REST for existing deduplication match (<20ms).
    • Saves raw leaf to Google Cloud Storage (`uploads/{hash}.jpg`).
           │
           ▼
  Step 3: Vision Microservice (`inference-service`)
    • Preprocessing: OpenCV checks blur score, brightness score, leaf mask.
    • Crop Identification: EfficientNet-B0 predicts species (e.g., Tomato).
    • Decision Router: Selects the Tomato EfficientNet-B2 disease model.
    • Disease Classification: Predicts condition (e.g., Early Blight) + confidence.
    • Severity Estimation: Estimates affected leaf area (0–100%).
    • Pest Detection: YOLOv8 flags presence of agricultural pests.
    • Grad-CAM: Generates activation heatmap and saves to GCS (`processed/{hash}.jpg`).
           │
           ▼
  Step 4: Contextual Enrichment & Synthesis
    • Weather: Fetches live local weather metrics via OpenWeather API.
    • LLM Advisory: Google Gemini 2.5 Flash generates organic, chemical, and preventive advice.
    • Translation: Asynchronously generates Hindi & Gujarati translations in Upstash Redis.
    • Audio: Synthesizes spoken advisory via Google Cloud Text-to-Speech.
           │
           ▼
  Step 5: Delivery & Triage
    • Returns structured JSON to frontend.
    • If disease confidence < 70%, automatically enqueues for Expert Agronomist review.
    • Generates notification alert in farmer's alerts inbox.
```

---

## Getting Started

### Prerequisites

- **Python:** 3.11+
- **Node.js:** 18+ (with npm)
- **Supabase Account:** PostgreSQL database connection string
- **Upstash Account:** Redis REST URL and Bearer Token
- **Google Cloud Account:** GCS Bucket & API keys (Gemini, TTS, Translation)

---

### 1. Model Inference Microservice (Server 2)

```powershell
# Navigate to model_service
cd model_service

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux / macOS

# Install dependencies (CPU PyTorch + OpenCV + YOLO)
pip install -r requirements.txt

# Start the inference microservice on port 8001
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Health check: **http://localhost:8001/health**

---

### 2. Backend Gateway Server (Server 1)

```powershell
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux / macOS

# Install dependencies
pip install -r requirements.txt

# Configure your environment
cp .env.example .env
# Edit .env with your Supabase DATABASE_URL, UPSTASH credentials, and API keys

# Apply database migrations
alembic upgrade head

# Start the API Gateway on port 8000
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive Swagger Docs: **http://localhost:8000/docs**

---

### 3. Frontend Dashboard

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start local development server
npm run dev
```

Application will be accessible at **http://localhost:5173**.

---

## Environment Configuration

Configure these parameters in `backend/.env`:

| Key | Description | Example / Default |
|---|---|---|
| `ENVIRONMENT` | Deployment environment | `production` / `development` |
| `DEBUG` | Enable debug logs | `False` |
| `DATABASE_URL` | Supabase PostgreSQL connection string | `postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres?sslmode=require` |
| `JWT_SECRET_KEY` | HMAC SHA-256 signing secret for authentication tokens | Secure 64-char hex string |
| `MODEL_SERVER_URL` | URL of dedicated Model Inference Microservice | `http://localhost:8001` or Cloud Run URL |
| `UPSTASH_REDIS_REST_URL` | Upstash Serverless Redis REST endpoint | `https://xxx.upstash.io` |
| `UPSTASH_REDIS_REST_TOKEN`| Upstash Bearer authorization token | `[YOUR-UPSTASH-TOKEN]` |
| `STORAGE_BACKEND` | Active storage provider | `gcs`, `s3`, or `local` |
| `AWS_ACCESS_KEY_ID` | GCS HMAC Access Key or AWS S3 Key | `GOOG1E...` |
| `AWS_SECRET_ACCESS_KEY` | GCS HMAC Secret Key or AWS S3 Secret | `[YOUR-SECRET-KEY]` |
| `AWS_ENDPOINT_URL` | Custom S3 endpoint (for GCS compatibility) | `https://storage.googleapis.com` |
| `AWS_S3_BUCKET` | Target bucket name | `smart-farming-data` |
| `GEMINI_API_KEY` | Google Gemini API key for treatment advisories | `[YOUR-GEMINI-KEY]` |
| `OPENWEATHER_API` | OpenWeather API key for live weather fetching | `[YOUR-OPENWEATHER-KEY]` |
| `GOOGLE_TTS_API_KEY` | Google Cloud Text-to-Speech API key | `[YOUR-TTS-KEY]` |
| `GOOGLE_TRANSLATION_API_KEY`| Google Cloud Translation API key | `[YOUR-TRANSLATE-KEY]` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `https://smart-farming-dashboard-green.vercel.app,http://localhost:5173` |

> [!CAUTION]
> Special characters in the database password (such as `@`, `#`, `$`) must be percent-encoded (e.g. `@` $\to$ `%40`) to prevent URI parsing failures. Never commit plain-text credentials to Git.

---

## Key API Endpoints

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Auth** | `POST` | `/auth/register` | Register new farmer, expert, or administrator |
| | `POST` | `/auth/login` | Authenticate and obtain JWT access & refresh tokens |
| | `POST` | `/auth/refresh` | Refresh expired access token |
| **Diagnostics** | `POST` | `/predict` | Upload leaf image, invoke vision microservice, synthesize advice |
| | `GET` | `/predictions/{id}` | Retrieve diagnosis details, Grad-CAM URLs, auto-mark alert read |
| | `POST` | `/predictions/{id}/rescan` | Submit follow-up treatment progress scan |
| **Alerts** | `GET` | `/alerts` | Get user notifications and triage advisories |
| | `POST` | `/alerts/{id}/read` | Mark individual alert as read |
| **Expert Triage** | `GET` | `/expert/queue` | List low-confidence diagnoses pending agronomist triage |
| | `GET` | `/expert/reviews/{id}` | Get review case with presigned raw leaf and Grad-CAM URLs |
| | `POST` | `/expert/reviews/{id}` | Approve, override, or request rescan with agronomist guidance |
| **Telemetry** | `GET` | `/weather` | Fetch live meteorological metrics for farm coordinates |
| | `GET` | `/crops` | Catalog of supported crop species, pathogens, and symptoms |
| | `GET` | `/history` | Longitudinal diagnostic timeline for authenticated user |
| | `GET` | `/admin/metrics` | System health, model inference latencies, triage counts |

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

## Production Deployment

The platform is deployed using continuous deployment triggers connected to GitHub:

| Service | Hosting Provider | Deployment Strategy |
|---|---|---|
| **API Gateway** (`smart-farming-backend`) | Google Cloud Run (`us-central1`) | Automated build via Cloud Build on git push to `main` |
| **Vision Microservice** (`inference-service`) | Google Cloud Run (`us-central1`) | Automated build via Cloud Build on git push to `main` |
| **Frontend Dashboard** | Vercel Edge Network | Automated deployment from GitHub repository |
| **Database** | Supabase Cloud | Managed PostgreSQL with connection pooler on port `5432` |
| **Redis Cache** | Upstash Serverless | Distributed REST-based Redis cluster |
| **Object Storage** | Google Cloud Storage | Regional bucket `smart-farming-data` with HMAC authentication |

For step-by-step instructions on setting up production infrastructure, refer to the [Deployment Guide](Docs/Deployment_Guide.md).

---

## Running Tests

Execute backend test suites:

```powershell
cd backend
python -m pytest tests/ -v
```

Execute frontend test and build verification:

```powershell
cd frontend
npm run build
```

---

## Documentation Index

Comprehensive documentation is available in the [`Docs/`](Docs/) directory:

- [Architecture & System Design](Docs/Architecture.md) — Comprehensive technical specification of all layers, contracts, and services.
- [API Specification](Docs/API_Specification.md) — OpenAPI / REST endpoint schemas, request parameters, and response structures.
- [Deployment Guide](Docs/Deployment_Guide.md) — Cloud Run, Vercel, Supabase, and Upstash deployment runbooks.
- [Configuration Reference](Docs/Config_Reference.md) — Complete environment variable and `config.yaml` dictionary.
- [Authentication & Roles](Docs/Auth_Roles.md) — RBAC matrix, token lifecycle, and session security models.
- [Model Cards](Docs/Model_Cards.md) — Model metrics, architecture benchmarks, datasets, and limitations.
- [MLOps & Retraining Loop](Docs/MLOps_Retraining.md) — Feedback ingestion, dataset candidate curation, and model promotion.
- [UI / UX Design System](Docs/UI_UX_Spec.md) — Design tokens, component states, and accessibility standards.

---

*AI-Powered Smart Farming — Documentation*  
*Last Updated: September 2026*
