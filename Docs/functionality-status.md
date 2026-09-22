# Smart Farming Functionality Status

**Assessment date:** 2026-09-22  
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

The core AI diagnosis pipeline runs end-to-end via the ARQ background worker with full per-stage event publishing:

1. The user uploads a JPEG, PNG, or WebP leaf image via `POST /predict`.
2. The backend validates, hashes, and saves the file. A synchronous quality check runs immediately; user-readable error messages are returned for blur, lighting, and no-leaf failures.
3. The prediction job is enqueued into ARQ; a placeholder DB record and `prediction_id` are returned immediately.
4. The ARQ worker runs the 9-stage pipeline: preprocessing → crop identification → decision routing → disease classification → severity estimation → pest detection → weather → recommendation → persistence. Each stage publishes a Redis live event and writes an intermediate DB snapshot.
5. A RAG retriever injects verified agronomic safety guidelines (pesticide bans, PHI constraints) into the LLM prompt.
6. If the requested language is not English, the recommendation is auto-translated via Google Cloud Translation API with an LLM fallback, and cached permanently in `prediction.result["translations"]`.
7. If disease or crop confidence is below the configured threshold, `ensure_expert_review()` automatically creates a pending expert-review record in the same transaction.
8. The final result is stored in PostgreSQL and available via REST and WebSocket.

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
- The file content is SHA-256 hashed; identical image bytes reuse the same filename on disk, and a completed prediction for the same file and plot can be returned from cache.
- Files are saved under `backend/data/uploads` via `core/paths.py`; all path logic runs through `resolve_storage_path()`, which prevents path traversal outside the configured storage root.
- A synchronous preprocessing check runs before the ARQ job is enqueued; user-readable rejection reasons (including actual sharpness and brightness scores) are returned for `failed_blur`, `failed_lighting`, and `failed_no_leaf`.
- If the ARQ pool is unavailable, a `503` is returned immediately and the prediction record is marked failed.
- Content-type headers are validated (`_ALLOWED_CONTENT_TYPES`).

**Known gaps:**

- File content is not independently verified (only content-type and extension are checked). A malformed file with a valid extension can pass initial validation.
- No idempotency key for two simultaneous identical requests arriving in parallel.
- Upload metadata such as device model, capture time, or GPS EXIF is not extracted or stored.

**Relevant code:**

- [predict.py](../backend/src/app/api/endpoints/predict.py) — upload handler, quality pre-check, ARQ enqueue
- [preprocessing/service.py](../backend/src/app/services/preprocessing/service.py) — blur/lighting/leaf detection
- [core/paths.py](../backend/src/app/core/paths.py) — path resolution and traversal protection
- [core/config.py](../backend/src/app/core/config.py) — upload size and storage roots

**What to improve:**

- Validate file bytes with a magic-number or image-decode check before persisting.
- Add idempotency protection for concurrent duplicate uploads.
- Surface content-type rejection as a clear user message.
- Add tests for oversized files, wrong content-type, duplicate concurrent uploads, and missing ARQ.

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

- Quality thresholds are embedded in service logic and must be changed in code, not config.
- No labeled test set for calibrating thresholds against real farmer photos.
- No separate heatmap or attribution artifact is produced; the processed image is the only artifact.
- Decoder/memory failures from malformed images are not explicitly handled.

**Relevant code:**

- [preprocessing/service.py](../backend/src/app/services/preprocessing/service.py)
- [preprocessing/leaf_isolator.py](../backend/src/app/services/preprocessing/leaf_isolator.py)

**What to improve:**

- Move quality thresholds to `config.yaml` so they can be tuned without code changes.
- Validate threshold values against a representative labeled test set.
- Add protective handling for malformed, truncated, or adversarial images.
- Add regression tests covering good, blurry, dark, bright, and no-leaf images.

---

### 1.3 Crop identification

**Status: Implemented**

**What works:**

- Runs the configured EfficientNet-B0 crop classifier against the processed leaf image.
- Returns crop label, confidence, and top-k probability information.
- Supported crops: Cotton, Groundnut, Pepper Bell, Potato, Tomato.
- Model file path and labels file are resolved at startup; model name and version are included in the `provenance` block of every prediction result.
- Confidence is stored in `prediction.crop_conf` for drift monitoring and expert escalation decisions.

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

