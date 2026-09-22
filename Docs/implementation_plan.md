# Master Implementation Plan: Complete Platform Hardening, Admin Role Management, and AWS S3 Storage Migration

**Source of Truth:** [`functionality-status.md`](functionality-status.md) (Sections 1.1–7.3, Section 8 Testing Gaps, Section 9 Priorities)  
**Target AWS Bucket:** `smart-farming-data-575509634394-us-east-1-an` (Region: `us-east-1`)  
**Scope:** Backend (FastAPI, ARQ, PyTorch, OpenCV, RAG, Translation), Frontend (React/TypeScript), Mobile (Flutter), Storage, Testing, and Security.

---

## User Review & Architecture Decisions

> [!IMPORTANT]
> **Strict Media Access Control (User Feedback Applied)**:
> Leaf images (raw and preprocessed) and synthesized audio files must **never** be publicly accessible. Access is governed by strict authorization rules:
> 1. **Farmer Owner**: Access is strictly limited to the user who uploaded the leaf image.
> 2. **Reviewing Expert**: Granted read access to a prediction's media *only if* the farmer requested expert review or the prediction was auto-escalated (`status in ['pending_expert_review', 'verified', 'rescan_requested']`).
> 3. **Administrator**: Full access to all media for auditing and oversight.
> 4. **Implementation Mechanism**: Assets in S3 will remain strictly private (`private` ACL). The API will expose an authorization-checked media proxy / presigned URL generator endpoint (`GET /predictions/{id}/media/{media_type}` and `GET /predictions/{id}/media-url/{media_type}`), which validates JWT claims and DB ownership before issuing a short-lived (15-minute) pre-signed S3 GET URL.

> [!IMPORTANT]
> **Admin Role Demotion Safeguard (User Feedback Applied)**:
> - Administrators can change roles of any other user (`farmer`, `expert`, `admin`).
> - **Lockout Protection**: An administrator cannot demote their own account and cannot demote the last remaining active administrator in the database.

> [!WARNING]
> **Security Breaking Changes**:
> - `X-User-ID` identity header fallback is disabled unless explicitly running with `ENVIRONMENT=development` and `DEBUG=True`.
> - `JWT_SECRET_KEY` check fails startup in production if set to `"dev-secret-key-change-me"`.
> - Refresh token cookies enforce `secure=True` in production.

---

## Open Questions & Product Decisions

1. **Account Deletion & Data Export [2.2]**: For GDPR/data privacy compliance, should farmer account deletion hard-delete all prediction images from S3 immediately, or soft-delete with a 30-day retention grace period? *(Recommended: Soft-delete user row, queue S3 assets for purge after 30 days).*
2. **Result Sharing Export [3.4]**: Should result sharing be implemented as a client-side printable HTML/PDF report or a server-rendered PDF export? *(Recommended: Client-side printable PDF view in web, share intent with summary text and image in mobile).*
3. **Dedicated Expert Shell [5.1]**: Should experts have a completely isolated layout (e.g. `/expert/*` portal without farmer scan widgets) or retain the shared collapsible sidebar? *(Recommended: Dedicated sidebar navigation mode for experts focusing exclusively on Queue, Review History, and Agronomic Guidance).*

---

## Explicitly Deferred Items

- **Learned Segmentation Model for Severity [1.6]**: Replacing the HSV contour heuristic with a deep-learning segmentation model (e.g., Mask R-CNN or U-Net) requires collecting and labeling pixel-level polygon masks for hundreds of leaves. *Deferred to Phase 5 of the long-term AI roadmap; this plan calibrates and hardens the existing HSV heuristic with crop/disease-aware thresholds and uncertainty flags.*
- **YOLO Bounding-Box Detection for Pests [1.7]**: Converting pest classification into full bounding-box object detection requires bounding-box training annotations. *Deferred to Phase 5; this plan hardens the classification engine with clear `model_unavailable` vs `no_pest_detected` status flags and health checks.*

---

## Superseded / Consolidated Items Reference

- **Cross-Process Config Reload**: Tagged with both **`[1.10]`** and **`[4.4]`**; implemented once via Redis pub/sub channel `config_reload_events` and handled in both FastAPI and the ARQ worker.
- **Cross-Process Model Promotion Reload**: Tagged with both **`[1.10]`** and **`[4.5]`**; reuses the Redis reload signal.
- **AdminMetrics TypeScript Alignment**: Tagged with both **`[4.3]`** and **`[5.2]`**; consolidated into the frontend API types update.
- **Token Refresh & Secure Storage Lifecycle**: Tagged with both **`[6.1]`** and **`[6.3]`**; consolidated into mobile secure storage and API client interceptor.

---

## Proposed Changes File Tree

