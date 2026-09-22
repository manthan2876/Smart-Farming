# Walkthrough: Platform Hardening, AWS S3 Migration & Admin User Management

All deliverables specified in the Master Implementation Plan, `Docs/functionality-status.md` (sections 1.1–7.3, 8, 9), Admin Role Switching, and AWS S3 Storage Migration have been implemented, integrated across the backend, web frontend, and mobile clients, and verified with automated test suites.

---

## 1. AWS S3 Storage & Privacy Gateway Migration

### What Was Done
- **Storage Layer**: Created unified storage interface with `LocalStorageBackend` and `S3StorageBackend` in [`backend/src/app/core/storage.py`](file:///z:/Projects/Smart-Farming/backend/src/app/core/storage.py) utilizing `boto3`, server-side encryption (`AES256`), and 15-minute temporary presigned URLs.
- **S3 Live Migration Script**: Developed [`backend/scripts/migrate_to_s3.py`](file:///z:/Projects/Smart-Farming/backend/scripts/migrate_to_s3.py) and migrated all historical assets to bucket `smart-farming-data-575509634394-us-east-1-an` in `us-east-1`.
  - **Scanned**: 34 files
  - **Uploaded**: 34 files
  - **Verified (ETag/MD5)**: 34 files
  - **Database Records Updated**: 20 prediction references
  - **Audit Report**: Generated at [`backend/s3_migration_report.json`](file:///z:/Projects/Smart-Farming/backend/s3_migration_report.json)
- **Strict Media Privacy Gateway**:
  - Implemented `GET /predictions/{id}/media-url/{type}` and `GET /predictions/{id}/media/{type}` in [`predict.py`](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/predict.py#L700-L808).
  - Objects in S3 remain private. Access is authorized strictly if:
    1. The caller is the owning farmer (`pred.user_id == caller_id`), OR
    2. The caller is an agronomist/expert AND the prediction is in an active review state (`pending_expert_review`, `verified`, `rescan_requested`), OR
    3. The caller is a system administrator (`role == "admin"`).
  - Any unauthorized farmer attempting to access another farmer's scan is rejected with `403 Forbidden`.

---

## 2. Admin User Management & Role Switching

### What Was Done
- **Backend Endpoints** ([`backend/src/app/api/endpoints/admin.py`](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/admin.py#L230-L335)):
  - `GET /admin/users`: Search, filter by role (`farmer`, `expert`, `admin`), and paginated user list with farm details and scan counts.
  - `PATCH /admin/users/{user_id}/role`: Changes role between `farmer`, `expert`, and `admin` with audit logging.
  - **Security Lockout Guards**:
    - **Self-Demotion Lockout**: Prevents an administrator from demoting their own account (`400 Bad Request`).
    - **Last Admin Lockout**: Prevents demoting the last active administrator on the platform (`400 Bad Request`).
- **Frontend Page** ([`frontend/src/pages/AdminUsersPage.tsx`](file:///z:/Projects/Smart-Farming/frontend/src/pages/AdminUsersPage.tsx)):
  - Registered route `/admin/users` in [`App.tsx`](file:///z:/Projects/Smart-Farming/frontend/src/App.tsx).
  - Search by name, email, or phone; filter by role; summary counters for total registered, growers, field experts, and admins.
  - Interactive role modification modal with audit reason and lockout warnings.

---

## 3. Dedicated Sidebar Navigation & Role Experiences

### What Was Done
Updated [`frontend/src/components/Sidebar.tsx`](file:///z:/Projects/Smart-Farming/frontend/src/components/Sidebar.tsx):
- **Expert / Agronomist Role**:
  - Purple branding theme & avatar.
  - **Agronomy Desk**: Dedicated Review Queue (`/admin/expert`) and Field Feedback Audits (`/admin/feedback`).
  - **Field Tools**: Diagnostic Scanner, Scan History, Weather Intelligence, and Alerts.
- **Administrator Role**:
  - Blue branding theme & avatar.
  - **Platform Control**: System Metrics & MLOps (`/admin/metrics`), User & Role Management (`/admin/users`), Review Queue, and Feedback Logs.
  - Full access to farm plots and settings.
- **Grower / Farmer Role**:
  - Clean, focused workflow with Dashboard, Diagnostic Scan, Plot Settings, Weather, and Alerts.

---

## 4. Client-Side Printable Diagnostic PDF Export

### What Was Done
- Updated [`frontend/src/pages/PredictionResultPage.tsx`](file:///z:/Projects/Smart-Farming/frontend/src/pages/PredictionResultPage.tsx):
  - Added "Print / Export PDF" button with `Printer` icon.
  - Official print-only report header: `"Smart Farming Diagnostic & Treatment Report"`, reference ID, and timestamp.
  - Added print styles in [`frontend/src/styles/tailwind.css`](file:///z:/Projects/Smart-Farming/frontend/src/styles/tailwind.css) (`@media print`) and `.no-print` classes to interactive audio controls, feedback forms, and navigation buttons so print output produces a clean, professional agricultural advisory report.

---

## 5. Core AI Pipeline & Agronomic Hardening

### Summary of Enhancements:
1. **Request & Preprocessing Validation**:
   - Magic byte & PIL image verification (`PIL.Image.open().verify()`) in `predict.py` rejects corrupt or deceptive non-image files before saving.
   - Robust OpenCV handling for dark, truncated, or unreadable images in [`preprocessing/service.py`](file:///z:/Projects/Smart-Farming/backend/src/app/services/preprocessing/service.py).
2. **Crop Identification & Routing Thresholds**:
   - [`crop_identifier/predictor.py`](file:///z:/Projects/Smart-Farming/backend/src/app/services/crop_identifier/predictor.py): Returns `unsupported_crop` status and explicit uncertainty when crop confidence is low.
   - [`decision_engine/router.py`](file:///z:/Projects/Smart-Farming/backend/src/app/services/decision_engine/router.py): Enforces routing confidence threshold; returns `Indeterminate (Low Crop Confidence)` result and skips disease classification if confidence is below threshold.
3. **Calibrated Low-Confidence & Escalation**:
   - [`disease_classifier/predictor.py`](file:///z:/Projects/Smart-Farming/backend/src/app/services/disease_classifier/predictor.py): Flags predictions with `is_uncertain: true` and `escalation_required: true` when below configured threshold.
4. **Severity & Quality Flags**:
   - [`severity/estimator.py`](file:///z:/Projects/Smart-Farming/backend/src/app/services/severity/estimator.py): Computes `quality_flag` (`reliable`, `low_leaf_area`, `extreme_damage`).
5. **Pest Detection**:
   - [`pest_detector/predictor.py`](file:///z:/Projects/Smart-Farming/backend/src/app/services/pest_detector/predictor.py): Distinguishes `no_pest_detected` vs `model_unavailable` vs `pest_detected`.
6. **RAG Knowledge Base & Model Rollback**:
   - Expanded RAG knowledge base across all 5 supported crops + safety guidelines in [`retriever.py`](file:///z:/Projects/Smart-Farming/backend/src/app/services/rag/retriever.py).
   - Added `POST /admin/models/rollback` in [`model_registry.py`](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/model_registry.py) to immediately revert model checkpoints.
7. **Farmer Feedback Auto-Merge**:
   - Approved feedback updates both `prediction.disease` and `prediction.result["disease"]["label"]` in [`feedback.py`](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/feedback.py).
8. **GeoJSON Validation & Server Area Calculation**:
   - Validates coordinates, closed rings, and detects self-intersections using `shapely` in [`farm.py`](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/farm.py).
9. **Weather Fallback & Redis Caching**:
   - Removed Warsaw default coordinates; caches weather reports in Redis with 10-minute TTL in [`weather.py`](file:///z:/Projects/Smart-Farming/backend/src/app/api/endpoints/weather.py).

---

## 6. Mobile Client Enhancements

1. **Weather Screen** ([`mobile/lib/screens/weather/weather_screen.dart`](file:///z:/Projects/Smart-Farming/mobile/lib/screens/weather/weather_screen.dart)):
   - Fixed wind speed calculation: converts `m/s` to `km/h` (`* 3.6`).
   - Added visual `"Cached observation"` indicator when served from cache.
2. **Offline Scan Sync Queue** ([`mobile/lib/services/sync_service.dart`](file:///z:/Projects/Smart-Farming/mobile/lib/services/sync_service.dart) & [`sync_queue_item.dart`](file:///z:/Projects/Smart-Farming/mobile/lib/models/sync_queue_item.dart)):
   - Preserves `plotId`, `lat`, `lon`, and `retryCount`.
   - Implements exponential backoff cooldown (`delay = min(300, (2 ^ retryCount) * 5)` seconds) before retrying failed scans.

---

## 7. Database Initialization & Schema Auto-Migration

### What Was Done
Updated [`backend/src/app/core/init_db.py`](file:///z:/Projects/Smart-Farming/backend/src/app/core/init_db.py):
- **Dynamic Schema Auto-Migration (`_ensure_column`)**:
  - Automatically inspects the active database (PostgreSQL and SQLite) and alters tables with missing columns (`ADD COLUMN IF NOT EXISTS`).
  - Added safe column migrations for:
    - `users`: `deleted_at`, `role`, `language`
    - `farms`: `boundary`, `name`, `area_acres`, `latitude`, `longitude`
    - `plots`: `geometry`, `status`, `crop`, `area_acres`
    - `predictions`: `plot_id`, `crop_conf`, `disease_conf`, `model_used`, `severity_pct`, `status`, `parent_id`, `raw_path`, `processed_path`
    - `expert_reviews`: `corrected_disease`, `corrected_severity`, `farmer_guidance`, `internal_note`
    - `feedback`: `corrected_label`, `review_status`, `review_decision`, `reviewer_id`, `reviewer_note`, `reviewed_at`
    - `dataset_candidates` & `mlops_runs`
- **503 Login Error Resolution**:
  - Resolved `503 Service Unavailable` caused by `users.deleted_at` column missing in the remote PostgreSQL instance by applying the migration and embedding safeguards.
- **Empty-Database Default Seeding**:
  - Automatically seeds default demo accounts if the database is brand new:
    - Admin: `admin@smartfarming.com` / `admin123`
    - Expert Agronomist: `expert@smartfarming.com` / `expert123`
    - Farmer: `farmer@smartfarming.com` / `farmer123` (with sample farm `Green Valley Farms`)

---

## 8. Verification Results

### Automated Test Suite (`pytest`)
All 33 backend test items executed cleanly (32 passed, 1 skipped due to external HF API credit requirement):
```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 33 items

backend\tests\test_admin_users.py .....                                  [ 15%]
backend\tests\test_api.py ......                                         [ 33%]
backend\tests\test_auth.py ...                                           [ 42%]
backend\tests\test_features_extended.py ....                             [ 54%]
backend\tests\test_hf_recommendation.py s                                [ 57%]
backend\tests\test_media_auth.py ....                                    [ 69%]
backend\tests\test_observability.py ......                               [ 87%]
backend\tests\test_pipeline.py .                                         [ 90%]
backend\tests\test_storage.py ...                                        [100%]

================= 32 passed, 1 skipped, 6 warnings in 25.10s ==================
```

### Frontend Build (`npm run build`)
TypeScript compiler and Vite production build succeeded with zero errors:
```
✓ 2882 modules transformed.
dist/index.html                     0.47 kB │ gzip:   0.31 kB
dist/assets/index-B7goa3xL.css     35.13 kB │ gzip:   7.33 kB
dist/assets/index-QP_8kKr8.js   1,102.23 kB │ gzip: 324.66 kB
✓ built in 30.52s
```

---

## 9. Mobile Past Scans History Fix & Terminal Logging

### Root Cause Analysis
1. **Schema Collision in History Endpoint (`history.py`)**:
   - In `backend/src/app/api/endpoints/history.py`, lines `res["crop"] = p.crop` and `res["disease"] = p.disease` were overwriting the nested dictionaries (`{"label": "Cotton", "confidence": 1.0}`) with flat string columns (`"Cotton"`).
   - In the Flutter mobile app, `Prediction.fromJson` executed `(json['crop'] as Map?)?.cast<String, dynamic>()`. In Dart strong mode, casting a `String` with `as Map?` threw a fatal `TypeError` on every record.
   - In `farmer_shell.dart`, `_loadHistory()` had a silent `catch (_) {}` block which swallowed the exception, leaving `_history` permanently empty and displaying "No scan history".
   - Failed scans in the database (e.g. scans #43 and #44 where crop/disease were null) further lacked fallbacks.

### Implemented Solutions
1. **Backend Normalization (`backend/src/app/api/endpoints/history.py`)**:
   - Explicitly ensures `crop`, `disease`, `severity`, `image`, and `status` are returned as compliant dictionaries matching `PredictionResponse` schema across all scans (including failed and legacy rows).
   - Preserves `label` and `confidence` fields expected by both mobile and web clients.
2. **Resilient Mobile Parsing (`mobile/lib/models/prediction.dart`)**:
   - Rewrote `Prediction.fromJson` to handle both nested `Map` and flat `String` representations for crop, disease, severity, and recommendations without throwing type errors.
3. **Structured Terminal Logging (`mobile/lib/utils/app_logger.dart`)**:
   - Built a dedicated `AppLogger` utility providing formatted, color-coded terminal output for mobile:
     - `[MOBILE HTTP]` logs request method, URL, status code, and payload sizes.
     - `[MOBILE INFO]` logs each fetched scan record (`Scan #51: Cotton | Bacterial Blight (63% severity, 95% conf)`), profile restorations, and UI renders.
     - `[MOBILE WARN]` and `[MOBILE ERROR]` log detailed error descriptions and full stack traces rather than silently swallowing exceptions.
   - Integrated into `api_service.dart`, `farmer_shell.dart`, `auth_wrapper.dart`, and `history_screen.dart`.
4. **Automated Unit Verification (`mobile/test/prediction_history_test.dart`)**:
   - Added Flutter unit tests validating standard predictions, legacy/string predictions, and failed scan records with terminal logging output. All tests pass with 0 errors.

---

## 10. Role-Based Login & Navigation Routing

### Problem Addressed
Previously, whenever any user logged in (regardless of whether their account role was `admin`, `expert`, or `farmer`), the client hardcoded a redirect to `/dashboard`. This caused confusion because:
- **Agronomists (`expert`)** have a dedicated Agronomy Desk with no `/dashboard` link in their sidebar (`Review Queue` at `/admin/expert` and `Feedback Logs` at `/admin/feedback`). Landing on `/dashboard` left them in an unfamiliar screen with no active sidebar selection.
- **Super Administrators (`admin`)** have a dedicated Platform Control desk where their primary landing page is Metrics & MLOps (`/admin/metrics`).

### Implemented Solutions
1. **Central Route Resolver (`frontend/src/lib/routes.ts`)**:
   - Implemented `getDefaultRouteForRole(role?: string): string`:
     - `admin` $\rightarrow$ `/admin/metrics` (Platform Control & Metrics)
     - `expert` $\rightarrow$ `/admin/expert` (Agronomy Desk Review Queue)
     - `farmer` (or default) $\rightarrow$ `/dashboard` (Diagnostic Dashboard)
2. **Auth Context Synchronous User Return (`frontend/src/context/AuthContext.tsx`)**:
   - Updated `signIn()` and `signUp()` signatures to return `Promise<Profile>` (resolving `res.user`) instead of `Promise<void>`.
   - Solved the React asynchronous state delay where context `user` state wasn't yet updated at the instant of navigation.
3. **Login Redirection (`frontend/src/pages/LoginPage.tsx`)**:
   - Added mount check: if an authenticated user navigates to `/auth/login`, they are immediately redirected to `getDefaultRouteForRole(user.role)`.
   - On successful login, the user is navigated directly to `getDefaultRouteForRole(loggedUser.role)` with `{ replace: true }`.
4. **Registration Redirection (`frontend/src/pages/RegisterPage.tsx`)**:
   - On successful sign up, routes new accounts to `getDefaultRouteForRole(newUser.role)`.
5. **Dashboard Route Protection (`frontend/src/pages/DashboardPage.tsx`)**:
   - Added guard redirecting `expert` accounts to `/admin/expert` if they attempt to load `/dashboard` directly.
6. **Protected Route Authorization Fallbacks (`frontend/src/components/ProtectedRoute.tsx`)**:
   - Updated authorization failure redirects to point to `getDefaultRouteForRole(user?.role)` instead of hardcoded `/dashboard`.