- Loads the crop-specific EfficientNet disease classifier.
- Returns disease label, confidence, probability distribution, and model metadata.
- Uses the preprocessed leaf image from the shared context.
- Confidence is stored in `prediction.disease_conf` for drift monitoring and automatic expert escalation.
- Model name, version, and file are recorded in the `provenance` block.

**Known gaps:**

- No calibrated confidence calibration or uncertainty quantification.
- Model loading is done at startup; the running process must be restarted (or `reload_config()` called) to switch to a promoted model in the same process.

**Relevant code:**

- [disease_classifier/predictor.py](../backend/src/app/services/disease_classifier/predictor.py)

**What to improve:**

- Define a calibrated low-confidence policy (e.g., always escalate if confidence < N%).
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

- Supports a configured YOLO classification model for pest detection.
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

**Status: Mostly implemented**

**What works:**

- `GET /weather` fetches current weather via OpenWeatherMap (or the configured provider).
- Returns temperature, humidity, wind speed, pressure, cloudiness, and condition.
- Weather data is in-memory cached for 10 minutes per lat/lon coordinate.
- A personalized agricultural advisory is generated using the AI recommendation service, with a rule-based fallback that accounts for precipitation, high humidity, extreme heat, and cold.
- Advisory is translated on-demand: if `language` is specified, the advisory is translated via Google Cloud Translation API and cached in the in-memory weather cache.
- `POST /weather/translate` provides a standalone translation endpoint for any advisory text.
- Weather context is shared with the pipeline: the `fetch_weather` stage in `prediction_job.py` incorporates weather into the LLM recommendation prompt. External failures degrade the result gracefully (`is_degraded=True`) without failing the prediction.
- Weather provider status and degraded flag are included in the `provenance` block.
- Web `WeatherPage.tsx` auto-translates the advisory when the user switches language, with an in-flight deduplication guard.

**Known gaps:**

- The weather cache is in-process and not shared across multiple FastAPI workers or restarts.
- The cache does not invalidate on language change: the first language cached per coordinate wins.
- The `GET /weather` default lat/lon is a hardcoded Warsaw coordinate (52.2297, 21.0122) — a development artifact.

**Relevant code:**

- [weather/service.py](../backend/src/app/services/weather/service.py)
- [weather.py endpoint](../backend/src/app/api/endpoints/weather.py)
- [weather/proactive.py](../backend/src/app/services/weather/proactive.py)

**What to improve:**

- Remove the hardcoded Warsaw default; require explicit coordinates.
- Move the in-memory cache to Redis for multi-worker and restart consistency.
- Add timeout, retry, and provider rate-limit handling.
- Add tests for provider timeout, malformed response, missing API key, and translation failures.

---

### 1.9 AI recommendation with RAG safety guardrails

**Status: Mostly implemented**

**What works:**

- Builds a structured recommendation from crop, disease, severity, weather, location, and context.
- Calls a HuggingFace `Qwen/Qwen3-4B-Instruct-2507` model via the nscale provider when an `HF_TOKEN` is configured.
- A lightweight in-process RAG retriever (`services/rag/retriever.py`) performs TF-IDF cosine similarity over a curated knowledge base (6 disease/crop chunks + general safety):
  - Crops covered: Cotton (bollworm), Tomato (early blight), Rice (blast), Wheat (rust), Groundnut (leaf spot), and a general pesticide safety chunk.
  - Banned pesticides explicitly listed: Endosulfan, Monocrotophos, Methyl Parathion, Phorate, Carbaryl.
  - PHI constraints, application timing, and organic alternatives are included.
  - The general safety chunk is always included regardless of relevance score.
  - Retrieved context is injected into the LLM system prompt before every recommendation.
- Returns structured output: `immediate_action`, `treatment`, `prevention`, `monitoring`, `pesticide`, `safety_disclaimer`.
- Falls back to generic agronomic advice when the LLM is unavailable or returns invalid JSON.
- Provider, model name, prompt version, fallback status, and fallback reason are recorded in the `provenance` block.

**Known gaps:**

- RAG knowledge base covers 5 crops; Cotton, Pepper Bell, and Potato disease-specific rules are not in the knowledge base.
- No feedback loop from expert corrections back into the knowledge base.
- The LLM's structured JSON output is not formally validated by a Pydantic schema; malformed output falls back silently.