```
Smart-Farming/
├── backend/
│   ├── config.yaml                              # [MODIFY] [1.2] [4.4] Move preprocessing thresholds & model configs
│   ├── requirements.txt                         # [MODIFY] Add boto3, pillow, shapely, pytest-asyncio
│   ├── scripts/
│   │   └── migrate_to_s3.py                     # [NEW] [S3] Data migration script with dry-run and checksums
│   └── src/app/
│       ├── core/
│       │   ├── config.py                        # [MODIFY] [2.1] [S3] S3 settings, ENV checks, security flags
│       │   ├── storage.py                       # [NEW] [S3] StorageBackend, LocalStorageBackend, S3StorageBackend
│       │   └── arq.py                           # [MODIFY] [1.10] Worker health, queue depth metrics
│       ├── models/
│       │   └── alert.py                         # [MODIFY] [4.2] Add unique constraint (user_id, kind, prediction_id)
│       ├── api/
│       │   ├── deps.py                          # [MODIFY] [2.1] Remove X-User-ID in prod, JWT secret fail-fast
│       │   └── endpoints/
│       │       ├── auth.py                      # [MODIFY] [2.1] [2.2] Secure cookie, change-password endpoint
│       │       ├── profile.py                   # [MODIFY] [2.2] Profile validation, deletion/export endpoints
│       │       ├── farm.py                      # [MODIFY] [2.3] GeoJSON validation, server-side area calculation
│       │       ├── predict.py                   # [MODIFY] [1.1] [1.10] [S3] Magic-bytes, idempotency, media auth gateway, /job/{id}
│       │       ├── history.py                   # [MODIFY] [3.5] Server-side filters (crop/disease/date), cursor pagination
│       │       ├── feedback.py                  # [MODIFY] [3.6] Merge corrections to prediction.result, update path
│       │       ├── expert.py                    # [MODIFY] [4.1] Severity regex parsing, optimistic lock, state machine
│       │       ├── alerts.py                    # [MODIFY] [4.2] Alerts pagination, expiry/archival
│       │       ├── admin.py                     # [MODIFY] [4.3] [4.4] [4.7] [ADMIN] User role routes, P95 DB aggregation, dry-run
│       │       ├── model_registry.py            # [MODIFY] [1.7] [4.5] Pest model health, rollback endpoint
│       │       ├── mlops.py                     # [MODIFY] [4.6] Status enum validation, missing file warnings, size limits
│       │       ├── weather.py                   # [MODIFY] [1.8] Remove Warsaw default, Redis weather cache, rate limits
│       │       └── translation.py               # [MODIFY] [5.4] Dual-engine failure handling, expanded language codes
│       ├── services/
│       │   ├── preprocessing/
│       │   │   └── service.py                   # [MODIFY] [1.2] Config-driven thresholds, malformed image protection
│       │   ├── crop_identifier/
│       │   │   └── predictor.py                 # [MODIFY] [1.3] unsupported_crop state, uncertainty score
│       │   ├── decision_engine/
│       │   │   └── router.py                    # [MODIFY] [1.4] Enforce crop confidence threshold before routing
│       │   ├── disease_classifier/
│       │   │   └── predictor.py                 # [MODIFY] [1.5] Calibrated low-confidence policy, precision tracking
│       │   ├── severity/
│       │   │   └── estimator.py                 # [MODIFY] [1.6] Disease-aware thresholds, uncertainty quality flag
│       │   ├── pest_detector/
│       │   │   └── predictor.py                 # [MODIFY] [1.7] Status distinguishing no_pest vs model_unavailable
│       │   ├── rag/
│       │   │   └── retriever.py                 # [MODIFY] [1.9] 5-crop knowledge base expansion, Pydantic validation, retrieval logging
│       │   ├── weather/
│       │   │   └── proactive.py                 # [MODIFY] [7.3] Alert deduplication, last-run metrics, manual trigger
│       │   └── prediction_job.py                # [MODIFY] [1.10] [S3] Idempotent retry, skip finished stages, S3 upload
│       └── worker.py                            # [MODIFY] [1.10] [4.4] Redis pub/sub config reload listener, S3 orphan cleanup
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts                        # [MODIFY] [5.2] Request timeout, retry with backoff
│   │   │   ├── admin.ts                         # [MODIFY] [4.3] [4.5] [7.3] [ADMIN] User roles, model rollback, weather trigger
│   │   │   └── types.ts                         # [MODIFY] [4.3] [5.2] Align AdminMetrics, UserAdminSummary, Prediction
│   │   ├── components/
│   │   │   ├── Appshell.tsx                     # [MODIFY] [5.1] Role-aware portal navigation, expert shell toggle
│   │   │   └── ProtectedRoute.tsx               # [MODIFY] [5.1] Strict role route maps
│   │   └── pages/
│   │       ├── ScanPage.tsx                     # [MODIFY] [3.1] Size limits alignment, upload cancellation, progress feedback
│   │       ├── ProcessingPage.tsx               # [MODIFY] [3.3] WebSocket live updates with polling fallback
│   │       ├── PredictionResultPage.tsx         # [MODIFY] [3.4] Model confidence labeling, printable/shareable result
│   │       ├── HistoryPage.tsx                  # [MODIFY] [3.5] Server-side filter controls, pagination UI, empty state
│   │       ├── AdminMetricsPage.tsx             # [MODIFY] [4.3] [4.4] [4.5] Date/crop filters, config editor, promotion form
│   │       └── AdminUsersPage.tsx               # [NEW] [ADMIN] User management table, search, role change modal
└── mobile/
    ├── pubspec.yaml                             # [MODIFY] Add sqflite, path, flutter_secure_storage
    └── lib/
        ├── i18n/
        │   └── domain_translations.dart         # [MODIFY] [5.4] Expanded disease/pest vocabulary
        ├── models/
        │   ├── prediction.dart                  # [MODIFY] [3.4] Confidence clarity, parsing robustness
        │   └── sync_queue_item.dart             # [MODIFY] [6.5] Include plot_id, lat, lon, request_id, file path
        ├── services/
        │   ├── api_service.dart                 # [MODIFY] [6.1] [6.3] Token refresh on 401, global timeout, structured errors
        │   ├── sync_service.dart                # [MODIFY] [6.5] SQLite table, bounded exponential backoff retry
        │   └── tts_service.dart                 # [MODIFY] [6.4] Audio cache cleanup, rate-limit resilience, deduplication
        └── screens/
            ├── auth/
            │   ├── auth_wrapper.dart            # [MODIFY] [6.1] flutter_secure_storage integration
            │   └── login_screen.dart            # [MODIFY] [6.1] Registration form validation
            ├── scan/
            │   ├── create_prediction_sheet.dart # [MODIFY] [3.2] Camera/storage permissions, discard cleanup
            │   └── processing_sheet.dart        # [MODIFY] [3.2] [3.3] WebSocket reconnect with exponential backoff
            ├── farm/
            │   └── farm_screen.dart             # [MODIFY] [2.3] Farm-level edit dialog
            ├── today/
            │   └── today_screen.dart            # [MODIFY] [6.5] Per-item upload status indicator
            └── weather/
                └── weather_screen.dart          # [MODIFY] [6.7] Wind speed km/h conversion, cached timestamp
```

