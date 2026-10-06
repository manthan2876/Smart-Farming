# Smart Farming Functionality Status

**Project:** AI-Powered Smart Farming  
**Version:** 2.0  
**Date:** 06 October 2026  
**Status:** Active / Production Reference  

---

**Scope:** Backend, web frontend, mobile client, model/inference services, scheduled jobs, and MLOps features currently present in this repository.

This document describes what the project currently does, how complete each capability is, and what should be improved next. The status is based on the code that exists today, not only on the roadmap documents.

## Status Legend

| Status | Meaning |
|---|---|
| Implemented | The feature works end-to-end in the production code path; production hardening may still be needed. |
| Mostly implemented | The main path works, but at least one important edge case, integration concern, or production gap remains. |
| Partial | Some functionality exists, but the full user journey or backend contract is incomplete. |
| Scaffolded | A screen, model, route, or service exists, but is mostly a prototype or is not connected to the live system. |
| Broken or disconnected | Code exists, but the path currently fails or is not used by the active application flow. |
| Planned or missing | Described by the roadmap/specification but not yet present in the code. |

---

## Executive Summary

The core AI diagnosis pipeline supports two execution modes controlled by `REQUIRE_REDIS`:

**Default / Serverless mode (`REQUIRE_REDIS=False`):**

1. The user uploads a JPEG, PNG, or WebP leaf image via `POST /predict`.
2. The backend validates the content-type and extension, verifies the file bytes with PIL `Image.verify()` (magic-byte check), hashes the image, and checks the Upstash Redis REST dedup cache (`sf:dedup:{hash}`, 24 h TTL). A cached completed result is returned immediately.
3. The image is saved to the active storage backend (local disk + GCS in production).
4. `run_pipeline()` is called **synchronously** in the request: calls the model service (Cloud Run Service #2) via HTTPS with OIDC auth, runs the 8-stage pipeline (preprocessing → crop identification → decision routing → disease classification → severity estimation → pest detection → weather → recommendation), then persists to PostgreSQL.
5. A RAG retriever injects verified agronomic safety guidelines (pesticide bans, PHI constraints) into the LLM prompt.
6. The completed result is saved to Upstash Redis REST dedup cache and returned immediately in the same HTTP response. `FastAPI BackgroundTasks` pre-translates the recommendation into Hindi and Gujarati, storing them in the `entity_translations` table for instant future lookups.
7. If disease or crop confidence is below the configured threshold, `ensure_expert_review()` automatically creates a pending expert-review record.

**ARQ worker mode (`REQUIRE_REDIS=True`):**

1–3. Same upload, validation, and storage steps as above.
4. The prediction job is enqueued into ARQ; a placeholder DB record and `prediction_id` are returned immediately (202-style response).
5. The ARQ worker runs the pipeline; each stage publishes a Redis pub/sub event for WebSocket streaming. The `POST /predict` response is a placeholder with `status.pipeline: "processing"`.

**Scheduled crons (production):** QStash (`QSTASH_TOKEN`, `QSTASH_URL`) delivers webhook calls to `/api/v1/internal-cron/weather-risk` (verified with `CRON_SECRET`) for proactive weather-risk alert generation.

The mobile application has been fully rebuilt from a prototype to a working farmer-facing client: full JWT authentication, farm/plot management, weather with TTS, alerts, feedback, expert-review escalation, on-demand translation, and a cloud TTS service with on-device fallback — all orchestrated by a 5-screen bottom-navigation shell (`FarmerShell`).

The web frontend is a functional multi-role application with a shared typed API client, token refresh, weather with TTS, admin dashboard with drift metrics and model health, and an operational MLOps dataset export that works end-to-end.

**Key remaining gaps:**

- ARQ worker runs in a separate OS process; `pipeline.reload_config()` only affects the FastAPI process. Model promotions require a worker restart to take effect.
- Login rate limiting uses a hard-coded development secret key; the `X-User-ID` identity fallback is still active in production code paths.
- `refresh_token` cookie is set with `secure=False`; must be changed before HTTPS deployment.
- Mobile offline queue uses `SharedPreferences` for raw image bytes — not durable for large payloads; `plot_id` is not preserved in the queue item.
- Test coverage is limited. Admin metrics, expert review, farm geometry, RAG, model registry, translation, and mobile parsing have no automated tests.

---

## 1. Core AI Diagnosis Pipeline

### 1.1 Image upload and request validation

**Status: Mostly implemented**

**What works:**

- `POST /predict` accepts JPEG, PNG, and WebP via multipart form upload.
- `settings.UPLOAD_MAX_BYTES` enforces a server-side file size limit (default 10 MB).
- **File bytes are independently verified:** PIL `Image.verify()` (magic-byte / header decode check) runs before the file is persisted. Malformed files with a valid extension are rejected with `400 Bad Request`.
- The file content is SHA-256 hashed; identical image bytes reuse the same filename on disk.
- A completed prediction for the same file and same plot is returned from the Upstash Redis REST dedup cache (24 h TTL) without re-running the pipeline.
- Files are saved under `backend/data/uploads` via `core/paths.py`; all path logic runs through `resolve_storage_path()`, which prevents path traversal outside the configured storage root.
- In `REQUIRE_REDIS=False` mode (default), a synchronous model-service call runs the full pipeline within the request and returns the completed result immediately. In `REQUIRE_REDIS=True` (ARQ) mode, a quality pre-check runs synchronously before enqueuing; user-readable rejection reasons are returned for `failed_blur`, `failed_lighting`, and `failed_no_leaf`.
- Content-type headers are validated (`_ALLOWED_CONTENT_TYPES`); extension-based fallback handles clients that omit content-type.

**Known gaps:**

- No idempotency key for two simultaneous identical requests arriving in parallel (race condition window between dedup check and prediction insert).
- Default lat/lon fallback is Warsaw (52.2297, 21.0122) — a dev artifact; unset clients produce geographically incorrect weather data.
- Upload metadata such as device model, capture time, or GPS EXIF is not extracted or stored.

**Relevant code:**

- [predict.py](../backend/src/app/api/endpoints/predict.py) — upload handler, PIL validation, dedup cache, sync pipeline or ARQ enqueue
- [preprocessing/service.py](../backend/src/app/services/preprocessing/service.py) — blur/lighting/leaf detection
- [core/paths.py](../backend/src/app/core/paths.py) — path resolution and traversal protection
- [core/config.py](../backend/src/app/core/config.py) — upload size and storage roots

**What to improve:**

- Add idempotency protection for concurrent duplicate uploads (dedup check → insert race window).
- Resolve Warsaw default lat/lon — require clients to send location or improve GPS fallback.
- Surface content-type rejection as a clear user-facing message on the scan page.
- Add tests for oversized files, wrong content-type, duplicate concurrent uploads.

---

### 1.2 OpenCV preprocessing and leaf quality checks

**Status: Implemented**

**What works:**

- Reads the uploaded image with OpenCV.
- Calculates Laplacian-variance sharpness (blur score) and mean-pixel brightness.
- Runs HSV-based leaf isolation to detect a leaf and segment the region of interest.
- Applies image enhancement and saves a processed image.
- Resizes and converts the image for downstream model inference.
- Rejects images that fail quality rules before any ML model stage runs.
- Returns structured, user-readable rejection messages including the actual and expected values:
  - `failed_blur`: sharpness score vs. required threshold.
  - `failed_lighting`: brightness vs. acceptable range.
  - `failed_no_leaf`: no crop leaf detected in frame.

**Known gaps:**

- No labeled test set for calibrating thresholds against real farmer photos.
- No separate heatmap or attribution artifact is produced; the processed image is the only artifact.
- Decoder/memory failures from malformed images are not explicitly handled.

**Relevant code:**

- [preprocessing/service.py](../backend/src/app/services/preprocessing/service.py)
- [preprocessing/leaf_isolator.py](../backend/src/app/services/preprocessing/leaf_isolator.py)

> [!NOTE]
> Quality thresholds (`blur_var_threshold`, `min_brightness`, `max_brightness`) are already configurable in [`config.yaml`](../backend/config.yaml) and can be tuned without code changes. Dynamic runtime overrides are also supported via Upstash Redis REST (`sf:config:thresholds`).

**What to improve:**

- Validate threshold values against a representative labeled test set.
- Add protective handling for malformed, truncated, or adversarial images.
- Add regression tests covering good, blurry, dark, bright, and no-leaf images.

---

### 1.3 Crop identification

**Status: Implemented**

**What works:**

- Runs the configured EfficientNet-B0 crop classifier against the processed leaf image (`crop_identifier_v1.pth`).
- Returns crop label, confidence, and top-k probability information.
- Supported crops: Cotton, Groundnut, Pepper Bell, Potato, Tomato.
- Model file path and labels file are resolved at startup; model name and version are included in the `provenance` block of every prediction result.
- Confidence is stored in `prediction.crop_conf` for drift monitoring and expert escalation decisions.
- The confidence routing threshold (`thresholds.crop_confidence`, default `0.7`) is read from [`config.yaml`](../backend/config.yaml); predictions below this threshold trigger automatic expert escalation.

**Known gaps:**

- A crop outside the supported label set produces a low-confidence output; there is no explicit `unsupported_crop` result or user-facing guidance.
- No calibration validation between the model's reported confidence and real-world accuracy.

**Relevant code:**

- [crop_identifier/predictor.py](../backend/src/app/services/crop_identifier/predictor.py)
- [config.yaml](../backend/config.yaml)
- [models/crop_identifier_v1.pth](../models/crop_identifier_v1.pth)

**What to improve:**

- Return a clear `unsupported_crop` state instead of passing a low-confidence unknown crop to subsequent stages.
- Expose crop confidence uncertainty to the user.
- Add unit tests for missing model file, invalid labels file, CPU-only inference, and confidence edge cases.

---

### 1.4 Crop-specific disease routing

**Status: Implemented**

**What works:**

- `decision_engine/router.py` reads the detected crop and selects the crop-specific disease model from `config.yaml`.
- Records the selected model name in `context["disease"]["model_used"]`, which appears in the prediction result and provenance block.
- Handles the case where no crop-specific model is configured.

**Known gaps:**

- The crop-confidence routing threshold is read from `thresholds.crop_confidence` in the config but is not consistently used as a gate in the router to skip disease classification for truly low-confidence crops.

**Relevant code:**

- [decision_engine/router.py](../backend/src/app/services/decision_engine/router.py)
- [config.yaml](../backend/config.yaml)

**What to improve:**

- Enforce the documented crop-confidence routing threshold: skip disease classification and return a "too uncertain to diagnose" result when confidence is below the threshold.
- Add tests for unknown crops, missing disease model config, and routing to a fallback model.

---

### 1.5 Disease classification

**Status: Implemented**

**What works:**

- Loads the crop-specific EfficientNet-B2 disease classifier (one model per supported crop, see [`config.yaml`](../backend/config.yaml)).
- Returns disease label, confidence, probability distribution, and model metadata.
- Uses the preprocessed leaf image from the shared context.
- Confidence is stored in `prediction.disease_conf` for drift monitoring and automatic expert escalation.
- Predictions below `thresholds.disease_confidence` (default `0.7`, configurable in `config.yaml`) automatically trigger expert review.
- Model name, version, and file are recorded in the `provenance` block.

**Known gaps:**

- No calibrated confidence calibration or uncertainty quantification.
- Model loading is done at startup; the running process must be restarted (or `reload_config()` called) to switch to a promoted model in the same process.

**Relevant code:**

- [disease_classifier/predictor.py](../backend/src/app/services/disease_classifier/predictor.py)

**What to improve:**

- Add per-crop precision/recall/F1 monitoring from expert review data.
- Add tests for missing weights, incompatible label files, and low-confidence predictions.

---

### 1.6 Severity estimation

**Status: Partial**

**What works:**

- Estimates the fraction of the leaf affected using HSV-based color segmentation contours (OpenCV heuristic).
- Returns `percent` (0–100) and a severity `bucket` (e.g., Low, Moderate, High, Critical).
- Produces an overlay visualization artifact.
- Severity percent is stored in `prediction.severity_pct`.

**Known gaps:**

- The approach is a color-based heuristic, not a learned segmentation model; results are sensitive to leaf color, lighting, and disease presentation.
- Thresholds and bucket definitions are embedded in code.
- No ground-truth evaluation has been published for this component.

**Relevant code:**

- [severity/estimator.py](../backend/src/app/services/severity/estimator.py)

**What to improve:**

- Validate estimates against manually segmented ground-truth masks.
- Make severity thresholds crop- and disease-aware where the product specification requires it.
- Return a quality flag when segmentation is unreliable.
- Add regression tests using representative healthy and diseased leaf images.

---

### 1.7 Pest detection

**Status: Partial / optional**

**What works:**

- Supports a configured YOLO classification model for pest detection (`models/pest_classifier/pest_classifier.pt`, as set in [`config.yaml`](../backend/config.yaml)).
- Returns ranked pest probabilities and labels when the model is available.
- The pipeline continues gracefully when the pest model is absent or unavailable.
- Model availability and name are recorded in the `provenance` block.
- Pest labels are stored in the prediction result and exposed to mobile clients (displayed in `ProcessingSheet` and `ResultDetailSheet`).

**Known gaps:**

- No bounding-box localization (classification only, not detection).
- No explicit distinction in the API response between "no pest detected" and "pest model unavailable."
- Pest model health is not exposed in the model health check endpoint.

**Relevant code:**

- [pest_detector/predictor.py](../backend/src/app/services/pest_detector/predictor.py)
- [models/pest_classifier](../models/pest_classifier)

**What to improve:**

- Add a status field distinguishing `no_pest_detected` from `model_unavailable`.
- Include pest model status in `GET /admin/models/health`.
- Add tests for missing weights, corrupt weights, and low-confidence pest results.

---

### 1.8 Weather data and advisory

**Status: Partial**

**What works:**

- `fetch_weather()` in `weather/service.py` reads `lat`/`lon` from `context["user"]` and calls the OpenWeatherMap REST API (`data/2.5/weather`).
- Returns temperature, feels-like, min/max, humidity, pressure, wind speed/direction, cloudiness, and weather condition/description.
- External failures set `is_degraded=True` and mark the weather stage as failed without aborting the prediction pipeline.
- Weather provider status and degraded flag are included in the `provenance` block.
- Weather data is injected into the pipeline context and used by the LLM recommendation prompt in subsequent stages.
- The `GET /weather` endpoint resolves coordinates from request parameters or falls back to the farmer's registered farm in profile (`user.farm.latitude`, `user.farm.longitude`); rejects with HTTP 400 if neither is configured.
- Implements two layers of caching: Upstash Redis REST cache (`sf:weather:{cache_key}`) with 10-minute TTL and in-memory cache `_WEATHER_CACHE` (10-minute TTL).
- Generates a farm-specific advisory paragraph via `generate_weather_advisory()` (calling Qwen3-4B with crop history and weather context) with automatic fallback to `_generate_rule_based_advisory()`.
- On-demand advisory translation is supported via `POST /weather/translate` and inline parameter `GET /weather?language=...` using Google Cloud Translation API.

**Known gaps:**

- The pipeline prediction path (`predict.py`) has a hardcoded default fallback to Warsaw coordinates (52.2297, 21.0122) when form parameters are omitted by clients.
- `fetch_weather()` in the standalone pipeline context does not query the Upstash Redis weather cache before making an HTTP request (only the `GET /weather` endpoint checks the Redis cache).
- No 5-day extended forecast visualization in the web frontend.

**Relevant code:**

- [weather/service.py](../backend/src/app/services/weather/service.py)
- [weather.py endpoint](../backend/src/app/api/endpoints/weather.py)
- [weather/proactive.py](../backend/src/app/services/weather/proactive.py)

**What to improve:**

- Unify pipeline weather fetching with the Upstash Redis cache `sf:weather:{lat}:{lon}` to eliminate redundant external API calls during predictions.
- Remove the Warsaw default from `predict.py` form parameters; require coordinates or use the authenticated farmer's registered farm location.
- Add extended 5-day forecast display to the web weather dashboard.
- Add tests for provider timeout, malformed response, and missing API key.

---

### 1.9 AI recommendation with RAG safety guardrails

**Status: Mostly implemented**

**What works:**

- Builds a structured recommendation from crop, disease, severity, weather, location, and pest context.
- Calls `Qwen/Qwen3-4B-Instruct-2507` via the HuggingFace `InferenceClient` with the **nscale** provider when `HF_TOKEN` is configured.
- A lightweight in-process RAG retriever (`services/rag/retriever.py`) performs TF-IDF cosine similarity over a curated knowledge base (6 disease/crop chunks + general safety):
  - Crops covered: **Cotton** (bollworm, leaf curl/bacterial blight), **Tomato** (early & late blight), **Potato** (early & late blight), **Pepper Bell** (anthracnose, bacterial spot), **Groundnut** (tikka leaf spot, rust), and a general pesticide safety chunk.
  - Banned pesticides explicitly listed: Endosulfan, Monocrotophos, Methyl Parathion, Phorate, Carbaryl.
  - PHI constraints, application timing, and organic alternatives are included.
  - The general safety chunk is always appended regardless of relevance score (threshold `0.04`).
  - Retrieved context is injected into the LLM system prompt before every recommendation.
- Returns structured output validated by a `LLMRecommendation` Pydantic model: `immediate_action`, `treatment`, `prevention`, `monitoring`. A `safety_disclaimer` is appended unconditionally post-validation.
- Falls back to a hard-coded rule-based response (not an external service) when the LLM is unavailable or its output fails Pydantic validation. The fallback sets `is_fallback=True` and records the reason.
- Provider, model name, prompt version, fallback status, and fallback reason are recorded in the `provenance` block.

**Known gaps:**

- RAG knowledge base does not currently cover unsupported crops (e.g., Rice, Wheat); a query for an unrecognised crop will fall back to the general safety chunk only.
- No feedback loop from expert corrections back into the knowledge base.
- `retrieve_context_with_ids()` returns retrieved chunk IDs but they are not yet persisted per-prediction for audit purposes.

**Relevant code:**

- [recommendation/service.py](../backend/src/app/services/recommendation/service.py)
- [rag/retriever.py](../backend/src/app/services/rag/retriever.py)

**What to improve:**

- Expand the RAG knowledge base to cover additional crops as the model is extended.
- Persist retrieved chunk IDs per prediction for retrieval auditability.
- Add retrieval correctness tests (query → expected chunks).
- Add integration tests for HF_TOKEN missing, nscale timeout, and Pydantic validation failure paths.

---

### 1.10 Pipeline orchestration and job execution

**Status: Implemented**

**What works:**

- **Synchronous mode (default, `REQUIRE_REDIS=False`):** `predict.py` calls `run_pipeline()` directly. The pipeline executes end-to-end within the HTTP request, results are committed to DB, dedup-cached in Upstash Redis REST (`sf:dedup:{hash}`, 24 h TTL), and the full result is returned in the response. `FastAPI BackgroundTasks` pre-translates the recommendation into Hindi and Gujarati, storing per-field translations in the `entity_translations` table.
- **ARQ worker mode (`REQUIRE_REDIS=True`):** `predict.py` calls `_enqueue_prediction_job()` which submits to ARQ via `arq_pool.enqueue_job()`. If the pool is not initialized, `503` is returned immediately. The ARQ worker (`services/prediction_job.py`) runs all stages, publishing a live Redis pub/sub event and writing an intermediate DB snapshot after each:
  - Stages: `preprocessing`, `crop_identification`, `decision_routing`, `disease_classification`, `severity`, `pest_detection`, `weather`, `recommendation`, `persistence`, final `completed`.
  - Each event includes: `stage`, `status`, `message`, `timestamp`, `duration_ms`, and a `data` snapshot.
  - Worker settings: `max_jobs=2`, `job_timeout=900` seconds, `max_tries=3`.
- **Job status endpoint:** `GET /job/{job_id}` returns ARQ job status (`complete`, `processing`, `not_found`).
- `reload_config()` is called by the model-promote endpoint to hot-reload `_CONFIG` in the FastAPI process.
- Automatic expert escalation: if disease or crop confidence is below the configured thresholds, `ensure_expert_review()` creates a pending `ExpertReview` record.
- **Scheduled crons (production):** QStash delivers webhook calls to `/api/v1/internal-cron/weather-risk` (verified with `CRON_SECRET`) for proactive weather-risk alert generation.

**Known gaps:**

- `reload_config()` only updates the in-process FastAPI state; the ARQ worker process (when `REQUIRE_REDIS=True`) continues using its own copy of `_CONFIG` until restarted.
- In ARQ mode, no idempotent retry: a retried job can re-process the same image and potentially duplicate alerts or reviews.
- In sync mode (`REQUIRE_REDIS=False`), WebSocket progress events are not emitted during pipeline execution; clients see the result only on completion.

**Relevant code:**

- [prediction_job.py](../backend/src/app/services/prediction_job.py) — ARQ worker path
- [pipeline.py](../backend/src/app/pipeline.py) — synchronous pipeline orchestrator
- [predict.py](../backend/src/app/api/endpoints/predict.py) — route handler, mode selection
- [worker.py](../backend/src/app/worker.py) — ARQ worker entrypoint
- [internal_cron.py](../backend/src/app/api/endpoints/internal_cron.py) — QStash webhook handler

**What to improve:**

- Implement cross-process config reload for ARQ workers (e.g., Redis pub/sub or inotify file watcher).
- Add idempotency protection so ARQ retried jobs do not duplicate results, alerts, or expert reviews.
- Emit WebSocket progress events in sync mode for a live progress UX without ARQ.
- Add worker health, queue depth, job latency, retry rate, and failure rate metrics.

---

## 2. Authentication and Authorization

### 2.1 Registration, login, JWT, refresh, and logout

**Status: Mostly implemented — development shortcuts active**

**What works:**

- `POST /auth/register` accepts name, phone/email, password, language, location, lat/lon, crop history, and farm details. Phone or email is required; a `409` is returned for duplicates.
- `POST /auth/login` authenticates with phone or email (`identifier` field) and password. Rate-limited to 5 requests per minute via `slowapi`.
- Passwords are hashed with `pwdlib`.
- `POST /auth/change-password` changes password for authenticated users (requires `old_password` and `new_password` with minimum 8 characters).
- Access tokens: HS256 JWT, 30-minute expiry. Refresh tokens: HS256 JWT, 30-day expiry.
- Both tokens use a shared `_secret_key()` function that reads `JWT_SECRET_KEY` from the environment, defaulting to `"change-this-development-secret-key-32-bytes"` when the variable is unset.
- `POST /auth/refresh` reads the `refresh_token` cookie, decodes it, and issues a new token pair. Deduplication is handled in the frontend API client.
- `POST /auth/logout` deletes the `refresh_token` cookie.
- The `get_current_user` dependency accepts a Bearer token or falls back to the `X-User-ID` request header as a development convenience. This fallback is active in the current code.
- `require_expert_role` and `require_admin_role` enforce DB-backed role checks (`user.role in ["expert", "admin"]` or `user.role == "admin"`).
- The `refresh_token` cookie `secure` flag is set dynamically: `True` when `ENVIRONMENT == "production"`, `False` otherwise.
- The web API client (`client.ts`) handles automatic token refresh with deduplication and dispatches a `tokenRefreshed` event for other tabs.

**Known gaps:**

- The default JWT secret is a hard-coded development value; a missing `JWT_SECRET_KEY` in production is silently accepted.
- The `X-User-ID` fallback in `get_current_user` is active in production code paths.
- No refresh-token rotation or revocation.

**Relevant code:**

- [auth.py](../backend/src/app/api/endpoints/auth.py)
- [deps.py](../backend/src/app/api/deps.py)
- [client.ts](../frontend/src/api/client.ts)
- [AuthContext.tsx](../frontend/src/context/AuthContext.tsx)

**What to improve:**

- Fail startup when `JWT_SECRET_KEY` equals the default development value.
- Remove the `X-User-ID` fallback or limit it to an explicit `DEBUG=true` environment flag.
- Add integration tests: register, login, refresh, logout, change-password, expired token, invalid token, role checks.

---

### 2.2 Profile management

**Status: Implemented**

**What works:**

- `GET /profile` returns the authenticated user's profile, including name, phone, email, language, role, and farm fields (location, lat/lon, crop history, farm name, area).
- `PATCH /profile` updates name, language, location, lat/lon, and crop history.
- Password change is supported via `POST /auth/change-password`.
- Profile is returned on login and register as part of `AuthResponse`.
- Mobile `ApiService.getProfile()` and `updateProfile()` call these endpoints; the result is used to pre-fill the `CreatePredictionSheet` and `FarmerShell` data.

**Known gaps:**

- Language preference is stored on the `User` model but is not automatically applied to weather or translation unless the client sends it explicitly.
- Profile update does not provide fine-grained validation on phone format or name length.

**Relevant code:**

- [profile.py](../backend/src/app/api/endpoints/profile.py)
- [auth.py](../backend/src/app/api/endpoints/auth.py)
- [mobile/lib/services/api_service.dart](../mobile/lib/services/api_service.dart)

**What to improve:**

- Add account deletion and data-export endpoints if required by the product.
- Add profile validation (name length, valid phone format, valid crop names).

---

### 2.3 Farm and plot management

**Status: Implemented**

**What works:**

- `GET /farm` returns the farmer's farm with all plots and multilingual entity translation overlays for plot names.
- `PUT /farm` creates or updates the farm with name, location, lat/lon, area, crop history, and GeoJSON boundary.
- **GeoJSON polygon validation (`_validate_geojson_polygon`):** Verifies polygon type, minimum 4 coordinates, closed linear rings (`ring[0] == ring[-1]`), valid coordinate boundaries (`-180 <= lon <= 180`, `-90 <= lat <= 90`), and checks for absence of self-intersections via Shapely `poly.is_valid`.
- **Geodesic area calculation:** Automatically calculates approximate geodesic farm area in acres using projected coordinates when geometry is submitted.
- `POST /farm/plots` creates a new plot with name, crop, area, and optional geometry.
- `PUT /farm/plots/{plot_id}` updates a plot.
- `DELETE /farm/plots/{plot_id}` removes a plot.
- Plot geometry is validated against the farm boundary using an in-process ray-casting algorithm (`_plot_inside_farm`), including tolerance on the boundary.
- Schemas `FarmRequest`, `FarmResponse`, `PlotRequest`, `PlotResponse` are Pydantic-validated.
- Mobile `FarmScreen` now launches `FieldBoundaryScreen` for drawing farm and plot boundaries via an interactive map with center-crosshair point placement. Boundaries are drawn by panning the map and tapping + to place vertices. Magnetic snapping auto-corrects plot points placed outside the farm boundary to the nearest farm edge. `GeoMath` utility calculates geodesic area returned as acres and hectares.
- `CreatePredictionSheet` loads farm plots and shows them in a dropdown; the selected `plot_id` is sent to `predictBytes()`.

**Known gaps:**

- The mobile `FarmScreen` supports editing farm boundary via `FieldBoundaryScreen`, but direct farm-level attribute editing (name, location) via a form is still not exposed.
- Plot-level ownership check is enforced on parent farm, but concurrent plot modifications lack optimistic locking.

**Relevant code:**

- [farm.py](../backend/src/app/api/endpoints/farm.py)
- [mobile/lib/screens/farm/farm_screen.dart](../mobile/lib/screens/farm/farm_screen.dart)
- [mobile/lib/screens/map/field_boundary_screen.dart](../mobile/lib/screens/map/field_boundary_screen.dart) — center-crosshair boundary drawing with magnetic snapping
- [mobile/lib/utils/geo_math.dart](../mobile/lib/utils/geo_math.dart) — geodesic calculations and snap projection

**What to improve:**

- Expose farm-level attribute editing (name, location) in the mobile `FarmScreen`.
- Add tests for invalid polygons, plot outside boundary, ownership isolation, and deleted farms.

---

### 2.4 Remote Config and Backend URL Security

**Status: Implemented**

**What works:**

- `RemoteConfigService.fetchBackendUrl()` fetches `api_base_url` exclusively from the Supabase `public.app_config` table via PostgREST (`https://{SUPABASE_URL}/rest/v1/app_config?key=eq.api_base_url&select=value`) using the default anonymous key or `SUPABASE_ANON_KEY`.
- 8-second network timeout; on temporary network failure, falls back to the locally cached value in SharedPreferences (`remote_config_api_base_url`) saved from prior successful Supabase fetches.
- **Strict single source of truth:** `ApiService.initBaseUrl()` resolves the backend URL exclusively from Supabase Remote Config (or its local offline cache). All local dev defaults (`http://127.0.0.1:8000`) and arbitrary compile-time overrides have been eliminated.
- **Backend URL is fully locked from the client:** The `_showServerSettingsDialog`, `Icons.dns_outlined` header button, and "Change URL" error-state link have been removed from `LoginScreen`. `setCustomBaseUrl` and `resetToRemoteConfig` are removed from `ApiService`. No user or farmer can inspect or modify the backend endpoint from within the app.
- Supabase table `public.app_config` has RLS enabled with a public read-only policy (SELECT for `anon`, `authenticated`, `public`). Write access requires admin database access only.

**Known gaps:**

- On first cold launch without any prior cache, an internet connection is required to fetch the initial config from Supabase.
- No in-app indicator showing which backend URL is currently active (intentional security design).

**Relevant code:**

- [remote_config_service.dart](../mobile/lib/services/remote_config_service.dart) — Supabase PostgREST query, timeout, and SharedPreferences caching
- [api_service.dart](../mobile/lib/services/api_service.dart) — `initBaseUrl()` exclusive Supabase resolution
- [login_screen.dart](../mobile/lib/screens/auth/login_screen.dart) — Server Settings dialog and URL buttons removed

**What to improve:**

- Add a startup validation warning if neither Supabase nor cache returns a URL and the fallback is the local dev address in a production build.
- Consider signing the config response (HMAC) to prevent MITM URL substitution.

## 3. Scan and Prediction Features

### 3.1 Web scan flow

**Status: Implemented**

**What works:**

- `ScanPage.tsx` allows file selection, image compression, and form submission with location, language, and plot metadata.
- `usePredict.ts` hook manages the upload-to-result flow.
- `ProcessingPage.tsx` polls and shows pipeline status.
- `PredictionResultPage.tsx` renders crop, disease, confidence, severity, pests, weather, and structured recommendation sections.
- Rescan is supported.

**Known gaps:**

- Image compression limit in the client may not match the server limit.
- Hard-coded localhost fallback URL has been removed from `client.ts` but some asset URL construction may still reference it.
- No explicit upload cancellation or progress indicator.

**Relevant code:**

- [frontend/src/pages/ScanPage.tsx](../frontend/src/pages/ScanPage.tsx)
- [frontend/src/hooks/usePredict.ts](../frontend/src/hooks/usePredict.ts)
- [frontend/src/pages/ProcessingPage.tsx](../frontend/src/pages/ProcessingPage.tsx)
- [frontend/src/pages/PredictionResultPage.tsx](../frontend/src/pages/PredictionResultPage.tsx)

**What to improve:**

- Align client-side and server-side file size limits.
- Add upload cancellation and explicit progress feedback.
- Show server-side rejection reasons and retry prompts clearly.

---

### 3.2 Mobile scan flow

**Status: Implemented**

**What works:**

- `CreatePredictionSheet` provides camera and gallery image selection, preview, retake, plot selector, location/lat/lon fields, and language selector. Fields are pre-filled from the user's profile and farm.
- If the device is offline, the scan is queued via `SyncService` and the user sees an offline-queued banner.
- On submission, `predictBytes()` is called and the returned `prediction_id` is passed to `ProcessingSheet`.
- `ProcessingSheet` connects via WebSocket (`/ws/predictions/{id}`) and falls back to 1.5-second polling. It displays a 5-stage animated progress view with live crop, disease, and pest labels as they are detected. Shows a user-friendly failure card with a rescan button.
- `ResultDetailSheet` shows the full structured result: localized recommendation sections, inline TTS player bar with cloud + on-device fallback, feedback form (correct/incorrect + optional note), expert-review request button, on-demand translation, and language switcher.

**Known gaps:**

- No device permission prompts for camera and storage; the app will silently fail if permissions are denied.
- WebSocket does not reconnect on disconnect inside the processing sheet.
- Captured image bytes are not cleaned up on discard.

**Relevant code:**

- [create_prediction_sheet.dart](../mobile/lib/screens/scan/create_prediction_sheet.dart)
- [processing_sheet.dart](../mobile/lib/screens/scan/processing_sheet.dart)
- [result_detail_sheet.dart](../mobile/lib/screens/scan/result_detail_sheet.dart)

**What to improve:**

- Add camera and storage permission handling with user-facing prompts and graceful fallback.
- Add WebSocket reconnect with exponential backoff.
- Clean up captured image bytes on sheet dismiss without submission.

---

### 3.3 Processing status and live events

**Status: Mostly implemented**

**What works:**

- The backend publishes a Redis event after every pipeline stage via `push_status()`.
- WebSocket endpoint (`/ws/predictions/{id}`) subscribes to the Redis channel and streams events to connected clients.
- Events include: `stage`, `status`, `message`, `timestamp`, `duration_ms`, and a `data` snapshot of the current crop/disease/pests/severity.
- The mobile `ProcessingSheet` listens via WebSocket and falls back to HTTP polling at 1.5-second intervals.
- A terminal `failed` event includes the error message, failed stage name, and a full data snapshot.
- The web `ProcessingPage.tsx` polls the prediction status.

**Known gaps:**

- The web client does not attempt WebSocket and relies only on polling.
- WebSocket connections are not explicitly closed on all disconnect paths.
- No connection-retry logic in the mobile WebSocket handler.

**Relevant code:**

- [prediction_job.py](../backend/src/app/services/prediction_job.py) — stage event publisher
- [predict.py](../backend/src/app/api/endpoints/predict.py) — WebSocket endpoint
- [processing_sheet.dart](../mobile/lib/screens/scan/processing_sheet.dart)

**What to improve:**

- Add WebSocket support to the web processing page.
- Close WebSocket channels on all disconnect and lifecycle paths.
- Add reconnect logic in the mobile processing sheet.

---

### 3.4 Prediction results display

**Status: Implemented**

**What works:**

- Full result is rendered: crop, disease, confidence, severity, pests, weather, and structured recommendation sections.
- `Prediction.fromJson()` handles all known response shapes: completed, failed, partial, and translated results.
- Previously reported unresolved-variable bug in `fromJson()` is fixed; all section fields are properly declared and parsed.
- `copyWithTranslations()` merges new translation keys without overwriting existing ones.
- `localizedRecommendation()`, `localizedImmediateAction()`, `localizedTreatment()`, `localizedPrevention()`, `localizedMonitoring()`, and `localizedAudioText()` resolve the correct language from the `translations` map with multi-key lookup.
- `localizedAudioText()` produces language-specific spoken summaries in English, Hindi, and Gujarati with native-language labels (e.g., "त्वरित कार्रवाई:", "સારવાર માર્ગદર્શન:").

**Known gaps:**

- No client-side result export or share functionality.
- Confidence is displayed as a percentage; no explicit label clarifying that this is model confidence, not ground truth.

**Relevant code:**

- [mobile/lib/models/prediction.dart](../mobile/lib/models/prediction.dart)
- [frontend/src/pages/PredictionResultPage.tsx](../frontend/src/pages/PredictionResultPage.tsx)

**What to improve:**

- Label confidence values clearly as model confidence.
- Add result sharing (PDF or image export) if required by the product.
- Add JSON parsing unit tests covering completed, failed, partial, and legacy response shapes.

---

### 3.5 History

**Status: Implemented, limited**

**What works:**

- `GET /history?offset=N&limit=M` returns the authenticated user's prediction history, paginated, with offset and limit validated (1–100).
- Returns the full `result` JSON with `prediction_id` and `created_at` added.
- Web `HistoryPage.tsx` displays history with crop/search filtering.
- Mobile `HistoryScreen` shows the full history list with pull-to-refresh and tap-to-open result sheet.
- `FarmerShell` loads history on startup and updates it when a new scan completes.

**Known gaps:**

- Server-side filters (date, crop, disease, status, plot) are not implemented; only offset/limit pagination exists.
- No cursor-based pagination; large offsets become slow.
- No visible pagination control on either web or mobile.

**Relevant code:**

- [history.py](../backend/src/app/api/endpoints/history.py)
- [frontend/src/pages/HistoryPage.tsx](../frontend/src/pages/HistoryPage.tsx)
- [mobile/lib/screens/history/history_screen.dart](../mobile/lib/screens/history/history_screen.dart)

**What to improve:**

- Add server-side filters: date range, crop, disease, status, plot ID.
- Implement cursor-based or keyset pagination.
- Add visible pagination controls and empty-state handling.
- Add ownership isolation tests.

---

### 3.6 Farmer feedback

**Status: Implemented (collection and review)**

**What works:**

- `POST /feedback` accepts `prediction_id`, `is_correct`, and an optional `farmer_note`. Returns `409` on duplicate submission.
- `POST /feedback/{feedback_id}/review` (expert role) persists: `review_status`, `review_decision`, `reviewer_id`, `reviewer_note`, `corrected_label`, and `reviewed_at`.
- When a review is approved for an incorrect prediction, a `DatasetCandidate` record is created (or updated if one exists) with `source="farmer_feedback_review"`, original label, corrected label, image path, and a provenance note.
- Web `PredictionResultPage.tsx` shows the feedback form.
- Mobile `ResultDetailSheet` includes a feedback form: correct/incorrect buttons, optional note field, loading state, and a confirmation snackbar on success.
- `GET /admin/feedback` (expert role) lists all feedback with review status, reviewer, and reviewed-at fields.

**Previous status was wrong:** The `Feedback` model import in the review path is correctly present (`from app.models import Feedback, DatasetCandidate`). The review decision **is** persisted (full fields written before `session.commit()`).

**Known gaps:**

- The corrected label from feedback review is stored in `DatasetCandidate` but is **not** merged back into the public prediction result JSON or the `prediction.disease` column.
- There is no update path if a farmer changes their feedback.

**Relevant code:**

- [feedback.py](../backend/src/app/api/endpoints/feedback.py)
- [result_detail_sheet.dart](../mobile/lib/screens/scan/result_detail_sheet.dart)
- [frontend/src/pages/PredictionResultPage.tsx](../frontend/src/pages/PredictionResultPage.tsx)

**What to improve:**

- Merge approved feedback corrections back into the prediction result and `prediction.disease` column.
- Define a feedback update path or prevent duplicate submissions explicitly.
- Add authorization tests (farmer can only feedback their own predictions).

---

## 4. Expert and Administration

### 4.1 Expert review queue

**Status: Mostly implemented**

**What works:**

- `GET /expert/queue` returns all pending `ExpertReview` records with crop, disease, confidence, severity, and timestamps. Ordered by most recent.
- `GET /expert/reviews/{review_id}` returns full review details including raw/processed presigned GCS image URLs and all prediction fields. Accepts a `lang` query parameter — if provided, `farmer_guidance` is translated via the `entity_translations` overlay before returning.
- `POST /expert/reviews/{review_id}` processes a review:
  - Accepts three `action` values: `'Override / Correct Findings'`, `'Request Rescan'`, or approve (any other value).
  - Persists: `decision`, `status="verified"`, `expert_id`, `farmer_guidance`, `internal_note`, `corrected_disease`, `corrected_severity`.
  - Updates `prediction.status` to `"rescan_requested"` or `"verified"`.
  - Updates `prediction.result["disease"]["label"]` and `prediction.disease` if a correction is provided. Updates `prediction.result["severity"]["percent"]` and `prediction.severity_pct` if a corrected severity is provided. `flag_modified` is called to ensure SQLAlchemy tracks the JSON mutation.
  - Creates a farmer-facing alert (with duplicate guard) of kind `"review_verified"`.
  - Optionally creates a `DatasetCandidate` record when `add_to_retraining=true`.
  - Enqueues background translation tasks via `enqueue_translation` for both `farmer_guidance` and the generated alert.
  - State-machine enforcement: only `pending` reviews can be submitted; re-submitting a `verified` review returns HTTP 409.
- Automatic low-confidence escalation: `prediction_job.py` calls `ensure_expert_review()` transactionally when disease or crop confidence is below threshold; `prediction.status` is set to `"pending_expert_review"`.
- Farmer can also manually request review via `POST /predictions/{id}/expert-request` (mobile `ResultDetailSheet` button).
- Web `ExpertQueuePage.tsx` and `ExpertReviewPage.tsx` render the queue and review forms.

**Known gaps:**

- No reviewer assignment or duplicate-review protection (two experts can submit reviews for the same record simultaneously).
- No frontend locking to prevent stale updates if two experts open the same review queue item concurrently.

**Relevant code:**

- [expert.py](../backend/src/app/api/endpoints/expert.py)
- [crud/expert_review.py](../backend/src/app/crud/expert_review.py)
- [prediction_job.py — ensure_expert_review call](../backend/src/app/services/prediction_job.py)
- [frontend/src/pages/ExpertQueuePage.tsx](../frontend/src/pages/ExpertQueuePage.tsx)
- [frontend/src/pages/ExpertReviewPage.tsx](../frontend/src/pages/ExpertReviewPage.tsx)

**What to improve:**

- Add concurrent-submission protection (optimistic locking or a `reviewed_at IS NULL` guard).
- Add reviewer assignment (`claimed_by`) to prevent duplicate work across active agronomists.
- Add authorization tests: expert cannot review another expert's submitted review.

---

### 4.2 Alerts

**Status: Implemented**

**What works:**

- `GET /alerts` returns the authenticated user's last 20 alerts, ordered by creation date, including `id`, `prediction_id`, `kind`, `severity`, `title`, `body`, `is_read`, and `created_at`. Supports a `lang` query parameter and `Accept-Language` header — translations are applied via the `entity_translations` overlay.
- `POST /alerts/{alert_id}/read` marks an alert read (with ownership check).
- Alert kinds generated: `"review_verified"` (from expert review completion) and weather risk alerts (from the scheduled `POST /internal/cron/weather-risks` job). There is no separate "prediction low-confidence" alert kind.
- `GET /predictions/{id}` automatically marks any associated `review_verified` alert as read when the farmer views the prediction detail.
- Web `SideBar.tsx` exposes alert access/unread state; `AlertsPage.tsx` displays alerts.
- Mobile `AlertsScreen` shows all alerts with read/unread state, distinguishes expert alerts (shield icon) from weather/disease alerts (warning icon), and supports marking alerts read. Unread count is shown as a `Badge` on the bottom nav icon.
- `FarmerShell` loads alerts on startup and refreshes them on request.

**Known gaps:**

- Alerts are capped at 20; there is no pagination for older alerts.
- No alert pagination on either web or mobile.
- Duplicate alerts for the same `prediction_id` and `kind` are guarded in the expert review path but not in all alert-creation paths.

**Relevant code:**

- [alerts.py](../backend/src/app/api/endpoints/alerts.py)
- [mobile/lib/screens/alerts/alerts_screen.dart](../mobile/lib/screens/alerts/alerts_screen.dart)
- [frontend/src/pages/AlertsPage.tsx](../frontend/src/pages/AlertsPage.tsx)

**What to improve:**

- Add pagination to the alerts endpoint.
- Add a global duplicate-creation guard (unique constraint on `user_id + kind + prediction_id`).
- Add alert expiry and archival.

---

### 4.3 Admin metrics and monitoring

**Status: Implemented with drift monitoring**

**What works:**

- `GET /admin/metrics` returns:
  - `total_users`, `total_scans`, `completed_scans`, `queue_depth` (processing count).
  - `accuracy`: ratio of farmer-feedback marked correct (labeled as-is; not a validated model metric).
  - `failures`: `total_failed`, `failure_rate`.
  - `processing_duration`: `avg_ms`, `p95_ms`, `sample_count` (computed from stored `total_duration_ms` in result JSON).
  - `fallbacks`: recommendation fallback count and weather fallback count.
  - `expert_metrics`: total reviews, approved, overrides, pending, `validated_accuracy` (approve / decided).
  - `disease_distribution`: disease label → count.
  - `confidence_histogram`: High (≥75%), Medium (50–75%), Low (<50%) confidence bracket counts.
  - `drift`: rolling 7d/30d average disease confidence, 7-day low-confidence rate, pending retraining candidates count, expert correction rate.
- `AdminMetricsPage.tsx` queries this endpoint and renders charts (bar, pie via Recharts), model health panel, dataset summary, and MLOps export form.
- Model health is fetched from `GET /admin/models/health` and displayed in the admin page.
- Dataset summary from `GET /admin/dataset/summary` is rendered.

**Known gaps:**

- The `accuracy` field in the response mixes farmer-feedback accuracy with `validated_accuracy` from expert reviews; the `AdminMetrics` TypeScript type (`accuracy_rate_pct`) does not cleanly map to the backend response fields (`accuracy`, `expert_metrics.validated_accuracy`).
- P95 duration is computed by sorting all durations in Python; this does not scale.

**Relevant code:**

- [admin.py](../backend/src/app/api/endpoints/admin.py)
- [frontend/src/pages/AdminMetricsPage.tsx](../frontend/src/pages/AdminMetricsPage.tsx)
- [frontend/src/api/admin.ts](../frontend/src/api/admin.ts)

**What to improve:**

- Align TypeScript `AdminMetrics` type with the actual backend response shape.
- Use database-level aggregation (`percentile_cont`) for P95 instead of Python sorting.
- Add date/crop/model-version filters.
- Clearly label farmer-feedback accuracy vs. expert-validated accuracy in both API and UI.
- Add tests for empty data, missing result JSON, and database failures.

---

### 4.4 Admin configuration management

**Status: Mostly implemented**

**What works:**

- `GET /admin/config` reads `crop_routing_threshold` and `expert_escalation_cutoff` from `config.yaml` (mapped from `thresholds.crop_confidence` and `thresholds.disease_confidence`). Only these two threshold fields are exposed; other config fields are not surfaced through this endpoint.
- `PUT /admin/config` writes updated threshold values back to `config.yaml`, calls `pipeline.reload_config()` so the running FastAPI process picks up the change immediately, and publishes the updated thresholds to Upstash Redis REST under the key `sf:config:thresholds`.
- `AdminMetricsPage.tsx` does not currently expose a config edit form; the endpoints are available but no frontend UI renders them.

**Known limitation:**

- The ARQ worker process is always separate; it never picks up config changes from either path until restarted.

**Relevant code:**

- [admin.py — /admin/config](../backend/src/app/api/endpoints/admin.py)

**What to improve:**

- Implement a cross-process reload signal for the worker.
- Expose the config edit form in the admin UI.
- Add range validation and audit logging for threshold changes.

---

### 4.5 Model registry and promotion gates

**Status: Implemented**

**What works:**

- `GET /admin/models` lists all registered model versions from `model_registry.json`, including version history, metrics, active version, and promoted-by.
- `GET /admin/models/health` checks which configured models have their checkpoint and labels files present on disk. Returns `overall_status: "healthy"` or `"degraded"`, plus per-model status, file paths, active version, val/test accuracy, and training date.
- `POST /admin/models/promote` promotes a model version to active:
  - Enforces a minimum test-accuracy gate: rejects promotion if `test_acc < min_test_acc`.
  - Verifies that checkpoint and labels files exist on disk before writing.
  - Updates `model_registry.json` (marks all other versions as `"retired"`) and `config.yaml` atomically.
  - Calls `pipeline.reload_config()` to hot-reload the in-process FastAPI config.
  - Logs the promotion with `promoted_by` and timestamp.
- `POST /admin/models/rollback` rolls back the active model to a specified or most-recently-retired version:
  - Accepts `model_key` and an optional `target_version`; defaults to the most recently retired version if not specified.
  - Verifies the target checkpoint exists on disk before switching.
  - Updates `model_registry.json` and `config.yaml`, then calls `pipeline.reload_config()`.
- `AdminMetricsPage.tsx` queries `GET /admin/models/health` and renders a model health panel.

**Known gaps:**

- `reload_config()` only affects the FastAPI process; the ARQ worker needs a separate restart.
- No frontend form for triggering promotions or rollbacks; only the health panel is rendered.

**Relevant code:**

- [model_registry.py](../backend/src/app/api/endpoints/model_registry.py)
- [frontend/src/pages/AdminMetricsPage.tsx](../frontend/src/pages/AdminMetricsPage.tsx)

**What to improve:**

- Add a promotion form to the admin UI.
- Add cross-process worker reload.
- Add tests for promotion gating, missing files, and concurrent promotions.

---

### 4.6 MLOps dataset export

**Status: Implemented (backend); aligned (frontend)**

**What works:**

- `GET /admin/dataset/summary` returns total candidates, by-source counts (expert vs. farmer), by-status counts, and per-crop distribution.
- `POST /admin/dataset/export` builds and streams a ZIP archive:
  - Filters by source (expert, farmer), crop (case-insensitive), and candidate status.
  - Splits candidates into `train`/`val`/`test` using deterministic SHA-256 hashing of candidate ID; split percentages must total 100.
  - Supports `PyTorch Folder` (ImageFolder structure: `images/<split>/<class_label>/`) and `JSON Manifest` formats.
  - Supports `raw` or `preprocessed` image targets.
  - Includes a `metadata.json` with full provenance block (exported\_at, total candidates, split summary, export config, schema\_version) and a `README.md` for reproducibility.
  - Path traversal is protected via `resolve_storage_path()`.
- `AdminMetricsPage.tsx` calls `exportDataset()` from `admin.ts` which sends `POST /admin/dataset/export` with a `requestBlob` call. The blob is downloaded as `dataset_export.zip`.
- The frontend export form exposes crop filter, status filter, image target, format, and split percentage controls.
- **Previously reported frontend/backend mismatch is resolved:** the frontend now calls the correct `POST /admin/dataset/export` route via `requestBlob`.

**Known gaps:**

- The `DatasetCandidate.status` filter accepts any string; invalid status values return an empty result rather than a validation error.
- Files missing from disk are silently skipped (no image in the archive, but the candidate appears in `metadata.json` with `image_file: null`).

**Relevant code:**

- [mlops.py](../backend/src/app/api/endpoints/mlops.py)
- [frontend/src/api/admin.ts](../frontend/src/api/admin.ts)
- [frontend/src/pages/AdminMetricsPage.tsx](../frontend/src/pages/AdminMetricsPage.tsx)

**What to improve:**

- Validate `status` filter against the known `DatasetCandidate.status` enum.
- Surface missing image files as warnings in the export response metadata.
- Add training dataset size limits and authorization audit logging.
- Add tests for empty exports, missing files, invalid split totals, and unauthorized access.

---

### 4.7 Database purge and blob cleanup

**Status: Implemented — confirmation token and dry-run preview enabled**

**What works:**

- `DELETE /admin/purge` deletes all DatasetCandidate, ExpertReview, Recommendation, Feedback, Alert, Prediction, and Image records in transactional cascade order.
- Requires explicit confirmation token via body (`payload.confirmation`) or query parameter (`confirmation`): accepts `'DELETE'` or `'PURGE_ALL_DATA'`; rejects mismatch with HTTP 400.
- Supports `dry_run=true` query parameter: computes and returns record counts across all 7 target tables without deleting data.
- `DELETE /admin/blobs` removes unreferenced files from `data/uploads`, `data/processed`, and `data/audio`.
- Supports `dry_run=true` query parameter: returns orphaned file counts and size without unlinking files.
- Scheduled weekly cleanup (`purge_orphaned_blobs_cron`) runs every Sunday at 03:00 UTC via the ARQ worker. Files newer than 1 hour are preserved (grace period for in-flight predictions).
- All storage paths use `storage_relative_path()` for normalization, preventing double-slash or OS-separator mismatches.

**Known gaps:**

- No persistent audit log table recording who triggered purge/cleanup actions and when.

**Relevant code:**

- [admin.py — /admin/purge and /admin/blobs](../backend/src/app/api/endpoints/admin.py)
- [worker.py — purge_orphaned_blobs_cron](../backend/src/app/worker.py)

**What to improve:**

- Add an audit log table for admin data modifications and purges.
- Add tests using temporary directories for blob cleanup.

---

### 4.8 Admin user management and manual triggers

**Status: Implemented**

**What works:**

- `GET /admin/users` returns paginated list of registered users with search (name, email, phone) and role filtering (`farmer`, `expert`, `admin`). Returns total count, farm name/location, scan count, and registration date.
- `PATCH /admin/users/{target_user_id}/role` updates user role (`farmer`, `expert`, `admin`) with critical security guards:
  - **Self-demotion lockout prevention:** Administrators cannot demote their own account.
  - **Last-admin lockout prevention:** Rejects demoting the last active administrator on the platform.
- `POST /admin/weather-risk/trigger` manually invokes the proactive microclimate weather-risk evaluation task across all farms/plots for testing and verification without waiting for scheduled cron triggers.
- Frontend `AdminUsersPage.tsx` provides role management UI, user search, and role switching modal.

**Relevant code:**

- [admin.py — /admin/users, /admin/weather-risk/trigger](../backend/src/app/api/endpoints/admin.py)
- [frontend/src/pages/AdminUsersPage.tsx](../frontend/src/pages/AdminUsersPage.tsx)

---

## 5. Web Frontend

### 5.1 Routing, authentication, and role portals

**Status: Mostly implemented**

**What works:**

- Public routes: Landing (`/`), About (`/about`), Services (`/services`), Crops (`/crops`), Terms (`/terms`), Privacy (`/privacy`), Login (`/auth/login`), Register (`/auth/register`), Forgot Password (`/auth/forgot-password`), Reset Password (`/auth/reset-password`).
- Protected routes (wrapped in `AppShell` + `ProtectedRoute`): Dashboard, Scan, Processing, Result, History, Settings, Weather, Alerts, Farm Settings, Expert Queue, Expert Review, Admin Metrics, Admin Feedback, Admin Users.
- Anti-vibecoded design system: complete UI redesign featuring custom SVG icon set in `src/components/icons/` (replacing Lucide), sharp border radii (`rounded-sm`), border depth instead of drop shadows, authentic agricultural color palette, real interactive diagnostic pipeline demo with Grad-CAM visualization, and skeleton loading states for asynchronous views.
- Terms of Service (`/terms`) and Privacy Policy (`/privacy`) pages fully integrated and linked in public footer.
- `ProtectedRoute` accepts two optional boolean props that gate routes by role:
  - `adminOnly` — allows `admin` **or** `expert` roles. Used for: `/admin/feedback`, `/admin/expert`, `/admin/expert/:id`.
  - `strictAdminOnly` — allows `admin` role only. Used for: `/admin/metrics`, `/admin/users`.
  - When neither prop is set, any authenticated user is admitted.
  - While auth state is loading, a skeleton loader is displayed instead of redirecting.
- `AuthContext` (`context/AuthContext.tsx`) provides the following to all consumers:
  - **State:** `user` (`Profile | null`), `token` (`string | null`), `isAuthenticated`, `isLoading`, `language`, `units`.
  - **Helpers:** `t(key)` translation function with compile-time type safety over 670+ keys, `setLanguage(lang)` (persists to localStorage and backend), `setUnits(units)` (localStorage only).
  - **Auth actions:** `signIn(identifier, password)`, `signUp(payload)`, `signOut()`, `refreshProfile()`.
  - The context does **not** expose `login()` or `logout()` — callers must use `signIn`/`signOut`.
- The sidebar (`Sidebar.tsx`) renders a role-aware navigation tree depending on role (`farmer`, `expert`, `admin`), embeds the compact `LanguageToggle` (Globe + 2-letter uppercase code) and `ThemeToggle`, and provides an in-sidebar notification panel for unread alerts.
- On 401, the shared API client automatically attempts a token refresh via the HttpOnly cookie. Deduplication prevents parallel refresh calls.

**Known gaps:**

- Farmer, expert, and admin experiences share most of the same shell; they are not distinct portals as described in the roadmap.
- Some pages render correctly for the wrong role if only URL-level protection is checked.

**Relevant code:**

- [frontend/src/App.tsx](../frontend/src/App.tsx)
- [frontend/src/components/ProtectedRoute.tsx](../frontend/src/components/ProtectedRoute.tsx)
- [frontend/src/context/AuthContext.tsx](../frontend/src/context/AuthContext.tsx)

**What to improve:**

- Define explicit role route maps.
- Add end-to-end authorization tests for all protected routes.
- Consider a dedicated expert shell to better separate the expert experience.

---

### 5.2 Web API client

**Status: Implemented**

**What works:**

- `client.ts` provides `request<T>()` and `requestBlob()` helpers.
- Base URL is resolved from `VITE_API_URL` env variable, defaulting to the current hostname on port 8000. localhost/127.0.0.1 in the configured URL are automatically replaced with the actual window hostname.
- All requests include `credentials: 'include'` for cookie-based refresh.
- Automatic token refresh on 401, with a deduplication promise and a `tokenRefreshed` browser event.
- `getWebSocketUrl()` constructs `ws://` or `wss://` URLs from the configured base URL.
- Typed API modules exist: `auth.ts`, `predictions.ts`, `farm.ts`, `expert.ts`, `alerts.ts`, `crops.ts`, `admin.ts`.
- Shared `types.ts` defines: `Prediction`, `Profile`, `Farm`, `Plot`, `WeatherData`, `AdminMetrics`, `FeedbackLog`.

**Known gaps:**

- `AdminMetrics` TypeScript type does not fully match the backend response (extra fields, missing `drift` block).
- No request timeout or network-level retry.

**Relevant code:**

- [frontend/src/api/client.ts](../frontend/src/api/client.ts)
- [frontend/src/api/types.ts](../frontend/src/api/types.ts)

**What to improve:**

- Add request timeout and retry configuration.
- Align `AdminMetrics` and other types with the actual backend response shapes.
- Consider generating types from an OpenAPI schema to keep them in sync.

---

### 5.3 Web weather page

**Status: Implemented**

**What works:**

- `WeatherPage.tsx` fetches weather data using the user's lat/lon from profile.
- Displays temperature, condition, humidity, and wind speed using the configured units. Pressure and cloudiness are **not** displayed.
- Shows the agricultural advisory text.
- Auto-translates the advisory when the user's language is Hindi or Gujarati, with an in-flight deduplication guard. Falls back to server-provided `translated_advisory` or `translations[lang]` before calling `POST /weather/translate`.
- TTS playback with pause/stop support. Fetches audio via `POST /tts`.
- Uses `translateWeather()` from `i18n/domain.ts` for condition labels.

**Known gaps:**

- No 5-day or extended forecast view.
- No explicit loading state between language switch and advisory translation.

**Relevant code:**

- [frontend/src/pages/WeatherPage.tsx](../frontend/src/pages/WeatherPage.tsx)

---

### 5.4 Internationalization

**Status: Implemented**

**What works:**

- Full UI translation dictionaries in English, Hindi (`hi`), and Gujarati (`gu`) (`i18n/en.ts`, `hi.ts`, `gu.ts`) with **670+ keys each**, providing 100% localization coverage across all 24 page components.
- Strict compile-time key parity: `gu.ts` and `hi.ts` are typed as `Record<keyof typeof en, string>`, causing `tsc` to fail if any key is missing or mismatched.
- Redesigned `LanguageToggle` component supporting dropdown (Globe + 2-letter uppercase code `EN`/`GU`/`HI`), segmented pill, and icon-only variants with tooltips. Embedded in PublicNav, Sidebar, Footer, and all auth pages.
- Curated agricultural domain lexicon for crops, diseases, pests, severity levels, weather conditions, and alert titles (`i18n/domain.ts`) with runtime translation helpers (`translateCrop`, `translateDisease`, `translatePest`, `translateSeverityBucket`, `translateWeather`, `translateAlertTitle`).
- Language preference is persisted in `localStorage` and synced to the backend user profile via `updateProfile()` inside `AuthContext.setLanguage()`. On login, the language stored in the profile is loaded and applied.
- `t()` translation function and `language`/`units` state are provided via context.
- Backend translation service (`services/translation/service.py`) supports: `en`, `hi`, `gu`, `mr`, `te`, `ta` (Marathi, Telugu, Tamil) via `normalize_language_code`.
- Primary translation engine: Google Cloud Translation API v2 (`translate_batch_google`).
- Fallback engine: HuggingFace Qwen LLM via nscale (`translate_batch_hf_fallback`) — used when Google API fails.
- Both async (FastAPI) and sync (ARQ worker) variants are provided.
- Auto-translation at pipeline end for non-English requests: `translate_recommendation_sync()`.
- On-demand translation: `POST /predictions/{id}/translate?target_language=...` translates and caches in DB; returns from cache on subsequent calls.
- Weather advisory translation: on-demand via `POST /weather/translate` and inline via `GET /weather?language=...`.
- Mobile: `DomainTranslations` and `AppTranslations` provide full localized UI + domain labels in `en`/`hi`/`gu`.

**Relevant code:**

- [translation/service.py](../backend/src/app/services/translation/service.py)
- [translation.py endpoint](../backend/src/app/api/endpoints/translation.py)
- [frontend/src/i18n/](../frontend/src/i18n/)
- [mobile/lib/i18n/](../mobile/lib/i18n/)
- [mobile/lib/providers/locale_provider.dart](../mobile/lib/providers/locale_provider.dart)

**What to improve:**

- Expand mobile `DomainTranslations` vocabulary as new disease labels and pest names are added.
- Add coverage tests for translation service: batch, on-demand endpoint, HF fallback.
- Add error handling when both Google and HF translation fail for the same text.

---

## 6. Mobile Application

### 6.1 Entry point and authentication flow

**Status: Implemented**

**What works:**

- `main.dart` bootstraps `LocaleProvider` → `FieldnoteApp` → `AuthWrapper`.
- `AuthWrapper` reads `auth_token` from `SharedPreferences` on startup. If a token exists, it calls `getProfile()`; if the profile returns role `farmer`, `FarmerShell` is displayed. If role is anything else, the token is cleared and `LoginScreen` is shown with a "farmer access only" message.
- `LoginScreen` supports both login and registration in one screen:
  - Toggle between login/register modes.
  - Language selector (English, हिन्दी, ગુજરાતી) in the app bar.
  - Registration sends name, password, phone/email, location, language, and crop history.
  - A farmer-only badge explains why non-farmer roles are blocked.
- JWT access token is stored in `SharedPreferences` under `auth_token`.
- Logout clears the token from `SharedPreferences` and calls `widget.onLogout`.

**Known gaps:**

- `SharedPreferences` is not secure storage; token is stored in plaintext.
- Mobile does not implement token refresh; an expired token causes the user to be silently logged out on the next app launch.

**Relevant code:**

- [main.dart](../mobile/lib/main.dart)
- [auth_wrapper.dart](../mobile/lib/screens/auth/auth_wrapper.dart)
- [login_screen.dart](../mobile/lib/screens/auth/login_screen.dart)

**What to improve:**

- Migrate to `flutter_secure_storage` for token storage.
- Add refresh-token support so sessions survive the 30-minute access token expiry.
- Add registration field validation (name length, phone format, etc.).

---

### 6.2 Farmer shell and navigation

**Status: Implemented**

**What works:**

- `FarmerShell` provides a 5-tab `IndexedStack` + `NavigationBar` bottom navigation: Today, History, Weather, Farm, Alerts.
- On startup, loads history, profile, farm, weather, and alerts concurrently via `Future.wait()`.
- Locale changes (via `didChangeDependencies`) trigger an automatic weather reload.
- Connectivity listener (via `connectivity_plus`) drains the offline scan queue automatically when the device comes online; pending count is refreshed afterward.
- Modals are shown as `DraggableScrollableSheet` bottom sheets: `CreatePredictionSheet` → `ProcessingSheet` → `ResultDetailSheet`.
- Alerts tab shows a `Badge` with unread count on the navigation icon.
- All screens receive data from `FarmerShell` state; no screen fetches its own data independently.

**Relevant code:**

- [farmer_shell.dart](../mobile/lib/screens/shell/farmer_shell.dart)

---

### 6.3 Mobile API service

**Status: Implemented**

**What works:**

- `ApiService` is constructed with a platform-aware base URL:
  - `API_BASE_URL` environment variable if set.
  - `http://10.0.2.2:8000` for Android emulator.
  - `http://127.0.0.1:8000` otherwise.
- Authorization header (`Bearer <token>`) is sent on all authenticated calls.
- 15-second timeout on weather and TTS requests.
- Complete API coverage:
  - Auth: `login()`, `register()`.
  - Profile: `getProfile()`, `updateProfile()`.
  - Farm: `getFarm()`, `saveFarm()`, `createPlot()`.
  - Weather: `getWeather()`, `translateWeatherAdvisory()`.
  - Alerts: `getAlerts()`, `markAlertRead()`.
  - Predictions: `predictBytes()`, `getPrediction()`, `getPredictionRaw()`, `history()`.
  - Feedback: `submitFeedback()`, `requestExpertReview()`.
  - Translation: `translatePrediction()`.
  - TTS: `generateTTS()`.
  - WebSocket helper: `getWebSocketUrl()`.
- `predictBytes()` sends `plot_id`, `lat`, `lon`, `location`, and `language`.

**Known gaps:**

- No structured error parsing beyond throwing `Exception(message)`.
- No token refresh; an expired token causes all requests to fail with a 401.

**Relevant code:**

- [api_service.dart](../mobile/lib/services/api_service.dart)

**What to improve:**

- Add token refresh support.
- Add structured error types for network, authentication, and server errors.
- Add global request timeout (currently only applied to weather/TTS).

---

### 6.4 Text-to-speech service

**Status: Implemented**

**What works:**

- `TtsService` is a singleton `ChangeNotifier`.
- Primary: Google Cloud TTS via backend `POST /tts`. Returns MP3 audio as base64; decoded and played with `audioplayers`. Voice selection is handled server-side.
- Fallback: `flutter_tts` on-device engine. If `gu` locale is unavailable, tries `hi-IN`, then `en-US`.
- `cleanText()` strips markdown (bold, italic, headers, bullet syntax) before TTS.
- `DomainTranslations.normalizeLang()` maps language names/codes to normalized codes (`en`, `hi`, `gu`).
- Per-item play/loading state tracked by string ID (`isItemPlaying(id)`, `isItemLoading(id)`).
- `toggle(id, text, langCode, {api})` — play if not playing, stop if playing the same item, switch if playing different item. The optional `api` parameter is required to use the Google Cloud path; omitting it forces on-device fallback.
- TTS is used in `ResultDetailSheet` (full recommendation) and `WeatherScreen` (advisory). Web `WeatherPage` also uses TTS via `POST /tts`.
- Backend `tts.py` caches audio by `sha256(lang_code + text)` in `data/audio/*.mp3`. Cache hit returns the file without calling Google API.

**Relevant code:**

- [tts_service.dart](../mobile/lib/services/tts_service.dart)
- [tts.py](../backend/src/app/api/endpoints/tts.py)

**What to improve:**

- Add cache size and age management to `data/audio` (prevent unbounded growth).
- Add rate limiting on `POST /tts` to prevent abuse.
- Avoid generating duplicate audio for semantically identical but whitespace-different text.

---

### 6.5 Offline queue and synchronization

**Status: Mostly implemented**

**What works:**

- `SyncService` queues pending scans as `SyncQueueItem` JSON (base64 image bytes + filename + location + language + `plot_id` + lat + lon + timestamp + retry metadata) in `SharedPreferences` under key `pending_leaf_scans`.
- `pendingCount()` and `getPendingItems()` expose queue state.
- `drain()` iterates the queue, calls `predictBytes()` for each item, removes successfully uploaded items, and re-queues failed items with an incremented `retryCount` and `lastAttemptAt` timestamp.
- Exponential backoff is applied during `drain()`: delay = `min(300, 2^retryCount × 5)` seconds. Items still in their cooldown window are skipped until the next drain cycle.
- `FarmerShell` listens to `onConnectivityChanged` and calls `drain()` when a non-`none` connection appears.
- Pending count is shown in the Today tab stat card.

**Known gaps:**

- `SharedPreferences` is not a durable queue; storing large base64 images can cause serialization failures or storage exhaustion on low-memory devices.
- No visible per-item status (uploading, failed, retrying) in the UI.
- No maximum retry cap; a permanently failing item re-queues indefinitely (backoff reaches and stays at the 300-second ceiling).

**Relevant code:**

- [sync_service.dart](../mobile/lib/services/sync_service.dart)
- [models/sync_queue_item.dart](../mobile/lib/models/sync_queue_item.dart)

**What to improve:**

- Migrate to SQLite (`sqflite`) for queue persistence.
- Add a maximum retry attempt count after which the item is discarded or flagged.
- Show per-item upload status in the Today screen.

---

### 6.6 Today screen

**Status: Implemented**

**What works:**

- Displays live farmer name, current weather stats (temperature, condition, humidity), pending sync count, and the latest prediction result card.
- Provides navigation to scan, history, and weather.
- Logout button.

**Relevant code:**

- [today_screen.dart](../mobile/lib/screens/today/today_screen.dart)

---

### 6.7 Weather screen (mobile)

**Status: Implemented**

**What works:**

- Displays temperature, condition, humidity, and wind speed from the live backend weather response. `wind_speed_mps` (m/s) is converted to km/h (`× 3.6`) before display.
- Shows an agricultural advisory.
- Advisory translation: first checks `weather["translations"][langCode]`, then `_dynamicTranslatedAdvisory` (fetched via `POST /weather/translate`), then `weather["advisory"]` as final fallback.
- TTS play/stop for the advisory, using `TtsService`.
- Pull-to-refresh with `RefreshIndicator`.
- Locale-aware via `DomainTranslations` for condition labels.
- Shows a "Cached observation" indicator when `weather["cached"] == true`.

**Known gaps:**

- No explicit last-updated timestamp displayed for cached data beyond the "Cached observation" badge.

**Relevant code:**

- [weather_screen.dart](../mobile/lib/screens/weather/weather_screen.dart)

**What to improve:**

- Show the last-updated timestamp for cached weather data alongside the cached badge.

---

### 6.8 Mobile dependencies and build

**Status: Buildable**

**What works:**

- `pubspec.yaml` declares all required dependencies with compatible versions:
  - `flutter_tts: ^4.2.2`, `audioplayers: ^6.1.0`, `web_socket_channel: ^3.0.3`.
  - `connectivity_plus: ^6.1.4`, `image_picker: ^1.1.2`, `shared_preferences: ^2.5.3`.
  - `http: ^1.3.0`, `http_parser: ^4.1.2`.
- SDK constraint: `>=3.4.0 <4.0.0`.
- Flutter Material Design enabled.

**Known gaps:**

- No automated tests in the mobile project.
- `flutter analyze` has not been run as part of this assessment.

**What to improve:**

- Run `flutter analyze` and fix any lints.
- Add unit tests for `Prediction.fromJson()` covering all known response shapes.
- Add widget tests for key screens.

---

## 7. Scheduled Jobs and Infrastructure

### 7.1 Redis and ARQ worker

**Status: Implemented (dual-mode: synchronous default vs. ARQ task queue)**

**What works:**

- **Mode A: Synchronous / Serverless default (`REQUIRE_REDIS=False`):** Predictions execute synchronously via `run_pipeline()`, calling the model service (Service #2) directly. Caching and deduplication use Upstash Serverless Redis REST (`sf:dedup:{hash}`). No background polling worker is required, allowing Cloud Run containers to scale to zero.
- **Mode B: Asynchronous ARQ task queue (`REQUIRE_REDIS=True`):**
  - FastAPI startup initializes an ARQ Redis pool (`core/arq.py`); stored in `app.state.arq_pool`.
  - `POST /predict` enqueues via `arq_pool.enqueue_job("process_prediction_job", ...)`. Returns `503` if pool is unavailable.
  - `worker.py` defines `WorkerSettings` with: `functions=[process_prediction_job]`, `max_jobs=2`, `job_timeout=900`, `max_tries=3`.
  - The `process_prediction_job` ARQ function runs `run_prediction_job()` in a thread executor to avoid blocking the async event loop.
  - Per-stage Redis pub/sub events are emitted and streamed over WebSocket.
- `GET /job/{job_id}` endpoint returns the ARQ job status (`complete`, `processing`, or `not_found`).
- Scheduled cron jobs in worker: `purge_orphaned_blobs_cron` (every Sunday at 03:00 UTC) and `evaluate_weather_risks` (06:00, 12:00, 18:00 UTC daily).

**Known gaps:**

- When running the ARQ worker process, it does not dynamically pick up `reload_config()` updates initiated from the FastAPI process without a worker restart.
- In ARQ mode, `max_tries=3` retries lack idempotency guards and may re-process an image, generating duplicate alerts or reviews.
- In synchronous mode (`REQUIRE_REDIS=False`), intermediate per-stage events are not published over WebSocket during execution.

**Relevant code:**

- [worker.py](../backend/src/app/worker.py)
- [core/arq.py](../backend/src/app/core/arq.py)
- [predict.py](../backend/src/app/api/endpoints/predict.py)

---

### 7.2 Storage and path management

**Status: Implemented**

**What works:**

- `core/paths.py` provides `ensure_storage_directories()`, `resolve_backend_path()`, `resolve_storage_path()` (with path traversal protection), and `storage_relative_path()`.
- Storage directories: `DATA_ROOT`, `UPLOAD_ROOT`, `PROCESSED_ROOT`, `AUDIO_ROOT` — all resolved from `settings`.
- Modular storage backend abstraction (`core/storage.py`):
  - `LocalStorageBackend`: Local filesystem storage with direct file I/O and relative URL serving.
  - `S3StorageBackend`: Object storage client supporting Google Cloud Storage (GCS) via its S3-compatible HMAC API (`https://storage.googleapis.com`) using `signature_version="s3"` for signature compatibility.
  - `get_storage()` factory instantiates the active backend based on `STORAGE_BACKEND` (`"local"`, `"s3"`, `"gcs"`).
  - Presigned URL generation for secure client media access (`storage.get_url(...)` with configurable expiration).
  - Orphaned blob purge utility (`purge_orphaned_blobs`) supporting `dry_run` previews and configurable grace periods.

**Relevant code:**

- [core/paths.py](../backend/src/app/core/paths.py)
- [core/storage.py](../backend/src/app/core/storage.py)

---

### 7.3 Proactive weather risk alerts

**Status: Implemented**

**What works:**

- `weather/proactive.py` implements the proactive microclimate alert engine (`evaluate_weather_risks`).
- Iterates all registered farms and plots with valid coordinates, fetching 5-day / 3-hour forecasts from OpenWeatherMap (up to 40 periods).
- Evaluates 3 agronomic risk rules:
  - `weather_blight_risk`: High humidity (>75%) + warm temps (20–30°C) → Fungal blight prevention warning.
  - `weather_heat_stress`: Sustained ambient temperature >38°C for ≥3 periods → Irrigation and mulching warning.
  - `weather_flood_risk`: Cumulative rainfall >20mm within 24 hours → Drainage check warning.
- **24-hour unread deduplication (`_alert_exists`):** Suppresses creating duplicate unread alerts of the same kind for the same plot if one was generated within the previous 24 hours.
- **Multi-channel execution:**
  - ARQ cron: runs at 06:00, 12:00, 18:00 UTC daily in dedicated worker environments.
  - Serverless QStash webhook: `POST /api/v1/internal-cron/weather-risk` verified with `CRON_SECRET` for Cloud Run environments.
  - Manual admin trigger: `POST /admin/weather-risk/trigger` for on-demand evaluation and validation.

**Known gaps:**

- Risk rules use static thresholds; they are not tailored per specific crop variety or growth stage.
- OpenWeatherMap forecast API quota can be consumed rapidly on instances with hundreds of registered plots (no batch geocoding or spatial clustering).

**Relevant code:**

- [weather/proactive.py](../backend/src/app/services/weather/proactive.py)
- [internal_cron.py](../backend/src/app/api/endpoints/internal_cron.py)
- [admin.py — trigger_weather_risk_job](../backend/src/app/api/endpoints/admin.py)
- [worker.py](../backend/src/app/worker.py)

**What to improve:**

- Add spatial clustering to group nearby farm plots and avoid redundant forecast API calls for the same coordinates.
- Make risk rule thresholds crop- and phenology-aware (e.g. flowering vs. vegetative stages).
- Surface proactive alert metrics (total alerts triggered, plots scanned) in `GET /admin/metrics`.

---

## 8. Testing

**Status: Partial automated coverage**

**Existing tests (`backend/tests/`):**

| File | What it tests |
|---|---|
| `test_auth.py` | Auth utility functions: password hashing, token creation/decode, token type validation (access vs. refresh), invalid token rejection. |
| `test_api.py` | Health + crops endpoint; `_public_result` serialization (strips `_` keys and `leaf_crop`); predict requires auth; feedback schema validation; weather endpoint returns 200 with temperature; admin metrics returns expected shape. |
| `test_pipeline.py` | Full pipeline smoke test (skipped when test image is absent); also runnable as a standalone script to print detailed per-stage output. |
| `test_hf_recommendation.py` | HuggingFace recommendation service live integration (skipped when `HF_TOKEN` is absent; gracefully skips on 402 Payment Required). |
| `test_observability.py` | Context stage initialization; weather degraded-state handling; recommendation rule-based fallback tagging; confidence rating and uncertainty flags; pest detector unavailable tagging; pipeline provenance and schema-version assertions. |
| `test_storage.py` | `LocalStorageBackend` save/read/URL/delete round-trip; `S3StorageBackend` instantiation; `get_storage()` factory. |
| `test_admin_users.py` | `GET /admin/users` list; `PATCH /admin/users/{id}/role` success, invalid role (422), self-demotion guard (400), last-admin demotion guard (400). |
| `test_media_auth.py` | `GET /predictions/{id}/media-url/raw` — owner allowed; stranger forbidden (403); expert allowed only when status is `pending_expert_review`; admin allowed for any scan. |
| `test_features_extended.py` | GeoJSON polygon validation: valid polygon, unclosed polygon rejected, out-of-bounds coordinates rejected; expert severity regex parsing for various string formats. |

**Existing mobile tests (`mobile/test/`):**

| File | What it tests |
|---|---|
| `widget_test.dart` | App smoke test — builds `FieldnoteApp` and asserts `MaterialApp` is present. |
| `prediction_history_test.dart` | `Prediction.fromJson()` with full structured record; legacy flat-string crop/disease without `TypeError`; failed scan record parsed without crash. |

**Coverage gaps (no automated tests):**

- Image upload validation (oversized, wrong type, malformed bytes, duplicate concurrent).
- Preprocessing quality rejection paths.
- Expert review: authorization, state transitions, concurrent submission.
- Feedback review: persistence, duplicate guard, correction merge into prediction result.
- Farm/plot: ownership enforcement, geometry edge cases beyond polygon closure/bounds.
- Admin purge and blob cleanup.
- Admin config update: persistence and hot-reload.
- Model registry: promotion gate, missing files, concurrent promotion.
- RAG retriever: retrieval correctness, safety chunk always present, no-match path.
- Translation service: batch, on-demand endpoint, HF fallback path.
- MLOps export: empty dataset, missing image files, invalid split totals, format modes.
- History: ownership isolation, pagination boundaries.
- ARQ worker job: idempotency, retry behavior, event publishing.
- Mobile: `SyncService` drain logic, `TtsService` fallback.

**Recommended test order:**

1. Add endpoint tests for: prediction lifecycle, expert review, feedback review, alert endpoints.
2. Add service tests for: preprocessing rejection, RAG retrieval, recommendation fallback, translation batch/fallback.
3. Add model registry and MLOps export tests.
4. Add worker integration test (temporary Redis, mock pipeline stages).
5. Add mobile unit tests: `SyncService`, `TtsService`.
6. Add frontend TypeScript build and API contract smoke tests.
7. Add end-to-end test: upload → prediction complete → result readable.

---

## 9. Priority Improvement Plan

### Priority 1: Close security and reliability gaps

1. Require a non-default `JWT_SECRET_KEY` at startup.
2. Remove or guard the `X-User-ID` development fallback in `get_current_user` (restrict strictly to `DEBUG=True`).
3. ~~Set `secure=True` on the refresh-token cookie for HTTPS.~~ **Done** — `auth.py` now sets `secure=True` when `ENVIRONMENT == "production"`.
4. Make ARQ retries idempotent (no duplicate alerts, reviews, or results on retry).
5. ~~Call `pipeline.reload_config()` from `PUT /admin/config`.~~ **Done** — `admin.py` calls `pipeline.reload_config()` on threshold updates and syncs to Upstash Redis REST (`sf:config:thresholds`).

### Priority 2: Improve mobile robustness

1. Replace `SharedPreferences` with SQLite for the offline scan queue to safely persist large raw image payloads.
2. ~~Preserve `plot_id`, lat, lon in queue items.~~ **Done** — `SyncQueueItem` and `enqueueBytes()` persist `plot_id`, `lat`, and `lon`.
3. ~~Add bounded retry with exponential backoff in `SyncService.drain()`.~~ **Done** — implements exponential backoff (`min(300, 2^retryCount × 5)` seconds). Add maximum attempt ceiling to prune permanently failing items.
4. Migrate JWT storage from `SharedPreferences` to `flutter_secure_storage`.
5. ~~Fix the wind speed unit label in `WeatherScreen`.~~ **Done** — `weather_screen.dart` explicitly converts m/s to km/h (`* 3.6`) before rendering.
6. ~~Remote Config via Supabase `app_config` table~~ **Done** — `RemoteConfigService` fetches `api_base_url` from Supabase and caches it locally. `ApiService.initBaseUrl()` uses a 4-level fallback chain. Backend URL cannot be changed from within the app.

### Priority 3: Expand test coverage

1. Backend endpoint tests for: prediction lifecycle, expert review, feedback review, alert.
2. Service tests for: preprocessing rejection, RAG retrieval correctness, translation fallback.
3. ~~Farm/plot geometry tests~~ **Done** — `test_features_extended.py` covers valid polygon, unclosed rejection, and out-of-bounds rejection.
4. ~~`Prediction.fromJson()` unit tests~~ **Done** — `prediction_history_test.dart` covers full record, legacy format, and failed scan.
5. Mobile unit tests: `SyncService`, `TtsService`.
6. Frontend TypeScript build and type alignment.

### Priority 4: Product and data quality

1. Expand the RAG knowledge base to cover all supported crops.
2. Merge approved feedback corrections into the public prediction result.
3. ~~Fix expert review severity parsing (accept numeric strings).~~ **Done** — regex extraction is tested and verified in `test_features_extended.py`.
4. Add server-side filters to `GET /history` (date range, crop, disease, status, plot).
5. ~~Remove hardcoded Warsaw default coordinates from `GET /weather`.~~ **Done** — `weather.py` now resolves coordinates from the user's farm profile or requires explicit `lat`/`lon`. Remove the dev Warsaw default in `predict.py` form parameters.
6. Build the full MLOps retraining loop once dataset export is validated end-to-end.

---

## 10. Reference Documents

**Markdown documentation (`Docs/`):**

| Document | Description |
|---|---|
| [Architecture.md](Architecture.md) | System architecture overview — services, data flow, infrastructure. |
| [API_Specification.md](API_Specification.md) | Full REST API reference: endpoints, request/response schemas, auth. |
| [Auth_Roles.md](Auth_Roles.md) | Authentication flows and role-based access control rules. |
| [Config_Reference.md](Config_Reference.md) | Application configuration keys, defaults, and environment variables. |
| [DATASET.md](DATASET.md) | Dataset descriptions: crops, disease classes, image sources. |
| [Deployment_Guide.md](Deployment_Guide.md) | Deployment instructions for local, staging, and production environments. |
| [mlops_training_guide.md](mlops_training_guide.md) | Model training workflow, evaluation criteria, and artifact management. |
| [MLOps_Retraining.md](MLOps_Retraining.md) | Automated retraining pipeline design and trigger conditions. |
| [Model_Cards.md](Model_Cards.md) | Model cards for crop, disease, and pest models (inputs, outputs, limits). |
| [UI_UX_Spec.md](UI_UX_Spec.md) | UI/UX specification: screens, navigation flows, component guidelines. |
| [screen_specifications.md](screen_specifications.md) | *(Superseded by `UI_UX_Spec.md`)* Original per-screen specifications. |
| [functionality-status.md](functionality-status.md) | This document — implementation status, gap analysis, and improvement plan. |

**Other files (`Docs/`):**

| File | Description |
|---|---|
| `smart_farming_roadmap_v2.pdf` | Project roadmap v2 (PDF). |
| `smart_farming_roadmap.pdf` | Original project roadmap (PDF). |
| `smart_farming_roadmap_stage10_plus.pdf` | Extended roadmap covering stage 10+ milestones (PDF). |
| `Ai-Powered-Smart-Farming.pptx` | Project presentation deck. |

---

*AI-Powered Smart Farming — Documentation*  
*Last Updated: 06 October 2026*