**Relevant code:**

- [recommendation/service.py](../backend/src/app/services/recommendation/service.py)
- [rag/retriever.py](../backend/src/app/services/rag/retriever.py)

**What to improve:**

- Expand the RAG knowledge base to cover all supported crops (Cotton disease, Pepper Bell disease, Potato disease, etc.).
- Add Pydantic validation for the LLM JSON output.
- Add retrieval correctness tests (query → expected chunks).
- Log which chunks were retrieved for each prediction for auditability.

---

### 1.10 Pipeline orchestration and job execution

**Status: Implemented**

**What works:**

- `predict.py` calls `_enqueue_prediction_job()` which submits the job to ARQ via `arq_pool.enqueue_job()`. If the ARQ pool is not initialized, `503` is returned immediately; no silent degradation.
- `services/prediction_job.py` is the canonical worker path. It calls all 9 stages individually, publishing a live Redis event and writing an intermediate DB snapshot after each one:
  - Stages: `preprocessing`, `crop_identification`, `decision_routing`, `disease_classification`, `severity` (+ alias `severity_calculation`), `pest_detection`, `weather`, `recommendation` (+ alias `llm_advisory`), `persistence`, final `completed`.
  - Each event includes: `stage`, `status`, `message`, `timestamp`, `duration_ms`, and a `data` snapshot of the current crop/disease/pests/severity.
- Intermediate DB writes after each stage: `prediction.result` and `prediction.crop/disease/severity_pct` columns are updated so REST polling always reflects current progress.
- `run_pipeline()` in `pipeline.py` is a synchronous fallback path used for local testing and the admin health endpoint.
- `reload_config()` is exposed and called by the model-promote endpoint to hot-reload `_CONFIG` and `_PREPROCESSOR` in the FastAPI process without a restart.
- Automatic expert escalation: if disease or crop confidence is below the configured thresholds after the pipeline completes, `ensure_expert_review()` creates a pending `ExpertReview` record transactionally.
- Auto-translation: if the requested language is not English, the recommendation is translated via `translate_recommendation_sync()` and stored in `prediction.result["translations"][lang_code]` before the final DB commit.
- Worker settings: `max_jobs=2`, `job_timeout=900` seconds, `max_tries=3`.

**Known gaps:**

- `reload_config()` only updates the in-process FastAPI state; the ARQ worker process continues using its own copy of `_CONFIG` until restarted.
- No idempotent retry: a retried job can re-process the same image, overwriting previous results and potentially duplicating alerts or reviews.
- No `/job/{job_id}` status endpoint; clients must poll `GET /predictions/{id}` to check progress.

**Relevant code:**

- [prediction_job.py](../backend/src/app/services/prediction_job.py)
- [pipeline.py](../backend/src/app/pipeline.py)
- [predict.py](../backend/src/app/api/endpoints/predict.py)
- [worker.py](../backend/src/app/worker.py)

**What to improve:**

- Implement cross-process config reload (e.g., Redis pub/sub or inotify-based config file watcher in the worker).
- Add idempotency protection so retried jobs do not duplicate results, alerts, or expert reviews.
- Add a `/job/{job_id}` status endpoint.
- Add worker health, queue depth, job latency, retry rate, and failure rate metrics.

---

## 2. Authentication and Authorization

### 2.1 Registration, login, JWT, refresh, and logout

**Status: Mostly implemented — development shortcuts active**

**What works:**

- `POST /auth/register` accepts name, phone/email, password, language, location, lat/lon, crop history, and farm details. Phone or email is required; a `409` is returned for duplicates.
- `POST /auth/login` authenticates with phone or email (`identifier` field) and password. Rate-limited to 5 requests per minute via `slowapi`.
- Passwords are hashed with `pwdlib`.
- Access tokens: HS256 JWT, 30-minute expiry. Refresh tokens: HS256 JWT, 30-day expiry.
- Both tokens use a shared `_secret_key()` function that reads `JWT_SECRET_KEY` from the environment, defaulting to `"change-this-development-secret-key-32-bytes"` when the variable is unset.
- `POST /auth/refresh` reads the `refresh_token` cookie, decodes it, and issues a new token pair. Deduplication is handled in the frontend API client.
- `POST /auth/logout` deletes the `refresh_token` cookie.
- The `get_current_user` dependency accepts a Bearer token or falls back to the `X-User-ID` request header as a development convenience. This fallback is active in the current code.
- `require_expert_role` and `require_admin_role` enforce DB-backed role checks (`user.role in ["expert", "admin"]` or `user.role == "admin"`).
- The `refresh_token` cookie is currently set with `secure=False`.
- The web API client (`client.ts`) handles automatic token refresh with deduplication and dispatches a `tokenRefreshed` event for other tabs.