---

## Detailed Component Breakdown

### Component 1: Cloud Storage Abstraction, S3 Migration, and Media Authorization Gateway

#### [NEW] [storage.py](file:///z:/Projects/Smart-Farming/backend/src/app/core/storage.py)
- **`StorageBackend` Interface**: Abstract methods `save(bytes, key, content_type)`, `get(key)`, `get_url(key, expires_in)`, `delete(key)`, `exists(key)`, `list_objects(prefix)`.
- **`LocalStorageBackend`**: Preserves local filesystem storage for dev environments; maps keys to `backend/data/*`.
- **`S3StorageBackend`**: Uses `boto3.client('s3', region_name='us-east-1')`.
  - Target bucket: `smart-farming-data-575509634394-us-east-1-an`.
  - Keys organized under prefixes: `uploads/{hash}.{ext}`, `processed/{hash}.{ext}`, `audio/{hash}.mp3`, `exports/{id}.zip`.
  - `get_url(key, expires_in=900)`: Generates AWS S3 pre-signed GET URL valid for 15 minutes.
  - All uploaded objects set with `ServerSideEncryption='AES256'` and `ACL='private'`.

#### [MODIFY] [config.py](file:///z:/Projects/Smart-Farming/backend/src/app/core/config.py)
- Add `STORAGE_BACKEND: str = Field(default="local")` (`"local"` or `"s3"`).
- Add `AWS_S3_BUCKET: str = Field(default="smart-farming-data-575509634394-us-east-1-an")`.
- Add `AWS_REGION: str = Field(default="us-east-1")`.
- Add `AWS_ACCESS_KEY_ID: str | None = None` and `AWS_SECRET_ACCESS_KEY: str | None = None`.
- Add `S3_PRESIGNED_EXPIRY_SECONDS: int = 900`.

#### [MODIFY] [predict.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/predict.py)
- **Media Authorization Gateway**:
  - Add `GET /predictions/{prediction_id}/media/{media_type}`:
    - `media_type`: `"raw"`, `"processed"`, `"audio"`.
    - Authorization rule:
      ```python
      prediction = session.get(Prediction, prediction_id)
      is_owner = prediction.user_id == current_user_id
      is_admin = current_user.role == "admin"
      is_reviewing_expert = (current_user.role == "expert" and 
                             (prediction.status in ["pending_expert_review", "verified", "rescan_requested"] or
                              prediction.expert_review is not None))
      if not (is_owner or is_admin or is_reviewing_expert):
          raise HTTPException(status_code=403, detail="Access denied. You are not authorized to view this prediction's media assets.")
      ```
    - In S3 mode, generates a 15-minute pre-signed redirect or streams bytes.
  - Add `GET /predictions/{prediction_id}/media-url/{media_type}` returning `{"url": presigned_url, "expires_in": 900}` for direct client media loading.

#### [NEW] [migrate_to_s3.py](file:///z:/Projects/Smart-Farming/backend/scripts/migrate_to_s3.py)
- Migration CLI supporting `--dry-run`, `--batch-size`, `--verify-checksum`, `--delete-local`:
  1. Walks `backend/data/uploads`, `backend/data/processed`, `backend/data/audio`.
  2. Uploads each file to S3 bucket `smart-farming-data-575509634394-us-east-1-an` under respective prefix.
  3. Computes MD5 hash locally and verifies against S3 ETag.
  4. Updates database columns `Image.raw_path`, `Image.processed_path`, and `Prediction.result` JSON to reflect S3 keys.
  5. Produces `s3_migration_report.json` detailing migrated, verified, and failed files.

---

### Component 2: Admin User Management & Role Switching

#### [MODIFY] [admin.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/admin.py)
- **`GET /admin/users`**:
  - Query parameters: `skip: int = 0`, `limit: int = 20`, `role: str | None = None`, `search: str | None = None`.
  - Returns total count and list of users with id, name, phone, email, language, role, created_at, scan_count, and farm location.
- **`PATCH /admin/users/{user_id}/role`**:
  - Request schema: `AdminRoleUpdateRequest(role: str, reason: str | None)`.
  - Allowed roles: `farmer`, `expert`, `admin`.
  - **Self-Demotion Guard**:
    ```python
    if user_id == current_user_id and payload.role != "admin":
        raise HTTPException(status_code=400, detail="Security violation: Administrators cannot demote their own account.")
    ```
  - **Last-Admin Guard**:
    ```python
    target_user = session.get(User, user_id)
    if target_user.role == "admin" and payload.role != "admin":
        admin_count = session.query(func.count(User.id)).filter(User.role == "admin").scalar()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Operation blocked: Cannot demote the last remaining administrator on the platform.")
    ```
  - Logs role change event: `admin_role_change_audit(admin_id, target_user_id, old_role, new_role, reason)`.

