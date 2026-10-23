# Changelog

## 2026-10-24

### Frontend & GIS Mapping
- Replaced Google Maps (`@vis.gl/react-google-maps`) across the frontend with open-source **Leaflet** (`react-leaflet`, `leaflet`), OpenStreetMap, and Esri World Imagery (high-resolution satellite view).
- Removed Google Maps API key requirements (`VITE_GOOGLE_MAPS_API_KEY`, `VITE_GOOGLE_MAPS_MAP_ID`) and external Google billing dependencies.
- Added interactive polygon boundary vertex editing: draggable circular handles, edge click to insert new vertices, and double-click to remove vertices.
- Added in-place plot renaming and boundary updating via `PUT /farm/plots/{plot_id}`.
- Streamlined sidebar navigation: removed redundant top header bell icon in favor of the dedicated **Alerts** tab with live unread badge counter; relocated language selector and theme toggle to the sidebar footer.

### MLOps & Retraining Architecture
- Added interactive multi-tab MLOps dashboard in `/admin/metrics`:
  - **Candidate Summary Tab**: overview of vetted agricultural scans, pending reviews, per-crop breakdown with status badges, and privacy/leakage guarantees.
  - **Dataset Export Tab**: export controls with crop/status filters, OpenCV normalized (224x224) or raw images, PyTorch / YOLO / CSV / TFRecord formats, train/val/test split sliders, and replay ratio buffer mixing.
  - **Export History Tab**: audit table displaying historical export runs with candidate count, split distributions, timestamps, format, and direct download links.
- Implemented spatial deterministic splitting using SHA-256 partition hashing on `plot_id` to eliminate plant rescan data leakage across train, val, and test splits.
- Implemented automatic EXIF GPS coordinate scrubbing for farmer privacy.
- Added support for Supabase Object Storage signed URL exports and direct streamed ZIP archives, with automatic `uploads/` path prefix normalization.
- Injected model server gateway authentication secrets dynamically via environment variables (`MODEL_GATEWAY_SECRET` / `AI_SERVICE_GATEWAY_SECRET`).

## 2026-10-22

### Security
- Removed automatic creation of accounts with public, hardcoded passwords.
- Replaced public production media serving with authenticated media routes and expiring signed storage URLs.
- Added production CORS configuration requirements and disabled interactive API documentation in production.
- Made mobile secure-storage failures visible instead of silently dropping token operations.
- Updated vulnerable backend runtime dependencies and added a hash-enforced `pip-audit` CI check.
- Added full-history Gitleaks scanning to pull request and main-branch CI.

### Operations
- Added a non-root, multi-stage backend image and a non-root frontend image.
- Added a local Docker Compose stack for the backend and web frontend.
- Switched the Render service command to Gunicorn with Uvicorn workers.
- Standardized backend CI and migration checks on the locked `uv` environment.
- Added route-level frontend code splitting and a localized render error boundary.
- Added Ruff lint and focused MyPy checks, plus CPU-only disease-confidence tests.
- Introduced canonical `/api/v1` routes while retaining unversioned compatibility aliases.
- Added a checked-in OpenAPI snapshot and generated TypeScript API schema bindings with CI drift checks and an isolated, locked generator toolchain.
- Added a TypeScript contract client that checks API paths, methods, parameters, JSON bodies, and responses against OpenAPI; migrated web REST API modules.
- Expanded the generated Dart SDK and CI drift checks to cover mobile-consumed API operations, with generated-model serialization tests.
- Added explicit OpenAPI response schemas for prediction/history, weather, translation, TTS, and admin endpoints.
- Localized English, Hindi, and Gujarati copy in web authentication, shared language/theme/navigation controls, and mobile authentication, history, and weather surfaces.
- Localized the web account settings email/phone verification flow and mobile settings labels.
- Localized additional web account settings validation and verification feedback in English, Gujarati, and Hindi.
- Added mobile catalog completeness checks and a rendered Hindi history localization test.
- Completed EN/GU/HI localization for remaining web and mobile UI surfaces, including admin/farm-boundary/scan copy, accessibility labels, and unknown-domain fallback labels.
- Added a localization CI check for untranslated UI literals, mobile key references, web catalog parity, rendered language differences, and fallback behavior.
- Added Flutter tests for localized domain fallbacks and rendered language switching.
- Extracted alert query/update persistence into CRUD functions behind a service layer; database failures now return explicit service-unavailable responses instead of success-shaped empty results.
- Extracted expert review queue/leases/decision persistence into dedicated service and CRUD layers (`services/expert.py`, `crud/expert_review.py`) with full state-machine validation and error propagation.
- Extracted farmer feedback creation, updates, and expert review into dedicated service and CRUD layers (`services/feedback.py`, `crud/feedback.py`).
- Refactored farm and plot boundaries into dedicated service and CRUD layers (`services/farm.py`, `crud/farm.py`), converting blocking synchronous SQLAlchemy endpoints in `endpoints/farm.py` to threadpool handlers with background tasks to prevent event loop starvation.
- Added unit test suites `test_expert_service.py` and `test_feedback_service.py` to CI testing.
- Implemented Phase 4 worker queue health monitoring (`/queue-health`, `/metrics`), worker settings, dead-letter failure recording, and operational guide (`Docs/Worker_Architecture_Runbook.md`).
- Implemented Phase 5 staging orchestration (`compose.staging.yaml`, `.env.staging.example`), Sentry telemetry hooks in FastAPI and React ErrorBoundary, automated database backup and restore scripts with SHA-256 integrity verification (`scripts/backup_database.sh`, `scripts/restore_database.sh`), `test_backup_restore.py`, `Docs/Backup_Restore_Runbook.md`, and `Docs/Incident_Runbook.md`.
- Implemented Phase 6 mobile release workflow (`.github/workflows/mobile-release.yml`), obfuscated release script (`mobile/scripts/build_release.sh`), field workflow integration tests (`mobile/test/field_workflow_integration_test.dart`), Terms of Service (`Docs/Terms_of_Service.md`), Privacy Policy (`Docs/Privacy_Policy.md`), and University Publication Scope charter (`Docs/Publication_Scope.md`).
- Customized repository MIT License (`LICENSE`) citing Charotar University of Science and Technology (CHARUSAT), student authors, and faculty guide.