**Known gaps:**

- The default JWT secret is a hard-coded development value; a missing `JWT_SECRET_KEY` in production is silently accepted.
- The `X-User-ID` fallback in `get_current_user` is active in production code paths.
- `secure=False` on the refresh-token cookie must be changed before HTTPS deployment.
- No refresh-token rotation or revocation.

**Relevant code:**

- [auth.py](../backend/src/app/api/endpoints/auth.py)
- [deps.py](../backend/src/app/api/deps.py)
- [client.ts](../frontend/src/api/client.ts)
- [AuthContext.tsx](../frontend/src/context/AuthContext.tsx)

**What to improve:**

- Fail startup when `JWT_SECRET_KEY` equals the default development value.
- Remove the `X-User-ID` fallback or limit it to an explicit `DEBUG=true` environment flag.
- Set `secure=True` on the refresh cookie for all HTTPS deployments.
- Add integration tests: register, login, refresh, logout, expired token, invalid token, role checks.

---

### 2.2 Profile management

**Status: Implemented**

**What works:**

- `GET /profile` returns the authenticated user's profile, including name, phone, email, language, role, and farm fields (location, lat/lon, crop history, farm name, area).
- `PATCH /profile` updates name, language, location, lat/lon, and crop history.
- Profile is returned on login and register as part of `AuthResponse`.
- Mobile `ApiService.getProfile()` and `updateProfile()` call these endpoints; the result is used to pre-fill the `CreatePredictionSheet` and `FarmerShell` data.

**Known gaps:**

- Password update is not supported via `/profile` (no change-password endpoint).
- Language preference is stored on the `User` model but is not automatically applied to weather or translation unless the client sends it explicitly.

**Relevant code:**

- [profile.py](../backend/src/app/api/endpoints/profile.py)
- [mobile/lib/services/api_service.dart](../mobile/lib/services/api_service.dart)

**What to improve:**

- Add a change-password endpoint.
- Add account deletion and data-export endpoints if required by the product.
- Add profile validation (name length, valid phone format, valid crop names).

---

### 2.3 Farm and plot management

**Status: Implemented**

**What works:**

- `GET /farm` returns the farmer's farm with all plots.
- `PUT /farm` creates or updates the farm with name, location, lat/lon, area, crop history, and GeoJSON boundary.
- `POST /farm/plots` creates a new plot with name, crop, area, and optional geometry.
- `PUT /farm/plots/{plot_id}` updates a plot.
- `DELETE /farm/plots/{plot_id}` removes a plot.
- Plot geometry is validated against the farm boundary using an in-process ray-casting algorithm (`_plot_inside_farm`), including tolerance on the boundary.
- Schemas `FarmRequest`, `FarmResponse`, `PlotRequest`, `PlotResponse` are Pydantic-validated.
- Mobile `FarmScreen` shows farm details and the plot list; `_showAddPlotDialog` creates plots via `createPlot()`.
- `CreatePredictionSheet` loads farm plots and shows them in a dropdown; the selected `plot_id` is sent to `predictBytes()`.

**Known gaps:**

- Farm boundary validation does not check for closed rings, self-intersections, winding order, or geographic coordinate range.
- Area is user-supplied; it is not computed from the boundary geometry.
- The mobile `FarmScreen` does not support editing farm-level details (name, location, area); only plot creation is exposed.

**Relevant code:**

- [farm.py](../backend/src/app/api/endpoints/farm.py)
- [mobile/lib/screens/farm/farm_screen.dart](../mobile/lib/screens/farm/farm_screen.dart)

**What to improve:**