#### [MODIFY] [admin.ts](file:///z:/Projects/Smart-Farming/frontend/src/api/admin.ts) & [types.ts](file:///z:/Projects/Smart-Farming/frontend/src/api/types.ts)
- Add `UserAdminSummary` interface to `types.ts`.
- Add `getAdminUsers(token, params)` and `updateUserRole(token, userId, role, reason)` in `admin.ts`.

#### [NEW] [AdminUsersPage.tsx](file:///z:/Projects/Smart-Farming/frontend/src/pages/AdminUsersPage.tsx)
- Complete UI for user administration:
  - Search bar (name/email/phone) and role filter tabs (`All`, `Farmers`, `Experts`, `Admins`).
  - Data table displaying User, Contact, Role badge, Total Scans, Joined date, and Action button.
  - "Change Role" modal with dropdown selector, role descriptions, reason input, and warning dialog. Disabled for the current user's own row.

---

### Component 3: Core AI Diagnosis Pipeline Hardening (Sections 1.1–1.10)

#### 1.1 Image upload and request validation
- **[MODIFY] [predict.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/predict.py)**:
  - **[1.1]** Magic-byte verification: Read first 2KB of upload and run `PIL.Image.open(io.BytesIO(head)).verify()`. Reject non-image byte streams with `400 Bad Request` and message `"The uploaded file is not a valid image format."`.
  - **[1.1]** Concurrent duplicate idempotency: Compute SHA-256 hash of image bytes. Use a Redis distributed lock `lock:predict:{user_id}:{sha256}` (TTL 30s) during upload. If an in-flight prediction with identical hash and user is running, return the existing in-flight `prediction_id` instead of spawning duplicate ARQ jobs.
  - **[1.1]** Surface content-type rejection: Explicit error `"Unsupported file format '{content_type}'. Allowed types: JPEG, PNG, WebP."`.

