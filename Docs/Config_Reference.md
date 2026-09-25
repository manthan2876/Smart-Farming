# Configuration Reference — AI-Powered Smart Farming

**Project:** AI-Powered Smart Farming  
**Version:** 1.0  
**Date:** September 2026  
**Status:** Active / Production Reference  

---

This document is the single source of truth for all runtime configuration in the Smart Farming platform. It covers the ML pipeline config file, backend and frontend environment variables, the model registry, and hot-reload behavior.

## Table of Contents

1. [config.yaml — ML Pipeline](#1-configyaml--ml-pipeline)
   - [Full File](#full-file)
   - [Field Reference](#field-reference)
2. [Environment Variables — Backend](#2-environment-variables--backend)
3. [Environment Variables — Frontend](#3-environment-variables--frontend)
4. [model_registry.json](#4-model_registryjson)
5. [Hot Reload](#5-hot-reload)

---

## 1. `config.yaml` — ML Pipeline

**Location:** `backend/config.yaml`

Controls model paths, inference thresholds, and storage directories for the ML pipeline. All relative paths are resolved from the `backend/` directory.

> [!TIP]
> The `thresholds` section can be updated at runtime without a server restart. See [Hot Reload](#5-hot-reload) for details.

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
  crop_confidence: 0.7
  disease_confidence: 0.7
  blur_var_threshold: 50.0
  min_brightness: 40.0
  max_brightness: 240.0
storage:
  upload_dir: data/uploads/
  processed_dir: data/processed/
```

---

### Field Reference

#### `models.crop_identifier`

| Field | Type | Default | Description |
|---|---|---|---|
| `path` | string | `models/crop_identifier_v1.pth` | Path (relative to `backend/`) to the crop identifier PyTorch checkpoint (`.pth`). |
| `labels` | string | `models/crop_identifier_labels.json` | Path to JSON file mapping index → class name for the crop identifier. |
| `arch` | string | `efficientnet_b0` | EfficientNet variant string passed to `timm`. |

---

#### `models.disease_models.{CropName}`

One entry per supported crop. The key **must exactly match** the class label output by the crop identifier model (case-sensitive).

| Field | Type | Default | Description |
|---|---|---|---|
| `path` | string | — | Path (relative to `backend/`) to the per-crop disease classifier checkpoint (`.pth`). |
| `labels` | string | — | Path to the per-crop class label JSON file (index → disease name). |
| `arch` | string | `efficientnet_b2` | EfficientNet variant string passed to `timm`. |

**Supported crop keys:**

| Key | Model File |
|---|---|
| `Cotton` | `models/disease_Cotton.pth` |
| `Groundnut` | `models/disease_Groundnut.pth` |
| `Pepper_Bell` | `models/disease_Pepper_Bell.pth` |
| `Potato` | `models/disease_Potato.pth` |
| `Tomato` | `models/disease_Tomato.pth` |

> [!IMPORTANT]
> Adding a new crop requires: (1) adding an entry under `disease_models` with the exact label string, (2) placing the checkpoint and label JSON at the specified paths, and (3) **restarting the server** — model path changes are not hot-reloadable.

---

#### `models.pest_classifier`

| Field | Type | Default | Description |
|---|---|---|---|
| `path` | string | `models/pest_classifier/pest_classifier.pt` | Path to the YOLOv8 pest classifier weights (`.pt`). If the file is missing at startup, pest detection is **skipped gracefully** — the pipeline continues without raising an error. |

---

#### `thresholds`

> [!NOTE]
> `crop_confidence` and `disease_confidence` are hot-reloadable via `PUT /admin/config`. The other threshold fields require a server restart.

| Field | Type | Default | Range | Description |
|---|---|---|---|---|
| `crop_confidence` | float | `0.7` | 0–1 | Minimum confidence for a crop prediction to be trusted. Below this value, the crop is flagged as `unsupported_crop` and the request is escalated. Mapped to `crop_routing_threshold` in the Admin API. |
| `disease_confidence` | float | `0.7` | 0–1 | Minimum confidence for a disease prediction. Below this value, the result is escalated to expert review (`escalation_required: true`). Mapped to `expert_escalation_cutoff` in the Admin API. |
| `blur_var_threshold` | float | `50.0` | > 0 | Laplacian variance threshold for blur detection. Images scoring below this value are rejected with status `failed_blur`. |
| `min_brightness` | float | `40.0` | 0–255 | Minimum HSV V-channel mean. Images below this value are rejected with status `failed_lighting` (too dark). |
| `max_brightness` | float | `240.0` | 0–255 | Maximum HSV V-channel mean. Images above this value are rejected with status `failed_lighting` (overexposed). |

---

#### `storage`

| Field | Type | Default | Description |
|---|---|---|---|
| `upload_dir` | string | `data/uploads/` | Directory (relative to `backend/`) where raw uploaded images are stored. |
| `processed_dir` | string | `data/processed/` | Directory (relative to `backend/`) for OpenCV-processed images and Grad-CAM heatmaps. |

> [!NOTE]
> When `STORAGE_BACKEND=s3` or `STORAGE_BACKEND=gcs`, these directories are used as temporary local staging areas before upload. See [`STORAGE_BACKEND`](#storage) in the environment variables section.

---

## 2. Environment Variables — Backend

**Location:** `.env` or `backend/.env` (or Google Cloud Run environment variables)

> [!CAUTION]
> Never commit `.env` files to version control. Values marked **CHANGE IN PRODUCTION** must be replaced with strong, randomly generated secrets before any public or production deployment.

### Authentication & Security

| Variable | Type | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | string | `dev-secret-key-change-me` | **⚠ CHANGE IN PRODUCTION.** Primary JWT signing key. |
| `JWT_SECRET_KEY` | string | `dev-secret-key-change-me` | Alias for `SECRET_KEY`. Both can be set to the same value. |
| `ALGORITHM` | string | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `30` | Access token lifetime in minutes. |
| `ENVIRONMENT` | string | `development` | Set to `production` in live deployments to enforce security policies and production origins. |
| `DEBUG` | bool | `True` | When `True`, enables `X-User-ID` header fallback authentication for local development. **Must be `False` in production.** |
| `CORS_ORIGINS` | string | `http://localhost:5173,...` | Comma-separated list of allowed frontend origins (e.g. `https://smart-farming-dashboard.vercel.app,http://localhost:5173`). |

### Database

| Variable | Type | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | string | `sqlite:///./dev_database.db` | SQLAlchemy connection DSN. For Cloud Run / production, set to Supabase managed PostgreSQL (e.g., `postgresql://postgres.<PROJECT_REF>:<DB_PASSWORD>@aws-0-<REGION>.pooler.supabase.com:5432/postgres?sslmode=require`). Normalized automatically in `session.py` to `postgresql+psycopg2://`. |

### Model Inference Server (Server 2)

Used in decoupled microservices architectures (such as Google Cloud Run):

| Variable | Type | Default | Description |
|---|---|---|---|
| `MODEL_SERVER_URL` | string | `http://127.0.0.1:8001` | URL of the dedicated PyTorch inference microservice (Cloud Run Service #2, e.g. `https://inference-service-<id>.<region>.run.app`). When configured, the main backend forwards image prediction requests to this service over HTTP/HTTPS with GCP OIDC authentication. |
| `MODEL_SERVER_TIMEOUT` | int | `60` | HTTP request timeout in seconds when calling the inference server. |

### Redis & Job Queue

| Variable | Type | Default | Description |
|---|---|---|---|
| `UPSTASH_REDIS_REST_URL` | string | `None` | Upstash Serverless Redis REST endpoint URL (e.g. `https://<db-id>.upstash.io`). Powers high-speed translation caching, 30-min weather response caching, prediction deduplication, and dynamic admin threshold sync. 100% serverless over HTTPS. |
| `UPSTASH_REDIS_REST_TOKEN` | string | `None` | Upstash Serverless Redis REST full-access bearer token. |
| `REDIS_URL` | string | `redis://127.0.0.1:6379` | Legacy Redis connection URL used by the local Docker ARQ job queue. |
| `REQUIRE_REDIS` | bool | `False` | Determines whether the backend requires local TCP Redis to run.<br>• **Cloud Run Production:** Must be **`False`**. Persistent ARQ polling workers prevent scale-to-zero and exhaust monthly free-tier quotas. With `REQUIRE_REDIS=False`, predictions run synchronously via HTTP to the inference service, allowing Cloud Run to scale to **0 instances** when idle.<br>• **Docker Compose / VM:** Can be set to `True` when running persistent background ARQ worker containers. |

### File Uploads & Local Paths

| Variable | Type | Default | Description |
|---|---|---|---|
| `UPLOAD_MAX_BYTES` | int | `10485760` | Maximum upload file size in bytes. Default is 10 MB (10 × 1024²). |
| `BACKEND_ROOT` | Path | Auto | Root directory of the backend repository. |
| `CONFIG_PATH` | Path | `config.yaml` | Path to pipeline `config.yaml`. |
| `DATA_ROOT` | Path | `data/` | Root directory for local file storage. |

### ML Inference Thresholds (Fallback)

These are used as fallback values only when `config.yaml` cannot be loaded. The `config.yaml` values take precedence.

| Variable | Type | Default | Description |
|---|---|---|---|
| `CROP_CONFIDENCE_THRESHOLD` | float | `0.7` | Fallback for `thresholds.crop_confidence`. |
| `DISEASE_CONFIDENCE_THRESHOLD` | float | `0.7` | Fallback for `thresholds.disease_confidence`. |

### External AI & Cloud Services

| Variable | Type | Default | Description |
|---|---|---|---|
| `HF_TOKEN` | string | **required** | HuggingFace user access token with read permissions. Used for the Qwen3-4B Agronomist LLM recommendation engine. |
| `OPENWEATHER_API` | string | `""` | OpenWeatherMap API key used to enrich disease diagnostics with live ambient temperature, humidity, and rainfall. |
| `GEMINI_API_KEY` | string | `""` | Google Gemini API key used for multimodal agronomist advisory fallback and multilingual translations. |
| `GOOGLE_TTS_API_KEY` | string | `""` | Google Cloud Text-to-Speech API key for Gujarati, Hindi, and English voice synthesis. |
| `GOOGLE_TRANSLATION_API_KEY` | string | `""` | Google Cloud Translation API key for dynamic advisory localization. |

### Object Storage (AWS S3 & Google Cloud Storage)

The backend provides a unified, S3-compatible storage abstraction (`storage.py`) supporting local disk, Google Cloud Storage (GCS), and AWS S3 / MinIO.

| Variable | Type | Default | Description |
|---|---|---|---|
| `STORAGE_BACKEND` | string | `local` | Storage driver. Options: `local`, `gcs`, or `s3`. |
| `AWS_ACCESS_KEY_ID` | string | — | Access key ID. For Google Cloud Storage, use the **GCS HMAC Access ID** (format: `<YOUR_GCS_HMAC_ACCESS_KEY>`). |
| `AWS_SECRET_ACCESS_KEY` | string | — | Secret access key. For Google Cloud Storage, use the **GCS HMAC Secret**. |
| `AWS_REGION` | string | `us-east-1` | AWS region (or `auto` / `us-central1` for GCS). |
| `AWS_S3_BUCKET` / `GCS_BUCKET` | string | `smart-farming-data` | Target bucket name. |
| `AWS_ENDPOINT_URL` | string | — | S3 endpoint override. For Google Cloud Storage, set to `https://storage.googleapis.com`. |
| `S3_PRESIGNED_EXPIRY_SECONDS` | int | `900` | Expiration lifetime in seconds for signed download URLs (default: 15 minutes). |

> [!NOTE]
> When `STORAGE_BACKEND=gcs` or `AWS_ENDPOINT_URL` contains `storage.googleapis.com`, the storage client automatically enforces `signature_version="s3"` (SigV2) to match Google Cloud Storage XML API interoperability specifications.

---

## 3. Environment Variables — Frontend

**Location:** `frontend/.env` (Local) or **Vercel Project Environment Variables** (Production)

| Variable | Type | Example / Default | Description |
|---|---|---|---|
| `VITE_API_URL` | string | `https://smart-farming-backend-xxx.run.app` | Base URL of the backend API, consumed by Axios client in `frontend/src/api/client.ts`. Default for local dev: `http://localhost:8000`. |
| `VITE_GOOGLE_MAPS_API_KEY` | string | `<YOUR_GOOGLE_MAPS_API_KEY>` | Google Maps JavaScript API key used for farm boundary geo-tagging, satellite field views, and soil moisture overlays in `FarmSettingsPage.tsx`. |
| `VITE_GOOGLE_MAPS_MAP_ID` | string | `<YOUR_MAP_ID>` | Map ID for vector styling in Google Maps JavaScript API. |

> [!NOTE]
> Vite only exposes variables prefixed with `VITE_` to client-side bundles. Secrets must never be stored in frontend environment variables.

---

## 4. `model_registry.json`

**Location:** `backend/model_registry.json`

Tracks promoted model versions, checkpoints, and validation metrics for each task.

### Decoupled Microservices Behavior (Cloud Run)

In production, heavy model weights (`.pth`, `.pt`) are housed inside Cloud Run Service #2 (`inference-service`), not the main backend container.
- When `MODEL_SERVER_URL` is set, the Model Registry endpoint (`GET /admin/models/health`) recognizes that inference is delegated to the remote service.
- It validates healthy connectivity and displays active model versions, validation accuracies, and promotion history loaded directly from `model_registry.json`.

### Structure

```json
{
  "tomato_disease": {
    "current_version": "v1.0",
    "versions": [
      {
        "version": "v1.0",
        "checkpoint_path": "models/disease_Tomato.pth",
        "val_acc": 0.908,
        "promoted_at": "2025-01-01"
      }
    ]
  }
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `{task_key}` | object | Top-level key identifying the model task (e.g., `tomato_disease`, `potato_disease`). |
| `current_version` | string | The version string currently active in production for this task. |
| `versions` | array | Ordered list of all promoted versions (most recent last). |
| `versions[].version` | string | Semantic version string (e.g., `v1.0`, `v2.1`). |
| `versions[].checkpoint_path` | string | Path to the model checkpoint (relative to `backend/`). |
| `versions[].val_acc` | float | Validation accuracy recorded at promotion time (0–1). |
| `versions[].promoted_at` | string | ISO 8601 date when this version was promoted. |

---

## 5. Hot Reload

The platform supports partial runtime configuration updates without a full server restart.

### What Can Be Hot-Reloaded

| Config Field | `config.yaml` key | Admin API param |
|---|---|---|
| Crop confidence threshold | `thresholds.crop_confidence` | `crop_routing_threshold` |
| Disease confidence threshold | `thresholds.disease_confidence` | `expert_escalation_cutoff` |

### What Requires a Server Restart

- All `models.*` fields (model paths, label paths, architectures)
- All `storage.*` fields
- `thresholds.blur_var_threshold`, `thresholds.min_brightness`, `thresholds.max_brightness`

### Hot-Reload Flow

```
Admin Client
  │
  │  PUT /admin/config
  │  { "crop_routing_threshold": 0.65, "expert_escalation_cutoff": 0.75 }
  ▼
API Process
  ├─ Writes new values to config.yaml & in-memory pipeline state
  ├─ Sets "sf:config:thresholds" in Upstash Serverless Redis REST
  │     │
  │     ▼
  │   All Cloud Run Backend & Inference Instances
  │   (Read live "sf:config:thresholds" on next inference request)
  │
  └─ Publishes event to Redis channel: config_reload_events
        │
        ▼
    ARQ Worker Processes (Local / Docker Compose only)
      ├─ Subscribed to config_reload_events
      └─ Each worker calls pipeline.reload_config()
```

> [!IMPORTANT]
> The `PUT /admin/config` endpoint requires admin-level authentication. Unauthenticated or non-admin requests will be rejected with `403 Forbidden`.

> [!NOTE]
> In serverless Cloud Run deployments (`REQUIRE_REDIS=False`), threshold updates are persisted to Upstash Redis REST under key `sf:config:thresholds`. All autoscaled backend and inference instances dynamically read this key, ensuring instantaneous system-wide synchronization without requiring worker polling daemons or container restarts.

---

*AI-Powered Smart Farming — Documentation*  
*Last Updated: September 2026*