- Add GeoJSON geometry validation (closed rings, self-intersections, valid coordinates).
- Add optional server-side area computation from geometry.
- Expose farm-level edit in the mobile `FarmScreen`.
- Add tests for invalid polygons, plot outside boundary, ownership isolation, and deleted farms.

---

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
- `GET /expert/reviews/{review_id}` returns full review details including raw/processed image paths and all prediction fields.
- `POST /expert/reviews/{review_id}` processes a review:
  - Persists: `decision`, `status="verified"`, `expert_id`, `farmer_guidance`, `internal_note`, `corrected_disease`, `corrected_severity`.
  - Updates `prediction.status` to `"rescan_requested"` or `"verified"`.
  - Updates `prediction.result["disease"]["label"]` and `prediction.disease` if a correction is provided. Updates `prediction.result["severity"]["percent"]` and `prediction.severity_pct` if a corrected severity is provided. `flag_modified` is called to ensure SQLAlchemy tracks the JSON mutation.
  - Creates a farmer-facing alert (with duplicate guard) of kind `"review_verified"`.
  - Optionally creates a `DatasetCandidate` record when `add_to_retraining=true`.
- Automatic low-confidence escalation: `prediction_job.py` calls `ensure_expert_review()` transactionally when disease or crop confidence is below threshold; `prediction.status` is set to `"pending_expert_review"`.
- Farmer can also manually request review via `POST /predictions/{id}/expert-request` (mobile `ResultDetailSheet` button).
- Web `ExpertQueuePage.tsx` and `ExpertReviewPage.tsx` render the queue and review forms.

**Known gaps:**

- `corrected_severity` is only persisted if the payload passes a numeric value; string inputs (e.g., `"Moderate (32%)"`) are silently ignored with a bare `except: pass`.
- No reviewer assignment or duplicate-review protection (two experts can submit reviews for the same record simultaneously).
- No state-machine enforcement: a `"verified"` review can be re-submitted.

**Relevant code:**

- [expert.py](../backend/src/app/api/endpoints/expert.py)
- [crud/expert_review.py](../backend/src/app/crud/expert_review.py)
- [prediction_job.py — ensure_expert_review call](../backend/src/app/services/prediction_job.py)
- [frontend/src/pages/ExpertQueuePage.tsx](../frontend/src/pages/ExpertQueuePage.tsx)
- [frontend/src/pages/ExpertReviewPage.tsx](../frontend/src/pages/ExpertReviewPage.tsx)

**What to improve:**

- Fix severity parsing: accept numeric strings and strip percentage / label suffixes.
- Add concurrent-submission protection (optimistic locking or a `reviewed_at IS NULL` guard).
- Add explicit state transitions and reject re-submission of already-verified reviews.
- Add authorization tests: expert cannot review another expert's submitted review.

---

### 4.2 Alerts

**Status: Implemented**

**What works:**

- `GET /alerts` returns the authenticated user's last 20 alerts, ordered by creation date, including `id`, `prediction_id`, `kind`, `severity`, `title`, `body`, `is_read`, and `created_at`.
- `POST /alerts/{alert_id}/read` marks an alert read (with ownership check).
- Alert kinds generated: `"review_verified"` (from expert review completion), weather risk alerts (from scheduled job), and prediction low-confidence alerts.
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

- `GET /admin/config` reads `crop_routing_threshold` and `expert_escalation_cutoff` from `config.yaml` (mapped from `thresholds.crop_confidence` and `thresholds.disease_confidence`).
- `PUT /admin/config` writes updated values back to `config.yaml`.
- `AdminMetricsPage.tsx` does not currently expose a config edit form; the endpoints are available but no frontend UI renders them.

**Known limitation:**

- `PUT /admin/config` writes to `config.yaml` but does **not** call `pipeline.reload_config()`. The running FastAPI process does not pick up the change until restarted.
- The ARQ worker process is always separate; it never picks up config changes from either path until restarted.

**Relevant code:**

- [admin.py — /admin/config](../backend/src/app/api/endpoints/admin.py)

**What to improve:**

- Call `pipeline.reload_config()` after `PUT /admin/config` so at least the FastAPI process picks up the change immediately.
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
- `AdminMetricsPage.tsx` queries `GET /admin/models/health` and renders a model health panel.

**Known gaps:**

