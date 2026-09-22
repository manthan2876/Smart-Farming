# 🌾 Smart Farming — AI-Powered Crop Disease Diagnosis

> Full-stack web application for AI-driven crop disease diagnosis, treatment recommendations, and farm management.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5%2B-3178C6?logo=typescript)](https://typescriptlang.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-EfficientNet-EE4C2C?logo=pytorch)](https://pytorch.org)

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture & Pipeline](#architecture--pipeline)
- [Folder Structure](#folder-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [With Redis (Async Pipeline)](#with-redis-async-pipeline)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [User Roles](#user-roles)
- [Running Tests](#running-tests)
- [Documentation Index](#documentation-index)

---

## Overview

**Smart Farming** is a full-stack AI platform designed to assist farmers with rapid, accurate crop disease diagnosis. A farmer simply uploads a photo of a diseased leaf — the system does the rest:

1. **Crop Identification** — Identifies the crop species from the image.
2. **Disease Classification** — Runs a per-crop specialist model to classify the disease.
3. **Severity Estimation** — Estimates disease severity using computer-vision heuristics.
4. **Pest Detection** — Detects pest presence using a YOLOv8-based classifier.
5. **Weather Context** — Fetches live weather data to enrich the agronomic context.
6. **LLM Recommendation** — Generates a tailored, actionable treatment recommendation via an LLM.

Results are presented in the farmer's preferred language (English, Hindi, or Gujarati) with text-to-speech support. Low-confidence diagnoses are routed to a human expert queue for agronomist review, and all predictions feed back into an MLOps retraining pipeline.

---

## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| API Framework | Python, FastAPI |
| ORM / Database | SQLAlchemy, PostgreSQL (SQLite for dev) |
| Async Job Queue | Redis + ARQ |
| DB Migrations | Alembic |
| Object Storage | MinIO / AWS S3 |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React + TypeScript, Vite |
| Styling | Tailwind CSS |
| Routing | React Router |
| Internationalisation | i18n — English, Hindi, Gujarati |

### ML / AI
| Model | Architecture | Purpose |
|---|---|---|
| Crop Identifier | EfficientNet-B0 (PyTorch) | Identify crop species from leaf image |
| Disease Classifiers | EfficientNet-B2 (per-crop, PyTorch) | Classify disease for each crop type |
| Pest Classifier | YOLOv8-cls | Detect and classify pest presence |
| Preprocessing | OpenCV | Image normalisation + severity heuristic |
| LLM | Qwen/Qwen3-4B-Instruct-2507 (HuggingFace / nscale) | Generate treatment recommendations |

---

## Architecture & Pipeline

```
Farmer uploads leaf photo
          │
          ▼
  ┌───────────────┐
  │ Preprocessing │  (OpenCV — resize, normalise)
  └──────┬────────┘
         │
         ▼
  ┌───────────────────┐
  │  Crop Identifier  │  (EfficientNet-B0)
  └──────┬────────────┘
         │  crop label + confidence
         ▼
  ┌──────────────────────┐
  │  Disease Classifier  │  (EfficientNet-B2, per-crop)
  └──────┬───────────────┘
         │
         ├──────────────────────────────────┐
         ▼                                  ▼
  ┌─────────────────┐             ┌─────────────────┐
  │ Severity Estim. │             │  Pest Detector  │
  │   (OpenCV)      │             │  (YOLOv8-cls)   │
  └──────┬──────────┘             └──────┬──────────┘
         │                               │
         └──────────────┬────────────────┘
                        │
                        ▼
                ┌──────────────┐
                │ Weather API  │
                └──────┬───────┘
                       │
                       ▼
              ┌─────────────────────┐
              │  LLM Recommendation │  (Qwen3-4B)
              └──────┬──────────────┘
                     │
                     ▼
         Structured diagnosis + advice
        (rendered in chosen language 🌐)
```

Low-confidence predictions → **Expert Review Queue** → agronomist approval / override → **MLOps Retraining Pipeline**.

For full details, see [Docs/Architecture.md](Docs/Architecture.md).

---

## Folder Structure

```
Smart-Farming/
├── backend/                        # FastAPI backend + ML pipeline
│   ├── src/app/
│   │   ├── main.py                 # Application entry point
│   │   ├── pipeline.py             # Pipeline orchestrator
│   │   ├── context.py              # Shared pipeline context factory
│   │   ├── api/endpoints/          # REST API routes
│   │   │   ├── auth.py
│   │   │   ├── predict.py
│   │   │   ├── history.py
│   │   │   ├── expert.py
│   │   │   ├── admin.py
│   │   │   ├── farm.py
│   │   │   ├── feedback.py
│   │   │   ├── weather.py
│   │   │   ├── crops.py
│   │   │   ├── tts.py
│   │   │   ├── mlops.py
│   │   │   ├── alerts.py
│   │   │   └── translation.py
│   │   ├── services/               # ML & business logic services
│   │   │   ├── preprocessing.py
│   │   │   ├── crop_identifier.py
│   │   │   ├── decision_engine.py
│   │   │   ├── disease_classifier.py
│   │   │   ├── severity.py
│   │   │   ├── pest_detector.py
│   │   │   ├── weather.py
│   │   │   ├── recommendation.py
│   │   │   ├── rag.py
│   │   │   └── translation.py
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── crud/                   # Database CRUD operations
│   │   ├── core/                   # Config, DB session, security, ARQ, scheduler
│   │   └── utils/                  # Model loader, logging, JSON utilities
│   ├── alembic/                    # Database migration scripts
│   ├── scripts/
│   │   ├── train_eval.py           # Model training & evaluation script
│   │   └── migrate_to_s3.py        # Local-to-S3 storage migration
│   ├── config.yaml                 # Model paths + inference thresholds
│   ├── model_registry.json         # Promoted model version history
│   └── requirements.txt
│
├── frontend/                       # React / TypeScript SPA
│   ├── src/
│   │   ├── pages/                  # Application pages
│   │   │   ├── LandingPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ScanPage.tsx
│   │   │   ├── ProcessingPage.tsx
│   │   │   ├── PredictionResultPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   ├── ExpertQueuePage.tsx
│   │   │   ├── ExpertReviewPage.tsx
│   │   │   ├── AdminMetricsPage.tsx
│   │   │   ├── AdminUsersPage.tsx
│   │   │   ├── AdminFeedbackPage.tsx
│   │   │   ├── AlertsPage.tsx
│   │   │   ├── WeatherPage.tsx
│   │   │   ├── FarmSettingsPage.tsx
│   │   │   ├── CropsPage.tsx
│   │   │   ├── SettingsPage.tsx
│   │   │   ├── AboutPage.tsx
│   │   │   └── ServicesPage.tsx
│   │   ├── components/             # Reusable UI components
│   │   │   ├── Appshell.tsx
│   │   │   ├── SideBar.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   ├── Toast.tsx
│   │   │   ├── PublicNav.tsx
│   │   │   └── ui/                 # Primitive components (Button, Card, Input, Badge, Modal, Table)
│   │   ├── api/                    # Typed API client modules
│   │   │   ├── auth.ts
│   │   │   ├── predictions.ts
│   │   │   ├── farm.ts
│   │   │   ├── admin.ts
│   │   │   ├── crops.ts
│   │   │   ├── expert.ts
│   │   │   └── alerts.ts
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   ├── hooks/
│   │   │   ├── usePredict.ts
│   │   │   └── useToast.ts
│   │   └── i18n/                   # Translation files (en, hi, gu)
│   └── package.json
│
├── Docs/                           # Project documentation
├── data/                           # Sample processed images
└── README.md
```

---

## Getting Started

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend build toolchain |
| Redis | 7+ | Optional — required for async pipeline |
| PostgreSQL | 14+ | Optional — SQLite used by default in dev |

---

### Backend Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Open .env and set SECRET_KEY, HF_TOKEN, DATABASE_URL, etc.

# 5. Run database migrations
alembic upgrade head

# 6. Start the API server
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000**.  
Interactive Swagger UI: **http://localhost:8000/docs**

---

### Frontend Setup

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment variables
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000

# 4. Start the development server
npm run dev
```

The app will be available at **http://localhost:5173**.

---

### With Redis (Async Pipeline)

When Redis is available, predictions are processed asynchronously via the ARQ worker, improving API response times and resilience.

```bash
# Terminal 1 — Start Redis via Docker
docker run -d -p 6379:6379 redis:7-alpine

# Terminal 2 — Start the ARQ worker
cd backend
python -m arq src.app.worker.WorkerSettings

# Terminal 3 — Start the API server
cd backend
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Environment Variables

Configure these in `backend/.env`. A template is provided in `backend/.env.example`.

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing secret key | `dev-secret-key-change-me` |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./dev_database.db` |
| `REDIS_URL` | Redis connection URL | `redis://127.0.0.1:6379` |
| `HF_TOKEN` | HuggingFace API token (required for LLM recommendations) | **required** |
| `STORAGE_BACKEND` | Object storage backend — `local` or `s3` | `local` |
| `AWS_ACCESS_KEY_ID` | AWS / MinIO access key (if `STORAGE_BACKEND=s3`) | — |
| `AWS_SECRET_ACCESS_KEY` | AWS / MinIO secret key (if `STORAGE_BACKEND=s3`) | — |
| `GOOGLE_TTS_API_KEY` | Google Cloud Text-to-Speech API key | — |
| `GOOGLE_TRANSLATION_API_KEY` | Google Cloud Translation API key | — |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:5173` |
| `ENVIRONMENT` | Runtime environment — `development` or `production` | `development` |

> **Note:** Never commit your `.env` file to version control. The `.gitignore` excludes it by default.

For a full reference of all configuration options including `config.yaml` fields, see [Docs/Config_Reference.md](Docs/Config_Reference.md).

---

## API Documentation

Once the backend server is running, the full interactive API reference is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

For a static, version-controlled API specification with example requests and responses, see [Docs/API_Specification.md](Docs/API_Specification.md).

### Key Endpoints at a Glance

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Obtain JWT access token |
| `POST` | `/api/v1/predict` | Upload leaf image and run diagnosis pipeline |
| `GET` | `/api/v1/history` | Retrieve prediction history |
| `GET` | `/api/v1/expert/queue` | List predictions pending expert review |
| `POST` | `/api/v1/expert/review/{id}` | Submit expert override |
| `GET` | `/api/v1/admin/metrics` | System-wide usage and model metrics |
| `GET` | `/api/v1/weather` | Fetch weather data for a location |
| `GET` | `/api/v1/crops` | List supported crops and diseases |

---

## User Roles

The system supports three distinct roles with different permissions:

### 🧑‍🌾 Farmer
- Upload leaf photos and receive AI-powered diagnoses
- View prediction history and detailed results
- Manage farm profile and plot information
- Submit feedback on diagnosis accuracy
- Receive treatment recommendations in their preferred language (EN / HI / GU)

### 🌿 Expert (Agronomist)
- Access the expert review queue for low-confidence predictions
- Override or approve AI-generated diagnoses
- Add agronomic notes and amended recommendations
- Flag predictions for inclusion in model retraining datasets

### 🛠️ Admin
- Full access to all system resources
- User management (create, suspend, assign roles)
- System metrics and usage dashboard
- Manage MLOps controls — trigger retraining, promote model versions
- Review aggregate feedback and adjust inference thresholds

For the complete authentication flow and permission matrix, see [Docs/Auth_Roles.md](Docs/Auth_Roles.md).

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

To run with coverage:

```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Documentation Index

All project documentation lives in the [`Docs/`](Docs/) directory.

| Document | Description |
|---|---|
| [Architecture.md](Docs/Architecture.md) | System architecture, ML pipeline design, and service boundaries |
| [API_Specification.md](Docs/API_Specification.md) | Full REST API reference with example requests and responses |
| [Auth_Roles.md](Docs/Auth_Roles.md) | Authentication flow, JWT handling, and role/permission matrix |
| [DATASET.md](Docs/DATASET.md) | Dataset sources, supported crop/disease class lists, preprocessing steps |
| [Model_Cards.md](Docs/Model_Cards.md) | Model architectures, training metrics, evaluation results, and known limitations |
| [Config_Reference.md](Docs/Config_Reference.md) | `config.yaml` fields and full environment variable reference |
| [UI_UX_Spec.md](Docs/UI_UX_Spec.md) | Frontend component design system and page-level specifications |
| [Deployment_Guide.md](Docs/Deployment_Guide.md) | Docker, Nginx reverse-proxy, and production environment provisioning |
| [MLOps_Retraining.md](Docs/MLOps_Retraining.md) | How prediction logs and expert feedback feed back into model retraining |

---

## Contributing

1. Fork the repository and create a feature branch (`git checkout -b feature/your-feature`).
2. Make your changes with clear, descriptive commits.
3. Ensure all tests pass (`pytest tests/ -v`).
4. Open a pull request with a summary of your changes.

---

## License

This project was developed as part of **B.Tech. IT 4th Year Minor Project** (Refrence: SIH 25099).