#### 1.2 Preprocessing and quality checks
- **[MODIFY] [config.yaml](file:///z:/Projects/Smart-Farming/backend/config.yaml)** & **[MODIFY] [preprocessing/service.py](file:///z:/Projects/Smart-Farming/backend/src/app/services/preprocessing/service.py)**:
  - **[1.2]** Move blur Laplacian threshold (`blur_threshold: 100.0`) and brightness range (`min_brightness: 40.0`, `max_brightness: 220.0`) to `config.yaml` under `preprocessing:` block.
  - **[1.2]** Malformed/adversarial image guard: Wrap `cv2.imdecode` in `try...except cv2.error` and check for decompression bombs (`PIL.Image.MAX_IMAGE_PIXELS = 20_000_000`).
  - **[1.2]** Validate thresholds against labeled set via regression test `test_preprocessing_thresholds()`.

#### 1.3 Crop identification
- **[MODIFY] [crop_identifier/predictor.py](file:///z:/Projects/Smart-Farming/backend/src/app/services/crop_identifier/predictor.py)**:
  - **[1.3]** If top-1 crop confidence is below `thresholds.crop_confidence`: set `context["crop"]["status"] = "unsupported_crop"`, set `context["crop"]["uncertainty"] = round(1.0 - conf, 3)`.
  - **[1.3]** Expose `crop.uncertainty` and `crop.is_unsupported` flags in the returned public result.

#### 1.4 Crop-specific disease routing
- **[MODIFY] [decision_engine/router.py](file:///z:/Projects/Smart-Farming/backend/src/app/services/decision_engine/router.py)**:
  - **[1.4]** Enforce routing gate: If `crop.status == "unsupported_crop"`, skip disease classification, set `status["disease_classification"] = "skipped"`, set message to `"Crop confidence too uncertain to route to a disease model"`, and trigger expert review escalation.

#### 1.5 Disease classification
- **[MODIFY] [disease_classifier/predictor.py](file:///z:/Projects/Smart-Farming/backend/src/app/services/disease_classifier/predictor.py)**:
  - **[1.5]** Calibrated low-confidence policy: If disease confidence < `thresholds.disease_confidence` (default 0.70), mark `disease.is_uncertain = True`.
  - **[1.5]** Add per-crop precision/recall/F1 calculation helper in `admin.py` drawing from verified expert review data vs original model predictions.

#### 1.6 Severity estimation
- **[MODIFY] [severity/estimator.py](file:///z:/Projects/Smart-Farming/backend/src/app/services/severity/estimator.py)**:
  - **[1.6]** Crop/disease-aware thresholds: Load HSV saturation/value ranges per crop from `config.yaml` (e.g. Tomato Early Blight dark necrotic lesions vs Cotton Leaf Curl yellowing).
  - **[1.6]** Return `severity.quality_flag = "low_contrast"` when leaf mask area is < 15% of frame or lighting variance is poor.

#### 1.7 Pest detection
- **[MODIFY] [pest_detector/predictor.py](file:///z:/Projects/Smart-Farming/backend/src/app/services/pest_detector/predictor.py)** & **[MODIFY] [model_registry.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/model_registry.py)**:
  - **[1.7]** Explicit status field: `pest.status` set to `"no_pest_detected"` (model ran successfully, no class > 0.40) vs `"model_unavailable"` (weights missing or ultralytics uninstalled).
  - **[1.7]** Include pest detector weights file check in `GET /admin/models/health`.

#### 1.8 Weather data and advisory
- **[MODIFY] [weather.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/weather.py)**:
  - **[1.8]** Remove Warsaw default coordinates (52.2297, 21.0122). Require `lat` and `lon` query params; if missing, look up `user.farm.latitude` and `user.farm.longitude`. If no farm coordinates exist, return `400 Bad Request` with `"Coordinates required or configure your farm location."`.
  - **[1.8]** Move weather caching to Redis (`SETEX weather:{lat_2dp}:{lon_2dp} 600 <json>`).
  - **[1.8]** Add exponential backoff retry (3 attempts) on OpenWeatherMap API calls with timeout of 5.0 seconds.

#### 1.9 AI recommendation with RAG safety guardrails
- **[MODIFY] [rag/retriever.py](file:///z:/Projects/Smart-Farming/backend/src/app/services/rag/retriever.py)** & **[MODIFY] [recommendation/service.py](file:///z:/Projects/Smart-Farming/backend/src/app/services/recommendation/service.py)**:
  - **[1.9]** Expand agronomic knowledge base to all 5 crops: add curated rules for Potato (Late Blight, Metalaxyl restrictions), Pepper Bell (Anthracnose, Copper oxychloride), Groundnut (Tikka disease, Mancozeb), Cotton (Bollworm, Spinosad), and Tomato.
  - **[1.9]** Pydantic schema validation: Parse LLM output into `RecommendationOutputSchema(immediate_action, treatment, prevention, monitoring, chemical_safety)`.
  - **[1.9]** Log retrieved chunk IDs in `prediction.result["provenance"]["rag_chunks"]`.

#### 1.10 Pipeline orchestration and ARQ execution
- **[MODIFY] [worker.py](file:///z:/Projects/Smart-Farming/backend/src/app/worker.py)** & **[MODIFY] [prediction_job.py](file:///z:/Projects/Smart-Farming/backend/src/app/services/prediction_job.py)**:
  - **[1.10, 4.4, 4.5]** Worker Redis pub/sub listener: Worker subscribes to `config_reload_events` on startup; invokes `reload_config()` when notified without worker restart.
  - **[1.10]** Idempotent ARQ retries: `run_prediction_job()` inspects `prediction.result["stages"]`. Any stage marked `"completed"` is reused; intermediate DB commits do not re-create alerts or duplicate `ExpertReview` rows.
  - **[1.10]** Add endpoint `GET /predictions/jobs/{job_id}` returning ARQ job status (`queued`, `in_progress`, `complete`, `failed`).
  - **[1.10]** Add ARQ queue depth and worker health metrics in `GET /admin/metrics`.

---

### Component 4: Authentication, Profile, and Farm Boundaries (Sections 2.1–2.3)

#### 2.1 Auth hardening
- **[MODIFY] [deps.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/deps.py)** & **[MODIFY] [auth.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/auth.py)**:
  - **[2.1]** Fail fast on default secret: In `deps.py`, if `settings.ENVIRONMENT != "development"` and `_secret_key() == "change-this-development-secret-key-32-bytes"`, raise `RuntimeError("Production startup aborted: Insecure default JWT_SECRET_KEY detected.")`.
  - **[2.1]** Restrict `X-User-ID`:
    ```python
    if not credentials:
        if settings.ENVIRONMENT == "development" and x_user_id:
            return x_user_id.strip()
        raise HTTPException(status_code=401, detail="Bearer token required.")
    ```
  - **[2.1]** Cookie security: Set `response.set_cookie("refresh_token", ..., secure=(settings.ENVIRONMENT == "production"), samesite="strict")`.

#### 2.2 Profile management
- **[MODIFY] [profile.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/profile.py)** & **[MODIFY] [auth.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/auth.py)**:
  - **[2.2]** Add `POST /auth/change-password` requiring `old_password` and `new_password` (min 8 chars).
  - **[2.2]** Add `DELETE /profile` (account deletion) and `GET /profile/export` (export personal data as JSON).
  - **[2.2]** Profile input validation: `name` length (2–100 chars), regex phone validation (`^\+?[0-9]{10,15}$`), and crop names validated against supported list.

#### 2.3 Farm and plot geometry
- **[MODIFY] [farm.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/farm.py)**:
  - **[2.3]** GeoJSON geometry validation: Validate linear rings are closed (`coords[0] == coords[-1]`), minimum 4 coordinate pairs, no self-intersections using `shapely.geometry.Polygon.is_valid`, and coordinates in valid WGS84 range (`-180 <= lon <= 180`, `-90 <= lat <= 90`).
  - **[2.3]** Server-side area computation: Compute geodesic polygon area in acres using `pyproj.Geod` or spherical geometry if user leaves `area_acres` blank.
  - **[2.3]** Mobile farm edit: Expose farm details update in mobile `FarmScreen` (`[6.1]`).

---

### Component 5: Scan Flow, Processing, Results, History, Feedback (Sections 3.1–3.6)

#### 3.1 & 3.2 Web and mobile scan flow
- **[MODIFY] [ScanPage.tsx](file:///z:/Projects/Smart-Farming/frontend/src/pages/ScanPage.tsx)**:
  - **[3.1]** Align client-side compression target to 8MB (under the 10MB server limit).
  - **[3.1]** Add `AbortController` cancellation button during upload with progress percentage bar.
  - **[3.1]** Display server-side rejection reason modal with actionable tips (e.g. hold camera steady, move to daylight).
- **[MODIFY] [create_prediction_sheet.dart](file:///z:/Projects/Smart-Farming/mobile/lib/screens/scan/create_prediction_sheet.dart)**:
  - **[3.2]** Camera/storage runtime permission handling via `permission_handler` with user guidance dialog.
  - **[3.2]** Clean up temporary cache images on sheet dismiss without submission.

#### 3.3 Live updates and WebSocket lifecycle
- **[MODIFY] [ProcessingPage.tsx](file:///z:/Projects/Smart-Farming/frontend/src/pages/ProcessingPage.tsx)** & **[MODIFY] [processing_sheet.dart](file:///z:/Projects/Smart-Farming/mobile/lib/screens/scan/processing_sheet.dart)**:
  - **[3.3]** Web processing page WebSocket integration (`ws://.../ws/predictions/{id}`) with auto-fallback to 1.5s polling.
  - **[3.3]** Mobile WebSocket reconnect with exponential backoff (1s, 2s, 4s, max 3 tries).
  - **[3.3]** Ensure WebSocket subscription is cleanly closed in `dispose()` / `useEffect` cleanup.

#### 3.4 Results display and model confidence labeling
- **[MODIFY] [PredictionResultPage.tsx](file:///z:/Projects/Smart-Farming/frontend/src/pages/PredictionResultPage.tsx)** & **[MODIFY] [result_detail_sheet.dart](file:///z:/Projects/Smart-Farming/mobile/lib/screens/scan/result_detail_sheet.dart)**:
  - **[3.4]** Label confidence values as `"Model Diagnostic Confidence"` with tooltip clarifying it represents probabilistic AI assessment.
  - **[3.4]** Add result sharing: Print/PDF report view on web; native Share Intent on mobile.

#### 3.5 Prediction history
- **[MODIFY] [history.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/history.py)** & **[MODIFY] [HistoryPage.tsx](file:///z:/Projects/Smart-Farming/frontend/src/pages/HistoryPage.tsx)**:
  - **[3.5]** Server-side filters: `GET /history?crop=Tomato&disease=Blight&status=completed&start_date=2026-01-01&plot_id=12`.
  - **[3.5]** Keyset / cursor pagination using `last_id: int` for efficient large-table queries.
  - **[3.5]** Web and mobile UI filter toolbar with active filter badges and pagination controls.

#### 3.6 Farmer feedback
- **[MODIFY] [feedback.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/feedback.py)**:
  - **[3.6]** Merge approved feedback corrections: When expert reviews feedback and approves correction, update `prediction.disease = corrected_label` and `prediction.result["disease"]["label"] = corrected_label`.
  - **[3.6]** Allow farmer to update existing feedback (`PUT /feedback/{id}`) instead of rejecting with conflict.
  - **[3.6]** Enforce ownership: Farmers can only submit feedback on their own predictions.

---

### Component 6: Expert Queue, Alerts, Metrics, MLOps, Cleanup (Sections 4.1–4.7, 7.3)

#### 4.1 Expert review queue
- **[MODIFY] [expert.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/expert.py)**:
  - **[4.1]** Severity regex parsing: Extract numeric float from strings like `"Moderate (32%)"` or `"32%"` (`re.search(r'\d+(\.\d+)?', str_val)`).
  - **[4.1]** Concurrent submission lock: Use optimistic locking on `ExpertReview.updated_at` / `status == "pending"`; return `409 Conflict` if another expert already verified the item.
  - **[4.1]** State machine: Reject review submission on already-verified items (`status != 'pending'`).
  - **[4.1]** Authorization: Experts cannot edit or overwrite another expert's finalized review.

#### 4.2 Alerts management
- **[MODIFY] [alerts.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/alerts.py)** & **[MODIFY] [models/alert.py](file:///z:/Projects/Smart-Farming/backend/src/app/models/alert.py)**:
  - **[4.2]** Add pagination: `GET /alerts?offset=0&limit=20`.
  - **[4.2]** Unique constraint / deduplication: Database constraint on `(user_id, kind, prediction_id)` preventing duplicate alert rows.
  - **[4.2]** Alert expiry/archival: Scheduled cron job to archive alerts older than 90 days.

#### 4.3 Admin metrics
- **[MODIFY] [admin.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/admin.py)**:
  - **[4.3]** Use PostgreSQL `func.percentile_cont(0.95).within_group(Prediction.duration_ms)` for P95 duration calculation.
  - **[4.3]** Add query filters `start_date`, `end_date`, `crop` to `GET /admin/metrics`.
  - **[4.3]** Explicitly label `farmer_feedback_accuracy` vs `expert_validated_accuracy` in the JSON response.

#### 4.4 Admin configuration
- **[MODIFY] [admin.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/admin.py)**:
  - **[4.4]** Trigger `pipeline.reload_config()` immediately on `PUT /admin/config`.
  - **[4.4]** Publish Redis event `config_reload_events` to notify worker processes.
  - **[4.4]** Validate threshold boundaries: `crop_confidence` and `disease_confidence` must be between `0.1` and `0.99`.

#### 4.5 Model registry
- **[MODIFY] [model_registry.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/model_registry.py)**:
  - **[4.5]** Add `POST /admin/models/rollback` to promote the immediately preceding active model version.
  - **[4.5]** Add promotion form in frontend `AdminMetricsPage.tsx`.

#### 4.6 MLOps dataset export
- **[MODIFY] [mlops.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/mlops.py)**:
  - **[4.6]** Validate `status` against `['pending_review', 'added_to_dataset', 'rejected']`.
  - **[4.6]** Add warning list in `metadata.json` for candidates whose image file was missing from disk/S3.
  - **[4.6]** Enforce export maximum candidate limit (e.g., 5,000 images per export) to prevent out-of-memory errors.

#### 4.7 Database purge and blob cleanup
- **[MODIFY] [admin.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/admin.py)**:
  - **[4.7]** Add `dry_run: bool = True` query parameter to `DELETE /admin/blobs` and `DELETE /admin/purge`.
  - **[4.7]** Require payload `{"confirmation": "PURGE_ALL_DATA"}` on `DELETE /admin/purge`.
  - **[4.7]** Log all deletion operations with administrator ID and file counts.

#### 7.3 Proactive weather risk jobs
- **[MODIFY] [weather/proactive.py](file:///z:/Projects/Smart-Farming/backend/src/app/services/weather/proactive.py)** & **[MODIFY] [admin.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/admin.py)**:
  - **[7.3]** Deduplication: Check if an alert for `(user_id, 'weather_risk', today)` already exists before inserting.
  - **[7.3]** Track execution stats: Save last-run timestamp, status, and farms-processed count in Redis key `weather_cron:status`.
  - **[7.3]** Add `POST /admin/weather-risk/trigger` for manual on-demand execution.

---

### Component 7: Web Frontend Hardening (Sections 5.1, 5.2, 5.4)

#### 5.1 Routing, authentication, and role portals
- **[MODIFY] [ProtectedRoute.tsx](file:///z:/Projects/Smart-Farming/frontend/src/components/ProtectedRoute.tsx)** & **[MODIFY] [Appshell.tsx](file:///z:/Projects/Smart-Farming/frontend/src/components/Appshell.tsx)**:
  - **[5.1]** Role Route Matrix: Enforce explicit route permission table (Farmers: `/dashboard`, `/scan`, `/history`, `/weather`, `/farm`; Experts: `/expert/queue`, `/expert/reviews/:id`; Admins: `/admin/metrics`, `/admin/users`, `/admin/feedback`).
  - **[5.1]** Provide a dedicated Expert Shell layout emphasizing the review queue.

#### 5.2 Web API client
- **[MODIFY] [client.ts](file:///z:/Projects/Smart-Farming/frontend/src/api/client.ts)** & **[MODIFY] [types.ts](file:///z:/Projects/Smart-Farming/frontend/src/api/types.ts)**:
  - **[5.2]** Add 15-second request timeout and 2 automatic retries for idempotent `GET` requests on network errors.
  - **[5.2]** Reconcile `AdminMetrics` type to match backend schema.

#### 5.4 Translation service
- **[MODIFY] [translation.py](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/translation.py)**:
  - **[5.4]** Handle dual-engine translation failure: If both Google and HuggingFace fail, return the canonical English text with `"translation_status": "degraded"`.

---

### Component 8: Mobile Client Hardening (Sections 6.1–6.8)

#### 6.1 Auth and secure storage
- **[MODIFY] [auth_wrapper.dart](file:///z:/Projects/Smart-Farming/mobile/lib/screens/auth/auth_wrapper.dart)** & **[MODIFY] [api_service.dart](file:///z:/Projects/Smart-Farming/mobile/lib/services/api_service.dart)**:
  - **[6.1]** Replace `SharedPreferences` token storage with `flutter_secure_storage`.
  - **[6.1, 6.3]** Implement transparent token refresh on `401 Unauthorized` in `api_service.dart`.
  - **[6.1]** Add registration form validation (phone format, password strength, required fields).

#### 6.3 API client resilience
- **[MODIFY] [api_service.dart](file:///z:/Projects/Smart-Farming/mobile/lib/services/api_service.dart)**:
  - **[6.3]** Add structured exceptions: `NetworkException`, `AuthException`, `ValidationException`, `ServerException`.
  - **[6.3]** Global 15s timeout across all HTTP calls.

#### 6.4 Audio cache management
- **[MODIFY] [tts_service.dart](file:///z:/Projects/Smart-Farming/mobile/lib/services/tts_service.dart)**:
  - **[6.4]** Mobile cache size limit: Maintain max 50MB audio cache on device; delete oldest files when full.
  - **[6.4]** Client-side rate limit on TTS requests.

#### 6.5 SQLite offline queue
- **[MODIFY] [sync_service.dart](file:///z:/Projects/Smart-Farming/mobile/lib/services/sync_service.dart)**:
  - **[6.5]** Replace `SharedPreferences` with `sqflite` table `pending_scans(id, file_path, plot_id, lat, lon, location, language, created_at, attempts)`.
  - **[6.5]** Bounded retry: Exponential backoff (1m, 2m, 4m, max 5 attempts). Mark permanently failed after 5 tries.
  - **[6.5]** Update `TodayScreen` to display per-item upload status.

#### 6.7 Weather screen
- **[MODIFY] [weather_screen.dart](file:///z:/Projects/Smart-Farming/mobile/lib/screens/weather/weather_screen.dart)**:
  - **[6.7]** Convert wind speed: `wind_speed_mps * 3.6` and label as `"km/h"` (or display raw `m/s`).
  - **[6.7]** Display cached timestamp (e.g. `"Updated 5 mins ago"`).

#### 6.8 Mobile build health
- **[MODIFY] [prediction.dart](file:///z:/Projects/Smart-Farming/mobile/lib/models/prediction.dart)**:
  - **[6.8]** Verify null-safety across all nested maps in `Prediction.fromJson()`.

---

## Component 9: Comprehensive Testing Plan (Section 8 & Cross-Cutting)

Address every automated testing gap enumerated in Section 8 and per-section test requirements.

| Test File | Sections Tested | What It Covers |
|---|---|---|
| `backend/tests/test_storage.py` | `[S3]`, `[1.1]` | Local vs S3 storage operations, pre-signed URL generation, path safety. |
| `backend/tests/test_media_auth.py` | `[S3]`, `[User Request]` | Media Gateway: owner allowed, reviewing expert allowed, non-owner rejected (403), admin allowed. |
| `backend/tests/test_admin_users.py` | `[ADMIN]` | List users, role promotion, self-demotion guard (400), last-admin guard (400). |
| `backend/tests/test_upload_validation.py` | `[1.1]` | Magic bytes rejection, oversized uploads, concurrent duplicate lock, content-type message. |
| `backend/tests/test_preprocessing_thresholds.py` | `[1.2]` | Config-driven blur/brightness thresholds, corrupt image protection. |
| `backend/tests/test_crop_routing.py` | `[1.3]`, `[1.4]` | `unsupported_crop` detection, confidence gate skipping disease stage. |
| `backend/tests/test_disease_classifier.py` | `[1.5]` | Calibrated low-confidence flagging, missing model handling. |
| `backend/tests/test_severity.py` | `[1.6]` | Crop-specific HSV ranges, low-contrast quality flag. |
| `backend/tests/test_pest_detection.py` | `[1.7]` | `no_pest_detected` vs `model_unavailable`, health check. |
| `backend/tests/test_weather.py` | `[1.8]`, `[7.3]` | Coordinate enforcement, Redis caching, timeout retry, proactive cron deduplication. |
| `backend/tests/test_rag.py` | `[1.9]` | 5-crop rule retrieval, Pydantic validation, chunk audit logging. |
| `backend/tests/test_pipeline_worker.py` | `[1.10]`, `[4.4]` | ARQ retry idempotency, stage skip, Redis pub/sub config reload. |
| `backend/tests/test_auth_security.py` | `[2.1]`, `[2.2]` | Prod secret check, `X-User-ID` rejection in prod, secure cookie, change-password. |
| `backend/tests/test_farm_geometry.py` | `[2.3]` | Invalid polygons, self-intersection, area computation, ownership. |
| `backend/tests/test_history.py` | `[3.5]` | Server-side filters (crop/status/date), cursor pagination, ownership isolation. |
| `backend/tests/test_feedback.py` | `[3.6]` | Feedback update, approved correction merged to prediction, ownership. |
| `backend/tests/test_expert_review.py` | `[4.1]` | Severity regex parsing, concurrent review lock, state machine. |
| `backend/tests/test_alerts.py` | `[4.2]` | Pagination, unique constraint duplicate guard, expiry job. |
| `backend/tests/test_admin_metrics.py` | `[4.3]`, `[4.7]` | DB P95 percentile, date filters, dry-run purge/blobs. |
| `backend/tests/test_model_registry.py` | `[4.5]` | Promotion gates, rollback endpoint, concurrent promotions. |
| `backend/tests/test_mlops.py` | `[4.6]` | Status enum validation, missing file warnings, export size limits. |
| `backend/tests/test_translation.py` | `[5.4]` | Batch translation, Google + HF dual failure degraded mode. |
| `mobile/test/prediction_parsing_test.dart` | `[3.4]`, `[6.8]` | `Prediction.fromJson()` with completed, partial, failed, and translated JSON. |
| `mobile/test/sync_service_test.dart` | `[6.5]` | SQLite queue insert, drain on connectivity, bounded backoff retry. |
| `mobile/test/tts_service_test.dart` | `[6.4]` | Cache eviction at 50MB, markdown stripping, language routing. |

---

## Verification Plan

### Automated Execution Commands
```bash
# 1. Backend Linting & Full Test Suite (including all ~20 test files)
cd z:\Projects\Smart-Farming\backend
pytest tests/ -v --cov=app

# 2. Frontend TypeScript Build & Type Checks
cd z:\Projects\Smart-Farming\frontend
npm run build

# 3. Mobile Static Analysis & Unit Tests
cd z:\Projects\Smart-Farming\mobile
flutter analyze
flutter test
```

### S3 Migration Verification Flow
1. Run `python backend/scripts/migrate_to_s3.py --dry-run` and inspect `s3_migration_report.json`.
2. Run live migration: `python backend/scripts/migrate_to_s3.py --verify-checksum`.
3. Verify bucket contents: `aws s3 ls s3://smart-farming-data-575509634394-us-east-1-an/ --recursive`.

### End-to-End Manual Verification Flows
1. **Admin Role Assignment & Demotion Guards**:
   - Log in as admin on web (`/admin/users`).
   - Change a farmer user's role to `expert`.
   - Log in as that user: verify access to `/expert/queue`.
   - Attempt to demote own admin account: verify UI and API block with error.
2. **Media Gateway Authorization Flow**:
   - Upload leaf as Farmer A.
   - Obtain media URL for raw and processed image.
   - Attempt to access as Farmer B: verify `403 Forbidden`.
   - Request expert review on scan.
   - Access as Expert: verify access granted.
   - Access as Admin: verify access granted.
3. **Mobile Offline SQLite Queue Flow**:
   - Turn off device network (Airplane mode).
   - Capture leaf scan: verify saved to local SQLite database with plot ID.
   - Reconnect network: verify `SyncService.drain()` automatically uploads to backend and updates prediction.