- `reload_config()` only affects the FastAPI process; the ARQ worker needs a separate restart.
- No rollback endpoint (re-promote the previous version).
- No frontend form for triggering promotions; only the health panel is rendered.

**Relevant code:**

- [model_registry.py](../backend/src/app/api/endpoints/model_registry.py)
- [frontend/src/pages/AdminMetricsPage.tsx](../frontend/src/pages/AdminMetricsPage.tsx)

**What to improve:**

- Add a promotion form to the admin UI.
- Add a rollback (previous-version promote) endpoint.
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

**Status: Implemented — destructive, no dry-run**

**What works:**

- `DELETE /admin/purge` deletes all DatasetCandidate, ExpertReview, Recommendation, Feedback, Alert, Prediction, and Image records. Requires admin role.
- `DELETE /admin/blobs` removes files in `data/uploads`, `data/processed`, and `data/audio` that are not referenced by any Image record. Returns `deleted_files` count. Requires admin role.
- Scheduled weekly cleanup (`purge_orphaned_blobs_cron`) runs every Sunday at 03:00 UTC via the ARQ worker. Files newer than 1 hour are preserved (grace period for in-flight predictions).
- All storage paths use `storage_relative_path()` for normalization, preventing double-slash or OS-separator mismatches.

**Known gaps:**

- No dry-run or preview mode before deletion.
- No audit log for who triggered the purge and when.
- `DELETE /admin/purge` is irreversible with no confirmation.

**Relevant code:**

- [admin.py — /admin/purge and /admin/blobs](../backend/src/app/api/endpoints/admin.py)
- [worker.py — purge_orphaned_blobs_cron](../backend/src/app/worker.py)

**What to improve:**

- Add a dry-run mode to both admin blob cleanup and purge.
- Record who triggered the operation and when in an audit log.
- Add a required confirmation parameter to the purge endpoint.
- Add tests using temporary directories for blob cleanup.

---

## 5. Web Frontend

### 5.1 Routing, authentication, and role portals

**Status: Mostly implemented**

**What works:**

- Public routes: Landing, About/Services, Crops, Login, Register.
- Protected routes: Dashboard, Scan, Processing, Result, History, Settings, Weather, Alerts, Farm Settings, Expert Queue, Expert Review, Admin Metrics, Admin Feedback.
- `ProtectedRoute` enforces role-based access; the main shell (`Appshell.tsx`) and sidebar are role-aware.
- `AuthContext` provides `user`, `token`, `language`, `units`, and `t()` translation function throughout the app.
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
- Displays temperature, condition, humidity, wind speed, pressure, and cloudiness using the configured units.
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

- Full UI translation dictionaries in English, Hindi (`hi`), and Gujarati (`gu`) (`i18n/en.ts`, `hi.ts`, `gu.ts`).
- Curated agricultural domain lexicon for crops, diseases, pests, severity levels, weather conditions, and alert titles (`i18n/domain.ts`).
- Language preference is persisted in `localStorage` via `AuthContext`.
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
- Primary: Google Cloud TTS via backend `POST /tts`. Returns MP3 audio as base64; decoded and played with `audioplayers`.
- Fallback: `flutter_tts` on-device engine. If `gu` locale is unavailable, tries `hi-IN`, then `en-US`.
- `cleanText()` strips markdown (bold, italic, headers, bullet syntax) before TTS.
- `DomainTranslations.normalizeLang()` maps language names to codes; TTS voices: `hi-IN-Standard-A`, `gu-IN-Standard-A`, `en-IN-Standard-A`.
- Per-item play/loading state tracked by string ID (`isItemPlaying(id)`, `isItemLoading(id)`).
- `toggle(id, text, langCode)` — play if not playing, stop if playing the same item, switch if playing different item.
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

- `SyncService` queues pending scans as `SyncQueueItem` JSON (base64 image bytes + filename + location + language + timestamp) in `SharedPreferences` under key `pending_leaf_scans`.
- `pendingCount()` and `getPendingItems()` expose queue state.
- `drain()` iterates the queue, calls `predictBytes()` for each item, removes successfully uploaded items, and re-queues failed items.
- `FarmerShell` listens to `onConnectivityChanged` and calls `drain()` when a non-`none` connection appears.
- Pending count is shown in the Today tab stat card.

**Known gaps:**

