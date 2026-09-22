# Configuration Reference — AI-Powered Smart Farming

This document is the single source of truth for all runtime configuration in the Smart Farming platform. It covers the ML pipeline config file, backend and frontend environment variables, the model registry, and hot-reload behavior.

---

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
> When `STORAGE_BACKEND=s3`, these directories are used as temporary local staging areas before upload to S3. See [`STORAGE_BACKEND`](#storage-1) in the environment variables section.

---

## 2. Environment Variables — Backend

**Location:** `.env` or `backend/.env`

> [!CAUTION]
> Never commit `.env` files to version control. Values marked **CHANGE IN PRODUCTION** must be replaced with strong, randomly generated secrets before any public or production deployment.

### Authentication & Security

| Variable | Type | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | string | `dev-secret-key-change-me` | **⚠ CHANGE IN PRODUCTION.** Primary JWT signing key. |
| `JWT_SECRET_KEY` | string | `dev-secret-key-change-me` | Alias for `SECRET_KEY`. Both must be set to the same value. |
| `ALGORITHM` | string | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `30` | Access token lifetime in minutes. |
| `ENVIRONMENT` | string | `development` | Set to `production` to enable security guards (disables debug auth, enforces HTTPS redirects, etc.). |
| `DEBUG` | bool | `True` | When `True`, enables the `X-User-ID` header fallback authentication (development only). **Must be `False` in production.** |
| `CORS_ORIGINS` | string | `http://localhost:5173,...` | Comma-separated list of allowed CORS origins. |

### Database

| Variable | Type | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | string | `sqlite:///./dev_database.db` | SQLAlchemy database URL. Use `postgresql://user:pass@host/db` for staging and production. |

### Redis & Job Queue

| Variable | Type | Default | Description |
|---|---|---|---|
| `REDIS_URL` | string | `redis://127.0.0.1:6379` | Redis connection URL used by the ARQ job queue and the config hot-reload pub/sub channel. |
| `REQUIRE_REDIS` | bool | `False` | If `True`, the application **fails to start** when Redis is unreachable. Recommended `True` in production. |

### File Uploads

| Variable | Type | Default | Description |
|---|---|---|---|
| `UPLOAD_MAX_BYTES` | int | `10485760` | Maximum upload file size in bytes. Default is 10 MB (10 × 1024²). |

### ML Inference Thresholds (Fallback)

These are used as fallback values only when `config.yaml` cannot be loaded. The `config.yaml` values take precedence.

| Variable | Type | Default | Description |
|---|---|---|---|
| `CROP_CONFIDENCE_THRESHOLD` | float | `0.7` | Fallback for `thresholds.crop_confidence`. |
| `DISEASE_CONFIDENCE_THRESHOLD` | float | `0.7` | Fallback for `thresholds.disease_confidence`. |

### External APIs

| Variable | Type | Default | Description |
|---|---|---|---|
| `GOOGLE_TTS_API_KEY` | string | `""` | Google Cloud Text-to-Speech API key. Leave empty to disable TTS features. |
| `GOOGLE_TRANSLATION_API_KEY` | string | `""` | Google Cloud Translation API key. Leave empty to disable translation features. |
| `HF_TOKEN` | string | **required** | HuggingFace API token. Must have inference provider permissions. The app will not function without this. |

### Storage

| Variable | Type | Default | Description |
|---|---|---|---|
| `STORAGE_BACKEND` | string | `local` | Storage driver. `local` uses the filesystem paths from `config.yaml`. `s3` uploads to AWS S3 or a MinIO-compatible endpoint. |
| `AWS_ACCESS_KEY_ID` | string | — | AWS / MinIO access key. Required when `STORAGE_BACKEND=s3`. |
| `AWS_SECRET_ACCESS_KEY` | string | — | AWS / MinIO secret key. Required when `STORAGE_BACKEND=s3`. |
| `AWS_REGION` | string | `us-east-1` | AWS region for the S3 bucket. |
| `AWS_S3_BUCKET` | string | `smart-farming-data-...` | S3 bucket name. Required when `STORAGE_BACKEND=s3`. |
| `S3_PRESIGNED_EXPIRY_SECONDS` | int | `900` | Expiry duration (in seconds) for generated presigned S3 URLs. Default is 15 minutes. |

---

## 3. Environment Variables — Frontend

**Location:** `frontend/.env`

| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Base URL of the backend API, used by all frontend API calls. Change to the deployed backend URL in staging/production. | `http://localhost:8000` |

> [!NOTE]
> Vite only exposes variables prefixed with `VITE_` to client-side code. Do not store secrets in `frontend/.env`.

---

## 4. `model_registry.json`

**Location:** `backend/model_registry.json`

Tracks promoted model versions for each task. This file is **managed automatically** by the `POST /admin/models/promote` endpoint — do not edit it manually unless you understand the promotion workflow.

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
Client
  │
  │  PUT /admin/config
  │  { "crop_routing_threshold": 0.65, "expert_escalation_cutoff": 0.75 }
  ▼
API Process
  ├─ Writes new values to config.yaml
  ├─ Calls pipeline.reload_config()  ← reloads in the API worker
  └─ Publishes event to Redis channel: config_reload_events
                          │
                          ▼
              ARQ Worker Processes
                ├─ Subscribe to config_reload_events
                └─ Each worker calls pipeline.reload_config()
```

> [!IMPORTANT]
> The `PUT /admin/config` endpoint requires admin-level authentication. Unauthenticated or non-admin requests will be rejected with `403 Forbidden`.

> [!WARNING]
> If Redis is unavailable during a hot-reload, the API process will still update its own in-memory config and write to `config.yaml`, but **worker processes will not be notified**. Workers will pick up the new config only on their next restart. Set `REQUIRE_REDIS=True` in production to prevent this split-brain scenario.

---

*Last updated: 2026-09-22*
