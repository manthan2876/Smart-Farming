# Configuration Reference — AI-Powered Smart Farming

- **Project:** AI-Powered Smart Farming
- **Version:** 2.2 (Monorepo & Cloud Architecture)
- **Date:** 22 October 2026
- **Status:** Active / Production Reference

---

This document is the definitive single source of truth for all runtime configuration in the Smart Farming platform. It covers the ML pipeline configuration file, backend environment variables, AI microservice variables, frontend and mobile environment settings, the model registry, and dynamic configuration hot-reloading.

## Table of Contents

1. [config.yaml — ML Pipeline](#1-configyaml--ml-pipeline)
   - [Full File](#full-file)
   - [Field Reference](#field-reference)
2. [Environment Variables — Backend](#2-environment-variables--backend)
   - [Security & Authentication](#security--authentication)
   - [Database](#database)
   - [Unified AI Microservice (Single Source of Truth)](#unified-ai-microservice-single-source-of-truth)
   - [Storage & Media Assets (Supabase Default)](#storage--media-assets-supabase-default)
   - [Redis, Caching & Task Queues](#redis-caching--task-queues)
   - [Upstash QStash & Internal Crons](#upstash-qstash--internal-crons)
   - [Geographic Defaults (Indian Agricultural Reference)](#geographic-defaults-indian-agricultural-reference)
   - [External AI & Cloud Integrations](#external-ai--cloud-integrations)
   - [SMTP Email Dispatch](#smtp-email-dispatch)
3. [Environment Variables — AI Microservice (Hugging Face Space)](#3-environment-variables--ai-microservice-hugging-face-space)
4. [Environment Variables — Frontend (React)](#4-environment-variables--frontend-react)
5. [Environment Variables — Mobile (Flutter)](#5-environment-variables--mobile-flutter)
6. [model_registry.json](#6-model_registryjson)
7. [Dynamic Configuration & Hot Reload](#7-dynamic-configuration--hot-reload)

---

## 1. `config.yaml` — ML Pipeline

**Location:** `backend/config.yaml` (also packaged in `ai_service/config.yaml`)

Defines model checkpoints, confidence thresholds, and local filesystem directories. All relative paths are resolved relative to the component root.

> [!TIP]
> The `thresholds` section can be updated at runtime without a server restart using the Admin API or Upstash Redis REST sync. See [Dynamic Configuration & Hot Reload](#7-dynamic-configuration--hot-reload).

### Full File

```yaml
models:
  crop_identifier:
    path: models/crop_identifier_v1.pth
    labels: models/crop_identifier_labels.json
    arch: efficientnet_b0
  disease_models:
    Cotton:
      path: models/disease_Cotton.pth
      labels: models/disease_Cotton_labels.json
      arch: efficientnet_b2
    Groundnut:
      path: models/disease_Groundnut.pth
      labels: models/disease_Groundnut_labels.json
      arch: efficientnet_b2
    Pepper_Bell:
      path: models/disease_Pepper_Bell.pth
      labels: models/disease_Pepper_Bell_labels.json
      arch: efficientnet_b2
    Potato:
      path: models/disease_Potato.pth
      labels: models/disease_Potato_labels.json
      arch: efficientnet_b2
    Tomato:
      path: models/disease_Tomato.pth
      labels: models/disease_Tomato_labels.json
      arch: efficientnet_b2
  pest_classifier:
    path: models/pest_classifier/pest_classifier.pt
thresholds:
  crop_confidence: 0.70
  disease_confidence: 0.70
  blur_var_threshold: 50.0
  min_brightness: 40.0
  max_brightness: 240.0
storage:
  upload_dir: data/uploads/
  processed_dir: data/processed/
```

### Field Reference

#### `models.crop_identifier`
- `path`: Path to crop classifier weights (`.pth`).
- `labels`: Path to JSON index-to-label class mapping.
- `arch`: Network backbone (default: `efficientnet_b0`).

#### `models.disease_models.{CropName}`
One entry per supported crop: `Cotton`, `Groundnut`, `Pepper_Bell`, `Potato`, `Tomato`. Keys must match the class output of the crop identifier.

#### `models.pest_classifier`
- `path`: Path to YOLOv8 pest detection weights (`.pt`). If missing at startup, pest detection is gracefully bypassed without halting the diagnostic pipeline.

#### `thresholds`
- `crop_confidence` (default: `0.70`): Minimum confidence required before routing to a crop-specific disease classifier. Below this cutoff, the crop is deemed ambiguous.
- `disease_confidence` (default: `0.70`): Predictions scoring below this confidence trigger automatic escalation to the agronomist expert review queue (`status = pending_expert_review`).
- `blur_var_threshold` (default: `50.0`): Minimum Laplacian variance for sharpness. Unfocused images are rejected with `failed_blur`.
- `min_brightness` (default: `40.0`) & `max_brightness` (default: `240.0`): Permissible lighting range in HSV V-channel mean.

---

## 2. Environment Variables — Backend

**Location:** `backend/.env` (Local) or Render Dashboard Environment Variables (Production)

### Security & Authentication

| Variable | Type | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | string | `dev-secret-key-change-me` | Legacy key field; auth token creation uses `JWT_SECRET_KEY`. |
| `JWT_SECRET_KEY` | string | `dev-secret-key-change-me` | HS256 signing key. A unique random key of at least 32 characters is required in production/staging. |
| `ALGORITHM` | string | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `30` | Access token lifetime in minutes. |
| `ENVIRONMENT` | string | `development` | Deployment mode: `development` or `production`. In production, enforces strict security policies. |
| `DEBUG` | bool | `True` | When `True`, enables `X-User-ID` header bypass for local dev. **Must be `False` in production.** |
| `CORS_ORIGINS` | string | empty | Exact, comma-separated allowed origins. Must include the deployed frontend origin in production/staging; wildcard/regex matching is not used. |

### Database

| Variable | Type | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | string | `sqlite:///./dev_database.db` | SQLAlchemy connection string. In production, points to Supabase Managed PostgreSQL via Session Pooler (`postgresql://postgres.<REF>:<PASS>@aws-0-<REGION>.pooler.supabase.com:5432/postgres?sslmode=require`). |
| `PROD_DATABASE_URL` | string | `None` | Optional production fallback DSN. |

### Unified AI Microservice (Single Source of Truth)

All AI, computer vision, translation, LLM advisory, and speech capabilities are centralized under the unified microservice deployed on Hugging Face Spaces.

| Variable | Type | Default | Description |
|---|---|---|---|
| `AI_SERVICE_URL` | string | `https://maharsh8805-smart-farming-ai.hf.space` | **Single source of truth.** Base URL of the unified AI microservice. Subroutes are automatically derived from this value. |
| `MODEL_SERVER_URL` | string | `{AI_SERVICE_URL}/vision` | Automatically derived endpoint for the 7-stage vision pipeline. |
| `MODEL_SERVER_TIMEOUT` | int | `120` | Maximum timeout in seconds for deep learning vision inference. |
| `TRANSLATION_SERVER_URL`| string | `{AI_SERVICE_URL}/translation` | Automatically derived endpoint for IndicTrans2 translation. |
| `TRANSLATION_SERVER_TIMEOUT` | float | `45.0` | Timeout in seconds for regional translation queries. |
| `ADVISORY_SERVER_URL` | string | `{AI_SERVICE_URL}/advisory` | Automatically derived endpoint for LLM agronomic advisory. |
| `ADVISORY_SERVER_TIMEOUT` | float | `60.0` | Timeout in seconds for LLM reasoning. |
| `TTS_SERVER_URL` | string | `{AI_SERVICE_URL}/tts` | Automatically derived endpoint for neural speech synthesis. |
| `TTS_SERVER_TIMEOUT` | float | `90.0` | Timeout in seconds for audio generation. |
| `GATEWAY_API_KEY` | string | `None` | Optional Bearer authorization key for securing the AI microservice. |

> [!NOTE]
> Pydantic model validators in `backend/src/app/core/config.py` automatically sanitize endpoints and purge obsolete tunnels (`trycloudflare.com`, `workers.dev`, `ngrok`), ensuring all subroutes consistently point to `AI_SERVICE_URL`.

### Storage & Media Assets (Supabase Default)

The backend features a unified storage abstraction layer (`backend/src/app/core/storage.py`) supporting Supabase Object Storage and local disk. The legacy `s3` value is an alias for the Supabase-compatible implementation, not a separately configured AWS S3 driver.

| Variable | Type | Default | Description |
|---|---|---|---|
| `STORAGE_BACKEND` | string | `supabase` | Primary storage engine: `supabase` (production default), `s3`, or `local`. |
| `SUPABASE_URL` | string | `""` | Supabase project URL (e.g., `https://<project-ref>.supabase.co`). |
| `SUPABASE_SERVICE_ROLE_KEY` | string | `""` | Supabase privileged service role key for direct storage bucket write/delete. |
| `SUPABASE_ANON_KEY` | string | `""` | Supabase public anonymous API key. |
| `SUPABASE_BUCKET` | string | `smart-farming-data-dev` | Target Supabase storage bucket name for media assets. |
| `SUPABASE_SIGNED_URL_EXPIRY_SECONDS` | int | `900` | Expiration time for signed download URLs (default: 15 minutes / 900s). |
| `UPLOAD_MAX_BYTES` | int | `10485760` | Server-side upload ceiling (default: 10 MB / 10 × 1024²). |

#### Backward-Compatible S3 Fallback Variables

| Variable | Type | Default | Description |
|---|---|---|---|
| `AWS_ACCESS_KEY_ID` | string | unused | Not consumed by the current storage backend. |
| `AWS_SECRET_ACCESS_KEY` | string | unused | Not consumed by the current storage backend. |
| `AWS_REGION` | string | unused | Not consumed by the current storage backend. |
| `AWS_S3_BUCKET` | string | Legacy alias to `SUPABASE_BUCKET` | Compatibility setting; this does not configure an AWS S3 client. |
| `S3_PRESIGNED_EXPIRY_SECONDS` | int | `900` | Alias to `SUPABASE_SIGNED_URL_EXPIRY_SECONDS`. |

### Redis, Caching & Task Queues

| Variable | Type | Default | Description |
|---|---|---|---|
| `REQUIRE_REDIS` | bool | `False` | **`False` in Render / production:** Disables continuous TCP worker polling to enable instant cold starts and scale-to-zero.<br>**`True` in local dev:** Activates local ARQ worker queue. |
| `UPSTASH_REDIS_REST_URL` | string | `None` | Upstash Serverless Redis REST endpoint (`https://<db>.upstash.io`). Powers phrase translation cache, image deduplication, weather cache, and dynamic threshold sync. |
| `UPSTASH_REDIS_REST_TOKEN`| string | `None` | Upstash Serverless Redis REST bearer token. |
| `LOCAL_REDIS_URL` | string | `redis://localhost:6379`| Local Redis connection URL for ARQ workers. |

### Upstash QStash & Internal Crons

Used for serverless scheduled jobs without maintaining always-on background worker daemons.

| Variable | Type | Default | Description |
|---|---|---|---|
| `QSTASH_URL` | string | `https://qstash.upstash.io/v2` | Upstash QStash REST API base URL. |
| `QSTASH_TOKEN` | string | `None` | QStash authentication token for scheduling jobs. |
| `QSTASH_CURRENT_SIGNING_KEY` | string | `None` | Current HMAC key used to verify incoming multi-region webhook signatures (`Upstash-Signature`). |
| `QSTASH_NEXT_SIGNING_KEY` | string | `None` | Next signing key used during zero-downtime key rotation. |
| `CRON_SECRET` | string | `None` | Shared header secret (`x-cron-secret` or `Authorization: Bearer <CRON_SECRET>`) for verifying internal cron webhook endpoints (`/api/v1/internal/cron/*`). |
| `METRICS_API_KEY` | string | `None` | Header key (`x-api-key`) for read-only polling of `/api/v1/admin/metrics` by GitHub Actions MLOps drift monitor. |

### Geographic Defaults (Indian Agricultural Reference)

When client GPS coordinates are omitted or unavailable, the backend uses these agricultural reference coordinates for meteorological lookups:

| Variable | Type | Default | Description |
|---|---|---|---|
| `DEFAULT_LAT` | float | `21.7645` | Default latitude coordinate (Gujarat, India). |
| `DEFAULT_LON` | float | `72.1519` | Default longitude coordinate (Gujarat, India). |
| `DEFAULT_LOCATION` | string | `Gujarat, India` | Default location string representation. |

### External AI & Cloud Integrations

| Variable | Type | Default | Description |
|---|---|---|---|
| `OPENWEATHER_API` | string | `""` | OpenWeatherMap API key for live temperature, humidity, and rainfall metrics. |
| `GROQ_API_KEY` | string | `""` | Groq cloud API key for ultra-fast Llama-3.3-70B agronomic advisory inference. |
| `GROQ_MODEL` | string | `llama-3.3-70b-versatile` | Groq LLM model name. |
| `GEMINI_API_KEY` | string | `""` | Google Gemini API key used as fallback for multimodal advisory. |
| `HF_TOKEN` | string | `""` | Hugging Face user access token for model hub access. |

### SMTP Email Dispatch

| Variable | Type | Default | Description |
|---|---|---|---|
| `SMTP_HOST` | string | `None` | SMTP mail relay server (e.g., `smtp.gmail.com` or custom SMTP provider). |
| `SMTP_PORT` | int | `587` | SMTP port (587 for STARTTLS). |
| `SMTP_USER` | string | `None` | Authenticated sender email address. |
| `SMTP_PASSWORD` | string | `None` | SMTP password or app password. |
| `SMTP_TLS` | bool | `True` | Enable STARTTLS encryption. |
| `EMAILS_FROM_EMAIL` | string | `None` | From email address header. |
| `EMAILS_FROM_NAME` | string | `Smart Farming Support` | Friendly display name. |
| `FRONTEND_URL` | string | `http://localhost:5173` | Frontend URL included in password reset email links. |

---

## 3. Environment Variables — AI Microservice (Hugging Face Space)

**Location:** Hugging Face Space Settings $\to$ Variables & Secrets (or `ai_service/.env`)

| Variable | Type | Default | Description |
|---|---|---|---|
| `PORT` | int | `7860` | HTTP listening port (strictly `7860` on Hugging Face Spaces). |
| `FORCE_CPU` | bool | `False` | Force PyTorch CPU execution even if CUDA is detected. |
| `CPU_THREADS` | int | `min(cpu_count, 4)` | Number of PyTorch CPU inference threads. |
| `USE_LOCAL_LLM` | bool | `True` | Whether to load in-memory Qwen2.5-1.5B for local advisory generation. |
| `LOCAL_LLM_MODEL` | string | `Qwen/Qwen2.5-1.5B-Instruct` | Hugging Face model identifier for local LLM advisory. |
| `GROQ_API_KEY` | string | `""` | Optional Groq API key for cloud LLM advisory acceleration. |
| `GROQ_MODEL` | string | `llama-3.3-70b-versatile` | Target Groq model. |
| `GEMINI_API_KEY` | string | `""` | Google Gemini API key for fallback advisory. |
| `INDICTRANS_MODEL` | string | `ai4bharat/indictrans2-en-indic-dist-200M` | Distilled IndicTrans2 model for English $\to$ Hindi/Gujarati translation. |
| `GATEWAY_SECRET` | string | `""` | Optional shared Bearer secret for incoming API requests. |

---

## 4. Environment Variables — Frontend (React)

**Location:** `frontend/.env` (Local) or Vercel Project Environment Variables (Production)

| Variable | Type | Example | Description |
|---|---|---|---|
| `VITE_API_URL` | string | `https://smart-farming-backend.onrender.com` | Backend API base URL consumed by the Fetch wrapper in `frontend/src/api/client.ts`. |
| `VITE_SUPABASE_URL` | string | `https://<ref>.supabase.co` | Supabase project URL for authentication and asset storage. |
| `VITE_SUPABASE_ANON_KEY` | string | `<ANON_KEY>` | Supabase anonymous public key. |

> [!IMPORTANT]
> Vite only exposes variables prefixed with `VITE_` to client-side bundles. Never place backend secrets or private keys in the frontend configuration.

---

## 5. Environment Variables — Mobile (Flutter)

**Location:** `mobile/.env` (Passed via `--dart-define-from-file=.env`)

| Variable | Type | Description |
|---|---|---|
| `SUPABASE_URL` | string | Supabase project URL used by `RemoteConfigService` to query `public.app_config`. |
| `SUPABASE_ANON_KEY` | string | Supabase public anonymous API key (read-only access governed by RLS). |

> [!NOTE]
> The mobile client dynamically resolves `api_base_url` from the Supabase `app_config` table at runtime, caching the endpoint locally in SharedPreferences for offline resiliency.

---

## 6. `model_registry.json`

**Location:** `backend/model_registry.json`

Tracks active model versions, validation accuracies, and promotion history:

```json
{
  "crop_identifier": {
    "current_version": "v1.0",
    "versions": [
      {
        "version": "v1.0",
        "checkpoint_path": "models/crop_identifier_v1.pth",
        "val_acc": 0.9948,
        "promoted_at": "2026-01-15"
      }
    ]
  },
  "tomato_disease": {
    "current_version": "v1.0",
    "versions": [
      {
        "version": "v1.0",
        "checkpoint_path": "models/disease_Tomato.pth",
        "val_acc": 0.9080,
        "promoted_at": "2026-02-01"
      }
    ]
  }
}
```

---

## 7. Dynamic Configuration & Hot Reload

The platform supports live threshold updates without application downtime or service restarts.

### Hot-Reloadable Fields

| Parameter | Admin API Payload Field | `config.yaml` Mapping | Upstash Redis Key |
|---|---|---|---|
| Crop Confidence Cutoff | `crop_routing_threshold` | `thresholds.crop_confidence` | `sf:config:thresholds` |
| Disease Escalation Cutoff | `expert_escalation_cutoff` | `thresholds.disease_confidence` | `sf:config:thresholds` |

### Synchronization Flow

```
Admin Client
   │
   │  PUT /admin/config
   │  { "crop_routing_threshold": 0.75, "expert_escalation_cutoff": 0.70 }
   ▼
FastAPI API Gateway
   ├─ Updates in-memory settings and rewrites config.yaml
   └─ Writes updated JSON to Upstash Redis REST under key "sf:config:thresholds"
         │
         ▼
All Distributed Backend & AI Service Instances
(Query sf:config:thresholds on subsequent inferences with zero downtime)
```

---

*AI-Powered Smart Farming — Configuration Reference*  
*Lead Developer & Model Architect: Manthan Kuvadiya*  
*Monorepo Repository: [github.com/manthan2876/Smart-Farming](https://github.com/manthan2876/Smart-Farming)*  
*Hugging Face Space: [Maharsh8805/smart-farming-ai](https://huggingface.co/spaces/Maharsh8805/smart-farming-ai)*  
*Last Updated: 19 October 2026*