- `SharedPreferences` is not a durable queue; storing large base64 images can cause serialization failures or storage exhaustion on low-memory devices.
- `plot_id`, lat, and lon are not preserved in the queue item (only location text).
- No bounded retry with backoff; a permanently failing item re-queues indefinitely.
- No visible per-item status (uploading, failed, retrying) in the UI.

**Relevant code:**

- [sync_service.dart](../mobile/lib/services/sync_service.dart)
- [models/sync_queue_item.dart](../mobile/lib/models/sync_queue_item.dart)

**What to improve:**

- Migrate to SQLite (`sqflite`) for queue persistence.
- Preserve `plot_id`, lat, lon, and a client request ID in each queue item.
- Add bounded retry with exponential backoff and a maximum attempt count.
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

- Displays temperature, condition, humidity, and wind speed from the live backend weather response.
- Shows an agricultural advisory.
- Advisory translation: first checks `weather["translations"][langCode]`, then `_dynamicTranslatedAdvisory` (fetched via `POST /weather/translate`), then `weather["advisory"]` as final fallback.
- TTS play/stop for the advisory, using `TtsService`.
- Pull-to-refresh with `RefreshIndicator`.
- Locale-aware via `DomainTranslations` for condition labels.

**Known gaps:**

- Wind speed is labeled "km/h" in the UI but the backend returns `wind_speed_mps` (meters per second). Conversion is not applied.

**Relevant code:**

- [weather_screen.dart](../mobile/lib/screens/weather/weather_screen.dart)

**What to improve:**

- Fix the wind speed unit label or apply the `m/s → km/h` conversion.
- Show the last-updated timestamp for cached weather data.

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

**Status: Implemented**

**What works:**

- FastAPI startup initializes an ARQ Redis pool (`core/arq.py`); the pool is stored in `app.state.arq_pool`.
- `POST /predict` enqueues via `arq_pool.enqueue_job("process_prediction_job", ...)`. Returns `503` if pool is unavailable.
- `worker.py` defines `WorkerSettings` with: `functions=[process_prediction_job]`, `max_jobs=2`, `job_timeout=900`, `max_tries=3`.
- Scheduled cron jobs: `purge_orphaned_blobs_cron` (every Sunday at 03:00 UTC), `evaluate_weather_risks` (06:00, 12:00, 18:00 UTC daily).
- `on_startup` configures logging so ARQ and `smart-farming.*` log records are both visible.
- The `process_prediction_job` ARQ function runs `run_prediction_job()` in a thread executor to avoid blocking the async event loop.

**Known gaps:**

- Worker process does not pick up `reload_config()` calls from the FastAPI process.
- No job-status endpoint; clients must poll `GET /predictions/{id}`.
- `max_tries=3` retries are not idempotent.

**Relevant code:**

- [worker.py](../backend/src/app/worker.py)
- [core/arq.py](../backend/src/app/core/arq.py)

---

### 7.2 Storage and path management

**Status: Implemented**

**What works:**

- `core/paths.py` provides `ensure_storage_directories()`, `resolve_backend_path()`, `resolve_storage_path()` (with traversal protection), and `storage_relative_path()`.
- Storage directories: `DATA_ROOT`, `UPLOAD_ROOT`, `PROCESSED_ROOT`, `AUDIO_ROOT` — all resolved from `settings`.
- All file-handling code in `predict.py`, `tts.py`, `admin.py`, `worker.py`, and `mlops.py` uses these helpers.

---

### 7.3 Proactive weather risk alerts

**Status: Partial**

**What works:**

- `weather/proactive.py` defines `evaluate_weather_risks` which is scheduled via ARQ cron three times per day.
- The function is designed to inspect farms/plots and create weather-related alerts.

**Known gaps:**

- Without access to the proactive service implementation details, it is unclear which farms are iterated, what thresholds are used, or whether deduplication logic is in place.
- No admin-facing last-run timestamp or manual trigger.

**Relevant code:**

- [weather/proactive.py](../backend/src/app/services/weather/proactive.py)
- [worker.py](../backend/src/app/worker.py)

**What to improve:**

- Add last-run time, success/failure status, and farms-processed count to an admin endpoint.
- Add a manual admin trigger for controlled testing.
- Add deduplication logic to prevent duplicate weather alerts per farm per day.

---

## 8. Testing

**Status: Limited automated coverage**

**Existing tests (`backend/tests/`):**

| File | What it tests |
|---|---|
| `test_auth.py` | Auth utility functions: password hashing, token creation/decode, token type validation. |
| `test_api.py` | Health + crops endpoint; `_public_result` serialization (strips `_` keys and `leaf_crop`); predict requires auth; feedback schema validation; weather endpoint returns 200 with temperature; admin metrics returns expected shape. |
| `test_pipeline.py` | Pipeline smoke test. |
| `test_hf_recommendation.py` | HuggingFace recommendation service integration test. |
| `test_observability.py` | Observability/logging test. |

**Coverage gaps (no automated tests):**

- Image upload validation (oversized, wrong type, malformed bytes, duplicate concurrent).
- Preprocessing quality rejection paths.
- Expert review: authorization, state transitions, concurrent submission, severity parsing.
- Feedback review: persistence, duplicate guard, correction merge into prediction result.
- Farm/plot: boundary validation, ownership, geometry edge cases.
- Admin purge and blob cleanup.
- Admin config update: persistence and hot-reload.
- Model registry: promotion gate, missing files, concurrent promotion.
- RAG retriever: retrieval correctness, safety chunk always present, no-match path.
- Translation service: batch, on-demand endpoint, HF fallback path.
- MLOps export: empty dataset, missing image files, invalid split totals, format modes.
- History: ownership isolation, pagination boundaries.
- ARQ worker job: idempotency, retry behavior, event publishing.
- Mobile: `Prediction.fromJson()` edge cases, `SyncService` drain logic, `TtsService` fallback.

**Recommended test order:**

1. Add endpoint tests for: prediction lifecycle, expert review, feedback review, farm geometry, alerts.
2. Add service tests for: preprocessing rejection, RAG retrieval, recommendation fallback, translation batch/fallback.
3. Add model registry and MLOps export tests.
4. Add worker integration test (temporary Redis, mock pipeline stages).
5. Add mobile unit tests: `Prediction.fromJson()`, `SyncService`, `TtsService`.
6. Add frontend TypeScript build and API contract smoke tests.
7. Add end-to-end test: upload → prediction complete → result readable.

---

## 9. Priority Improvement Plan

### Priority 1: Close security and reliability gaps

1. Require a non-default `JWT_SECRET_KEY` at startup.
2. Remove or guard the `X-User-ID` development fallback in `get_current_user`.
3. Set `secure=True` on the refresh-token cookie for HTTPS.
4. Make ARQ retries idempotent (no duplicate alerts, reviews, or results on retry).
5. Call `pipeline.reload_config()` from `PUT /admin/config` so threshold changes take effect immediately in the FastAPI process.

### Priority 2: Improve mobile robustness

1. Replace `SharedPreferences` with SQLite for the offline scan queue.
2. Preserve `plot_id`, lat, lon in queue items.
3. Add bounded retry with exponential backoff in `SyncService.drain()`.
4. Migrate JWT storage from `SharedPreferences` to `flutter_secure_storage`.
5. Fix the wind speed unit label in `WeatherScreen`.

### Priority 3: Expand test coverage

1. Backend endpoint tests for: prediction lifecycle, expert review, feedback review, farm, alert.
2. Service tests for: preprocessing rejection, RAG retrieval correctness, translation fallback.
3. Mobile unit tests: `Prediction.fromJson()`, `SyncService`, `TtsService`.
4. Frontend TypeScript build and type alignment.

### Priority 4: Product and data quality

1. Expand the RAG knowledge base to cover all supported crops.
2. Merge approved feedback corrections into the public prediction result.
3. Fix expert review severity parsing (accept numeric strings).
4. Add server-side filters to `GET /history`.
5. Remove the hardcoded Warsaw default coordinates from `GET /weather`.
6. Build the full MLOps retraining loop once dataset export is validated end-to-end.

---

## 10. Reference Documents

- [Smart Farming roadmap v2](smart_farming_roadmap_v2.md)
- [Original Smart Farming roadmap](smart_farming_roadmap.md)
- [Screen specifications](screen_specifications.md)
- [Dataset descriptions](dataset%20descriptions.txt)
- [Weather research notes](research-notes_on_how-weather-affect-on-crop.txt)
