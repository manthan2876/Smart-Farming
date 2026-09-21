# Smart Farming Functionality Status

**Assessment date:** 2026-09-21  
**Scope:** Backend, web frontend, mobile client, model/inference services, scheduled jobs, and MLOps features currently present in this repository.

This document describes what the project currently does, how complete each capability is, and what should be improved next. The status is based on the code that exists today, not only on the roadmap documents.

## Status Legend

| Status | Meaning |
|---|---|
| Implemented | The main path exists and is usable, although production hardening may still be needed. |
| Mostly implemented | The main path works, but an important edge case, integration, or production concern remains. |
| Partial | Some functionality exists, but the user journey or backend contract is incomplete. |
| Scaffolded | A screen, model, route, or service exists, but it is mostly a prototype or is not connected to the complete system. |
| Broken or disconnected | Code exists, but the path currently fails, is not persisted, or is not used by the active application flow. |
| Planned or missing | Described by the roadmap/specification but not implemented in the current code. |

## Executive Summary

The strongest working capability is the web-based leaf image diagnosis pipeline:

1. The user uploads a JPEG, PNG, or WebP leaf image.
2. The backend validates and preprocesses the image with OpenCV.
3. A crop model identifies the crop.
4. A decision engine selects a crop-specific disease model.
5. Disease, severity, pest, weather, and recommendation stages run.
6. The prediction is stored and displayed in the web application.

The project also contains substantial authentication, farm/plot management, history, feedback, expert, administration, TTS, scheduled-job, and MLOps code. Several of these features are only partially connected.

The most important current gaps are:

- Prediction processing uses FastAPI `BackgroundTasks`, not the Redis/ARQ queue that is already implemented.
- Expert-review requests do not reliably create queue records, and automatic low-confidence escalation is not active.
- The web admin MLOps export contract does not match the backend route.
- Feedback review is not persisted and has a missing backend import.
- Mobile is a prototype with incomplete authentication, synchronization, and backend coverage.
- Pipeline progress events do not represent every actual processing stage.
- Configuration changes are written to YAML but are not safely reloaded by already-running model services.

## 1. Core AI Diagnosis Pipeline

### 1.1 Image upload and request validation

**Status: Mostly implemented**

**Current behavior:**

- `POST /predict` accepts JPEG, PNG, and WebP images.
- A 10 MB server-side upload limit is enforced.
- The file is hashed, giving identical image content a reusable filename.
- Duplicate completed predictions can be returned from the image cache for the same plot.
- The image is saved under `backend/data/uploads`.
- The first preprocessing check runs before the request is placed in background processing.

**Main code:**

- [backend/src/app/api/endpoints/predict.py](../backend/src/app/api/endpoints/predict.py)
- [backend/src/app/services/preprocessing/service.py](../backend/src/app/services/preprocessing/service.py)
- [backend/src/app/context.py](../backend/src/app/context.py)

**What to improve:**

- Validate file contents instead of trusting only the MIME type and extension.
- Move upload size, allowed types, and storage paths into shared configuration.
- Use absolute paths derived from the backend directory consistently.
- Add idempotency handling for two identical requests arriving at the same time.
- Store upload metadata such as device, capture time, GPS, and original filename where appropriate.
- Add focused tests for invalid files, oversized files, duplicate uploads, and concurrent duplicates.

### 1.2 OpenCV preprocessing and leaf quality checks

**Status: Implemented, with validation limitations**

**Current behavior:**

- Reads the uploaded image with OpenCV.
- Calculates blur and brightness-related quality information.
- Detects a leaf and isolates the relevant region.
- Applies image enhancement and writes a processed image.
- Resizes/model-prepares the image for downstream inference.
- Rejects images that fail the quality rules before expensive model stages run.

**Main code:**

- [backend/src/app/services/preprocessing/service.py](../backend/src/app/services/preprocessing/service.py)
- [backend/src/app/services/preprocessing/leaf_isolator.py](../backend/src/app/services/preprocessing/leaf_isolator.py)

**What to improve:**

- Define and version quality thresholds rather than embedding them in service logic.
- Return a user-readable reason for every rejection: blur, darkness, no leaf, unsupported content, or unreadable file.
- Test the thresholds against a labeled set of good and bad farmer images.
- Preserve raw, processed, and any segmentation/heatmap outputs as separate artifacts.
- Add protection against malformed images that cause decoder or memory failures.

### 1.3 Crop identification

**Status: Implemented**

**Current behavior:**

- Uses the configured crop-identification model and label file.
- Produces a crop label, confidence, and probability information.
- The configured crop set includes Cotton, Groundnut, Pepper Bell, Potato, and Tomato.

**Main code:**

- [backend/src/app/services/crop_identifier/predictor.py](../backend/src/app/services/crop_identifier/predictor.py)
- [backend/config.yaml](../backend/config.yaml)
- [models/crop_identifier_v1.pth](../models/crop_identifier_v1.pth)
- [models/crop_identifier_labels.json](../models/crop_identifier_labels.json)

**What to improve:**

- Include model name and version in every prediction result.
- Make low crop confidence a visible, user-actionable result.
- Define behavior for crops outside the supported label set.
- Add tests for missing models, invalid labels, CPU-only inference, and low confidence.
- Track accuracy and confusion between supported crops using a fixed evaluation set.

### 1.4 Crop-specific disease routing

**Status: Implemented**

**Current behavior:**

- The decision engine reads the detected crop.
- It selects the disease model configured for that crop.
- It records which model was used.
- It supports the crop-specific disease model files stored under `models`.

**Main code:**

- [backend/src/app/services/decision_engine/router.py](../backend/src/app/services/decision_engine/router.py)
- [backend/src/app/config.py](../backend/src/app/config.py)
- [backend/config.yaml](../backend/config.yaml)

**What to improve:**

- Enforce the documented crop-confidence routing threshold consistently.
- Return a clear unsupported-crop result instead of silently continuing.
- Validate every configured model path at startup and expose model health.
- Add a model registry or manifest containing model version, labels, training date, and metrics.

### 1.5 Disease classification

**Status: Implemented**

**Current behavior:**

- Loads the crop-specific disease classifier.
- Returns disease label, confidence, probability data, and model metadata.
- Uses the processed leaf image from the shared context.
- Disease label files and model files exist for the supported crops.

**Main code:**

- [backend/src/app/services/disease_classifier/predictor.py](../backend/src/app/services/disease_classifier/predictor.py)
- [models](../models)

**What to improve:**

- Define a calibrated unknown/uncertain class or confidence policy.
- Keep model loading out of individual requests where possible.
- Record inference time and model version.
- Add per-crop precision, recall, F1, confusion matrix, and calibration monitoring.
- Test behavior when a crop model is missing or incompatible with its label file.

### 1.6 Severity estimation

**Status: Partial**

**Current behavior:**

- Estimates affected leaf area using OpenCV/color-based heuristics.
- Returns an affected-area percentage and a severity bucket.
- Produces an overlay-like visualization.
- It is not currently a learned segmentation model and its result is sensitive to lighting and leaf color.

**Main code:**

- [backend/src/app/services/severity/estimator.py](../backend/src/app/services/severity/estimator.py)

**What to improve:**

- Validate estimates against manually segmented ground-truth masks.
- Make thresholds crop- and disease-aware where justified.
- Return uncertainty or a quality flag when segmentation is unreliable.
- Clearly distinguish the original processed image from a true attribution/segmentation artifact.
- Add regression tests using representative healthy and diseased leaves.

### 1.7 Pest classification

**Status: Partial / optional**

**Current behavior:**

- Supports a configured YOLO classification model.
- Returns ranked pest probabilities when the model is available.
- The pipeline can continue when the pest model is absent or unavailable.
- The current implementation is classification-oriented; it does not provide a complete pest bounding-box workflow.

**Main code:**

- [backend/src/app/services/pest_detector/predictor.py](../backend/src/app/services/pest_detector/predictor.py)
- [models/pest_classifier](../models/pest_classifier)

**What to improve:**

- Distinguish `no pest detected` from `pest model unavailable`.
- Add model health checks and an explicit status in the result.
- Use object detection and bounding boxes if the product requires pest localization.
- Test missing weights, corrupt weights, and low-confidence pest results.

### 1.8 Weather data

**Status: Partial**

**Current behavior:**

- Fetches current weather using the configured external weather provider.
- Weather context is used by the recommendation pipeline and exposed by a weather endpoint.
- External failures degrade the result instead of necessarily failing the whole prediction.

**Main code:**

- [backend/src/app/services/weather/service.py](../backend/src/app/services/weather/service.py)
- [backend/src/app/api/endpoints/weather.py](../backend/src/app/api/endpoints/weather.py)
- [backend/src/app/services/weather/proactive.py](../backend/src/app/services/weather/proactive.py)

**What to improve:**

- Add timeout, retry, caching, and provider rate-limit handling.
- Clearly mark stale, unavailable, and live weather data.
- Standardize units. The backend and frontend currently do not consistently present wind speed units.
- Store the weather snapshot used for each prediction for reproducibility.
- Add tests for provider timeouts, malformed responses, and missing API keys.

### 1.9 AI recommendation generation

**Status: Partial but functional**

**Current behavior:**

- Builds a recommendation from crop, disease, severity, weather, location, and related context.
- Calls a Hugging Face/Qwen-backed service when configured.
- Parses and validates structured output.
- Falls back to generic advice when the external model is unavailable or returns invalid data.

**Main code:**

- [backend/src/app/services/recommendation/service.py](../backend/src/app/services/recommendation/service.py)
- [backend/src/app/api/endpoints/predict.py](../backend/src/app/api/endpoints/predict.py)

**What to improve:**

- Persist recommendation records separately from the prediction JSON when auditability is important.
- Include provider, model, prompt version, and fallback status in the result.
- Add deterministic local safety rules for dangerous or unsupported treatment advice.
- Validate pesticide and fertilizer advice against crop/disease restrictions.
- Add tests for malformed JSON, provider timeout, missing token, unsafe output, and fallback behavior.

### 1.10 Pipeline orchestration and persistence

**Status: Mostly implemented, with architectural inconsistency**

**Current behavior:**

- [pipeline.py](../backend/src/app/pipeline.py) coordinates preprocessing, crop, routing, disease, severity, pest, weather, and recommendation stages.
- A shared context object carries data and status through the stages.
- A placeholder prediction is stored before the long-running stages complete.
- The background pipeline updates the prediction record when processing succeeds or fails.
- Redis publishes some progress events for the web client.

**Important limitation:**

- `/predict` currently uses FastAPI `BackgroundTasks` to call `run_background_pipeline`.
- The Redis/ARQ worker function exists but the prediction endpoint does not enqueue an ARQ job.
- The ARQ `/job/{job_id}` status endpoint therefore does not correspond to the active prediction dispatch path.

**Main code:**

- [backend/src/app/pipeline.py](../backend/src/app/pipeline.py)
- [backend/src/app/api/endpoints/predict.py](../backend/src/app/api/endpoints/predict.py)
- [backend/src/app/worker.py](../backend/src/app/worker.py)
- [backend/src/app/core/arq.py](../backend/src/app/core/arq.py)

**What to improve:**

- Choose one production job architecture. ARQ is the better fit for durable queueing, retrying, job status, and controlled concurrency.
- Enqueue prediction jobs into ARQ and return a real job ID, or remove the unused ARQ prediction path.
- Persist stage transitions and failure reasons.
- Publish every real stage, not only crop identification and completion.
- Make retries idempotent so a retry cannot duplicate images, recommendations, or alerts.
- Add worker health, queue depth, job latency, retry, and failure metrics.

## 2. Authentication and Farmer Features

### 2.1 Registration, login, JWT refresh, and logout

**Status: Implemented with development shortcuts**

**Current behavior:**

- Users can register and log in.
- Passwords are hashed.
- Access and refresh tokens are supported.
- Refresh tokens are handled through an HTTP-only cookie flow.
- Logout and frontend token refresh logic exist.
- A development-oriented `X-User-ID` identity fallback is still present.

**Main code:**

- [backend/src/app/api/endpoints/auth.py](../backend/src/app/api/endpoints/auth.py)
- [backend/src/app/api/deps.py](../backend/src/app/api/deps.py)
- [frontend/src/context/AuthContext.tsx](../frontend/src/context/AuthContext.tsx)

**What to improve:**

- Disable the header identity fallback outside an explicit development mode.
- Require a production JWT secret and fail startup when it is missing.
- Use secure, correctly scoped cookies in production.
- Add refresh-token rotation and revocation if the threat model requires it.
- Add integration tests for registration, login, refresh, logout, expired tokens, and role checks.

### 2.2 Web farmer scan flow

**Status: Implemented**

**Current behavior:**

- The farmer selects or captures an image in the web application.
- The client can compress the image and submit location, language, and plot metadata.
- The client navigates through upload, processing, and result views.

**Main code:**

- [frontend/src/pages/ScanPage.tsx](../frontend/src/pages/ScanPage.tsx)
- [frontend/src/api/predictions.ts](../frontend/src/api/predictions.ts)

**What to improve:**

- Align the client compression limit with the server limit.
- Use the shared API client and environment-based backend URL everywhere.
- Replace browser `alert()` calls with structured application feedback.
- Display server-side rejection reasons and retry options clearly.
- Add an upload cancellation state and progress indicator.

### 2.3 Processing status and live updates

**Status: Partial**

**Current behavior:**

- A WebSocket endpoint subscribes to Redis prediction-status events.
- The frontend also polls prediction details while processing.
- The backend publishes at least crop-identification and completion events.
- The frontend presents a multi-stage progress experience.

**Limitation:**

The frontend stages are more detailed than the events actually emitted by the backend, so some displayed progress is optimistic rather than authoritative.

**What to improve:**

- Publish status for preprocessing, crop identification, routing, disease, severity, pest, weather, recommendation, persistence, and failure.
- Include structured progress payloads with stage, status, message, and timestamp.
- Make polling a reliable fallback when Redis/WebSocket is unavailable.
- Close subscriptions and clients on all disconnect paths.
- Show a terminal failed state instead of leaving the user in processing.

### 2.4 Prediction results and rescan

**Status: Implemented with presentation limitations**

**Current behavior:**

- Shows crop, disease, confidence, severity, pests, weather, recommendation, and source images.
- Supports farmer feedback and text-to-speech actions.
- Displays historical prediction information for rescans/follow-ups.
- Supports initiating a rescan flow.

**Main code:**

- [frontend/src/pages/PredictionResultPage.tsx](../frontend/src/pages/PredictionResultPage.tsx)
- [backend/src/app/api/endpoints/predict.py](../backend/src/app/api/endpoints/predict.py)

**What to improve:**

- Use configured API URLs instead of hard-coded localhost/127.0.0.1 paths.
- Clearly label confidence as model confidence, not certainty.
- Separate raw, processed, and explanation images.
- Display degraded model/weather/recommendation states.
- Add result export/share controls only after authorization and privacy rules are defined.

### 2.5 History and filtering

**Status: Implemented, limited**

**Current behavior:**

- The backend returns authenticated prediction history with pagination support.
- The web client displays history and provides crop/search filtering.

**Main code:**

- [backend/src/app/api/endpoints/history.py](../backend/src/app/api/endpoints/history.py)
- [frontend/src/pages/HistoryPage.tsx](../frontend/src/pages/HistoryPage.tsx)

**What to improve:**

- Add server-side date, crop, disease, status, and plot filters.
- Add visible pagination or cursor loading controls.
- Add trends over time for disease and severity.
- Add authorized deletion/export if required by the product.
- Test ownership isolation and pagination boundaries.

### 2.6 Farmer feedback

**Status: Implemented for collection; partial for review**

**Current behavior:**

- A farmer can mark a prediction correct/incorrect and leave a note.
- Feedback can feed future dataset-candidate/MLOps workflows.
- A review endpoint and admin UI exist, but review decisions are not fully persisted.

**Main code:**

- [backend/src/app/api/endpoints/feedback.py](../backend/src/app/api/endpoints/feedback.py)
- [backend/src/app/crud/feedback.py](../backend/src/app/crud/feedback.py)
- [frontend/src/pages/PredictionResultPage.tsx](../frontend/src/pages/PredictionResultPage.tsx)

**Known issue:**

The feedback review path references `Feedback` without importing it, and the current review operation is effectively an acknowledgement rather than a stored decision.

**What to improve:**

- Add reviewer, decision, timestamp, and audit fields.
- Prevent duplicate feedback or define update semantics.
- Decide whether feedback review belongs in the admin workflow or expert workflow.
- Add tests for authorization, duplicate submission, and review persistence.

### 2.7 Profile, language, and settings

**Status: Partial**

**Current behavior:**

- Profile retrieval and update exist.
- Crop history and some farmer settings are persisted.
- Web translation dictionaries exist for English, Hindi, and Gujarati.
- Some interface language and measurement settings remain local UI state.

**Main code:**

- [backend/src/app/api/endpoints/profile.py](../backend/src/app/api/endpoints/profile.py)
- [frontend/src/pages/SettingsPage.tsx](../frontend/src/pages/SettingsPage.tsx)
- [frontend/src/i18n](../frontend/src/i18n)

**What to improve:**

- Persist language and unit preferences in the user profile.
- Migrate hard-coded page text to the translation dictionaries.
- Apply selected units consistently to weather, farm area, and recommendations.
- Add profile validation and an explicit account deletion/data-export policy.

### 2.8 Farm boundaries and plot management

**Status: Implemented**

**Current behavior:**

- Farmers can save farm details, location, area, and boundary geometry.
- Farmers can create, update, and delete plots.
- Plot geometry is checked to ensure it lies inside the farm boundary.
- Plots can be associated with crop metadata and prediction requests.

**Main code:**

- [backend/src/app/api/endpoints/farm.py](../backend/src/app/api/endpoints/farm.py)
- [backend/src/app/models/farm.py](../backend/src/app/models/farm.py)
- [backend/src/app/models/plot.py](../backend/src/app/models/plot.py)
- [frontend/src/pages/FarmSettingsPage.tsx](../frontend/src/pages/FarmSettingsPage.tsx)

**What to improve:**

- Validate closed rings, self-intersections, coordinate order, and valid geographic ranges.
- Calculate area from geometry or clearly document that user-entered area is authoritative.
- Add plot listing/detail routes if clients need independent plot pages.
- Add tests for boundary edges, invalid polygons, ownership, and deleted farms.

### 2.9 Alerts

**Status: Partial**

**Current behavior:**

- Alerts are stored and can be listed and marked read.
- Weather-risk rules run on a schedule.
- The web shell exposes alert access/unread state.

**Main code:**

- [backend/src/app/api/endpoints/alerts.py](../backend/src/app/api/endpoints/alerts.py)
- [backend/src/app/services/weather/proactive.py](../backend/src/app/services/weather/proactive.py)
- [frontend/src/components/SideBar.tsx](../frontend/src/components/SideBar.tsx)

**What to improve:**

- Add a dedicated alerts page and detail/history view.
- Add reliable unread-count invalidation and pagination.
- Generate prediction/severity alerts where the product requires them.
- Make scheduled job health and last-run time visible to administrators.
- Prevent duplicate alerts when the same weather condition is evaluated repeatedly.

### 2.10 Text-to-speech recommendations

**Status: Partial**

**Current behavior:**

- The web result screen can request spoken recommendation text.
- Google Text-to-Speech audio is cached under `backend/data/audio`.
- The admin and scheduled orphan cleanup now include the audio directory.
- The current voice configuration is English-only and requires `GOOGLE_TTS_API_KEY`.

**Main code:**

- [backend/src/app/api/endpoints/tts.py](../backend/src/app/api/endpoints/tts.py)
- [frontend/src/pages/PredictionResultPage.tsx](../frontend/src/pages/PredictionResultPage.tsx)
- [backend/src/app/worker.py](../backend/src/app/worker.py)

**What to improve:**

- Select voice and language from the user’s persisted preference.
- Add cache size, age, and failure management.
- Avoid generating duplicate audio for equivalent normalized text.
- Add rate limiting and provider error handling.
- Decide whether audio needs persistent ownership metadata or should remain a disposable cache.

## 3. Expert and Administration

### 3.1 Expert review queue

**Status: Partial / disconnected in important paths**

**Current behavior:**

- Experts can access a protected review queue and review prediction details.
- Review actions can include approval, override, farmer guidance, notes, and retraining flags.
- Completing a review can create a farmer alert.

**Known gaps:**

- The farmer request-expert endpoint changes prediction status but does not reliably create an `ExpertReview` record, so the prediction may not appear in the queue.
- The background pipeline currently does not automatically create a pending review when confidence is low.
- Corrected disease/severity data is not consistently merged back into the prediction result.

**Main code:**

- [backend/src/app/api/endpoints/expert.py](../backend/src/app/api/endpoints/expert.py)
- [backend/src/app/api/endpoints/predict.py](../backend/src/app/api/endpoints/predict.py)
- [frontend/src/pages/ExpertQueuePage.tsx](../frontend/src/pages/ExpertQueuePage.tsx)
- [frontend/src/pages/ExpertReviewPage.tsx](../frontend/src/pages/ExpertReviewPage.tsx)

**What to improve:**

- Create the review record transactionally when a farmer requests review.
- Implement threshold-based automatic escalation.
- Define clear state transitions: ready, pending review, verified, rejected, rescan requested.
- Persist expert corrections in both the review and public prediction result.
- Add duplicate-review protection, assignment, priority, and audit history.

### 3.2 Expert-generated farmer alerts

**Status: Implemented**

**Current behavior:**

- Completing an expert review can create a farmer-facing alert.
- Expert guidance is attached to the prediction/recommendation flow.

**Main code:**

- [backend/src/app/api/endpoints/expert.py](../backend/src/app/api/endpoints/expert.py)

**What to improve:**

- Make alert creation idempotent for repeated submissions.
- Include corrected diagnosis and severity explicitly.
- Add delivery/read status and notification preferences.

### 3.3 Admin metrics

**Status: Implemented but limited**

**Current behavior:**

- Reports total users and scans.
- Reports disease distribution.
- Reports confidence brackets.
- Calculates an accuracy-like percentage from farmer feedback.

**Main code:**

- [backend/src/app/api/endpoints/admin.py](../backend/src/app/api/endpoints/admin.py)
- [frontend/src/pages/AdminMetricsPage.tsx](../frontend/src/pages/AdminMetricsPage.tsx)

**Important interpretation:**

The current accuracy value is the ratio of feedback marked correct. It is not a validated model accuracy metric and should be labeled accordingly.

**What to improve:**

- Restrict metrics to completed predictions where appropriate.
- Add date, crop, disease, model-version, and farm filters.
- Add trends, confidence calibration, rejection rate, processing latency, and fallback rate.
- Separate farmer feedback accuracy from expert-validated accuracy.
- Add tests for empty data and database failures.

### 3.4 Admin feedback review

**Status: Partial / broken integration**

**Current behavior:**

- The web admin interface lists feedback and offers review actions.
- Backend routes exist for listing and reviewing feedback.

**Known gaps:**

- The backend review decision is not persisted as a real review state.
- The feedback endpoint has a missing `Feedback` import in the review path.

**What to improve:**

- Add review status, reviewer, reason, and timestamps.
- Store an immutable audit trail.
- Route confirmed corrections into the expert/MLOps workflow.
- Fix the import and add endpoint-level tests.

### 3.5 Database purge and blob cleanup

**Status: Implemented and destructive**

**Current behavior:**

- Admins can purge prediction-related database records.
- Admin blob cleanup removes files in `data/uploads`, `data/processed`, and `data/audio` that are not referenced by image records.
- Scheduled cleanup is defined in the ARQ worker.

**Main code:**

- [backend/src/app/api/endpoints/admin.py](../backend/src/app/api/endpoints/admin.py)
- [backend/src/app/worker.py](../backend/src/app/worker.py)

**What to improve:**

- Centralize storage roots so API and worker use the same absolute paths.
- Add dry-run and deletion preview modes.
- Record who performed destructive operations and when.
- Add a retention period before deleting unreferenced files.
- Ensure audio ownership rules are explicit if TTS audio becomes user-specific.
- Protect purge operations with confirmation and stronger authorization.

### 3.6 Admin configuration management

**Status: Mostly implemented**

**Current behavior:**

- Admins can read and update crop-routing and disease-confidence thresholds in YAML.
- The UI exposes configuration controls.

**Known limitation:**

The running pipeline loads configuration into process-level objects. Updating the YAML file does not necessarily reload the already-running configuration, so a change may not take effect until restart.

**What to improve:**

- Reload configuration safely after updates or explicitly require/reveal restart behavior.
- Validate threshold ranges and relationships.
- Version configuration changes and record the administrator.
- Separate editable operational settings from model paths and secrets.
- Add concurrency protection for simultaneous updates.

### 3.7 MLOps dataset summary and export

**Status: Partial / disconnected**

**Current behavior:**

- Dataset candidates can be created from farmer feedback and expert activity.
- Backend routes can summarize candidates and export images/metadata as a ZIP.

**Known gaps:**

- Export UI options such as filters, crop selection, split percentages, format, and raw/preprocessed selection are not fully applied by the backend.
- The admin frontend calls a route/method that does not match the backend export route: the UI expects an admin export GET path while the backend exposes a dataset export POST path.

**Main code:**

- [backend/src/app/api/endpoints/mlops.py](../backend/src/app/api/endpoints/mlops.py)
- [frontend/src/pages/AdminMetricsPage.tsx](../frontend/src/pages/AdminMetricsPage.tsx)
- [backend/src/app/models/dataset.py](../backend/src/app/models/dataset.py)

**What to improve:**

- Align the frontend and backend route, HTTP method, request schema, and response handling.
- Implement all export filters and split logic.
- Include labels, provenance, consent, model version, and review status in metadata.
- Prevent duplicate candidates and unsafe path traversal in export archives.
- Add export authorization, audit logging, and tests for empty and large exports.
- Add model training/retraining orchestration only after the dataset contract is stable.

## 4. Web Frontend

### 4.1 Public pages and authentication screens

**Status: Implemented**

**Current behavior:**

- Public landing, about/services, login, registration, crop listing, and protected routes exist.
- Shared UI components and route protection are present.

**Main code:**

- [frontend/src/App.tsx](../frontend/src/App.tsx)
- [frontend/src/pages/LandingPage.tsx](../frontend/src/pages/LandingPage.tsx)
- [frontend/src/pages/LoginPage.tsx](../frontend/src/pages/LoginPage.tsx)
- [frontend/src/pages/RegisterPage.tsx](../frontend/src/pages/RegisterPage.tsx)

**What to improve:**

- Align implemented route names with roadmap/specification route names or document the final contract.
- Replace hard-coded backend URLs with one environment-based API configuration.
- Add route-level tests for anonymous, farmer, expert, and admin users.
- Add consistent loading, empty, and server-error states.

### 4.2 Role portals and navigation

**Status: Partial**

**Current behavior:**

- Farmer, expert, and admin access checks exist.
- The main web shell and sidebar provide role-aware navigation.

**Limitation:**

The role experiences still share much of the same shell and are not fully separate portals as described by the roadmap.

**What to improve:**

- Define explicit role route maps and navigation contracts.
- Give expert and admin users dedicated shells where their workflows differ substantially.
- Hide unavailable actions at both UI and API levels.
- Add end-to-end authorization tests.

### 4.3 Internationalization

**Status: Scaffolded / partial**

**Current behavior:**

- English, Hindi, and Gujarati dictionaries exist.
- Some language metadata is sent with prediction requests.

**Limitation:**

Many pages still contain hard-coded English strings, and changing the language does not fully translate the running application.

**What to improve:**

- Move all visible UI text into translation keys.
- Add runtime locale switching and persistence.
- Translate server-provided recommendation labels and error messages where possible.
- Test long translated strings on mobile and desktop layouts.

### 4.4 Frontend data and API reliability

**Status: Partial**

**Current behavior:**

- React Query and API modules are present.
- Several page-specific calls and hard-coded URLs coexist.

**What to improve:**

- Consolidate requests through one typed API client.
- Generate or maintain shared request/response types.
- Normalize authentication, error, timeout, and retry handling.
- Remove localhost assumptions before deployment.
- Add build and browser-level smoke tests.

## 5. Mobile Application

### 5.1 Camera-first scanning

**Status: Partial / prototype**

**Current behavior:**

- Uses Flutter, image picker/camera input, image compression, HTTP prediction submission, local TTS, history, and bottom navigation.
- A separate camera screen exists, but the main app duplicates camera behavior rather than using one centralized flow.

**Main code:**

- [mobile/lib/main.dart](../mobile/lib/main.dart)
- [mobile/lib/screens/camera_screen.dart](../mobile/lib/screens/camera_screen.dart)
- [mobile/lib/providers/prediction_provider.dart](../mobile/lib/providers/prediction_provider.dart)

**What to improve:**

- Choose one camera and prediction flow.
- Add explicit loading, error, retry, and result states.
- Move API and prediction state out of the main widget.
- Add device permission handling and image lifecycle cleanup.
- Test Android and iOS camera behavior on real devices.

### 5.2 Mobile API integration

**Status: Partial**

**Current behavior:**

- Mobile supports prediction submission and history retrieval.
- It uses a fixed development/emulator backend URL.
- Token fields exist but a complete mobile login/token lifecycle is not implemented.

**What is missing:**

- Mobile authentication and registration.
- Profile and farm/plot APIs.
- Weather and alerts.
- Feedback and expert review.
- Prediction detail/rescan workflows.
- Production environment configuration.

**Main code:**

- [mobile/lib/services/api_service.dart](../mobile/lib/services/api_service.dart)
- [mobile/lib/models/prediction.dart](../mobile/lib/models/prediction.dart)

**What to improve:**

- Add environment-specific base URLs.
- Implement secure token storage, refresh, and logout.
- Match mobile models to the backend response schemas.
- Add network timeout, retry, and structured error parsing.
- Add contract tests against a local backend.

### 5.3 Offline queue and synchronization

**Status: Partial / not connected to the main flow**

**Current behavior:**

- Image paths can be stored in `SharedPreferences`.
- A synchronization service can drain queued scans when connectivity is available.
- Connectivity dependencies are included.

**Known gaps:**

- The main app does not reliably initialize or call the queue drain.
- Queued metadata is incomplete or discarded.
- Queue records and the `SyncQueueItem` model are not fully aligned.
- There is no robust retry/backoff or visible queue state.

**Main code:**

- [mobile/lib/services/sync_service.dart](../mobile/lib/services/sync_service.dart)
- [mobile/lib/providers/prediction_provider.dart](../mobile/lib/providers/prediction_provider.dart)

**What to improve:**

- Use a durable local database instead of only `SharedPreferences` for queue records.
- Preserve plot, location, language, and client request IDs.
- Add connectivity listeners and bounded retry with backoff.
- Show pending, uploading, failed, and completed states.
- Handle expired/deleted temporary image files.
- Add offline integration tests.

### 5.4 Mobile model/build health

**Status: Broken until verified**

**Current concern:**

The mobile prediction parsing code references recommendation data without declaring the required local value in the parser. This should be checked with `flutter analyze` and corrected before treating the mobile client as build-ready.

**What to improve:**

- Run `flutter analyze` and `flutter test` in the mobile directory.
- Add JSON parsing tests for completed, failed, partial, and legacy prediction responses.
- Keep generated or shared API contracts synchronized with the backend.

### 5.5 Mobile profile and weather presentation

**Status: Scaffolded / demo**

**Current behavior:**

- Profile, location, crop list, weather values, and latest prediction presentation contain hard-coded or default data in parts of the main screen.

**What to improve:**

- Load live profile, farm, weather, alert, and prediction data.
- Label cached data and show its last-updated time.
- Reuse backend units and localization settings.

## 6. Scheduled Jobs and Infrastructure

### 6.1 Redis and ARQ integration

**Status: Scaffolded / partially active**

**Current behavior:**

- The app initializes an optional ARQ Redis pool during FastAPI startup.
- A worker function named `process_prediction_job` can run the heavy prediction pipeline in an executor.
- Scheduled ARQ jobs exist for orphaned file cleanup and proactive weather risks.
- The application can continue when Redis is unavailable unless `REQUIRE_REDIS` is enabled.

**Important limitation:**

The active `/predict` endpoint uses FastAPI `BackgroundTasks`, so prediction requests are not currently queued into ARQ. Redis is active for status pub/sub and pool initialization, but not as the prediction job queue.

**Main code:**

- [backend/src/app/core/arq.py](../backend/src/app/core/arq.py)
- [backend/src/app/worker.py](../backend/src/app/worker.py)
- [backend/src/app/main.py](../backend/src/app/main.py)

**What to improve:**

- Decide whether ARQ is the official prediction execution mechanism.
- If yes, enqueue jobs from `/predict`, return an ARQ job ID, run a worker process, and make retries/idempotency explicit.
- If no, remove or narrow unused ARQ prediction code and document Redis as pub/sub plus scheduled-job infrastructure.
- Add worker startup instructions, health checks, queue metrics, and failure alerts.

### 6.2 Orphaned file cleanup

**Status: Implemented**

**Current behavior:**

- Admin cleanup and scheduled cleanup inspect uploaded, processed, and audio directories.
- Image paths referenced by database image records are preserved.
- Unreferenced files are deleted.

**What to improve:**

- Use shared absolute storage configuration.
- Add dry-run, retention, and audit modes.
- Protect against symlinks and unexpected nested files.
- Add tests using temporary directories.

### 6.3 Proactive weather risk jobs

**Status: Partial**

**Current behavior:**

- Scheduled weather evaluation runs three times per day through the worker configuration.
- It can inspect farms/plots and create weather-related alerts.

**What to improve:**

- Verify the worker process is actually deployed in every environment.
- Add deduplication and alert expiry.
- Record last successful run and provider failure details.
- Add a manual admin trigger for controlled testing.

## 7. Data, Models, and MLOps

### 7.1 Stored prediction history

**Status: Implemented**

**Current behavior:**

- Predictions, images, users, farms, plots, feedback, recommendations, alerts, expert reviews, and dataset candidates have database models.
- Prediction results preserve a structured JSON result and status.
- Historical parent relationships support rescans/follow-ups.

**What to improve:**

- Add schema versioning to stored result JSON.
- Store model/config/provider versions for reproducibility.
- Use explicit relationships and lifecycle rules for image and prediction deletion.
- Add migration tooling and backup/restore documentation.

### 7.2 Model training and evaluation assets

**Status: Offline assets present; production lifecycle partial**

**Current behavior:**

- Model weights, label files, datasets, notebooks, and evaluation artifacts exist in the repository structure.
- The runtime loads configured model files for inference.

**What is missing or limited:**

- There is no complete automated model registry, promotion process, or retraining pipeline.
- Accuracy/drift monitoring is not connected to production feedback.
- Dataset export is not yet a reliable end-to-end training handoff.

**What to improve:**

- Version datasets, labels, weights, configuration, and evaluation metrics together.
- Add reproducible training commands and environment manifests.
- Define promotion gates for model accuracy and safety.
- Add production drift and confidence monitoring.
- Keep large model artifacts outside normal source control when scaling the project.

## 8. Testing and Operational Readiness

**Status: Limited automated coverage**

**Existing coverage:**

- Authentication utility tests in [backend/tests/test_auth.py](../backend/tests/test_auth.py).
- Basic API and serialization checks in [backend/tests/test_api.py](../backend/tests/test_api.py).
- A pipeline smoke test in [backend/tests/test_pipeline.py](../backend/tests/test_pipeline.py).
- An external recommendation test in [backend/tests/test_hf_recommendation.py](../backend/tests/test_hf_recommendation.py).

**Important missing coverage:**

- Admin blob cleanup, database purge, configuration updates, and MLOps export.
- Expert review creation, authorization, state transitions, and alerts.
- History ownership and pagination.
- Farm and plot geometry edge cases.
- WebSocket events and background failures.
- TTS caching and provider failures.
- Model fallback and missing-weight behavior.
- Frontend route and API contract tests.
- Mobile analysis, parsing, offline queue, and synchronization.

**Recommended test order:**

1. Add backend endpoint tests for prediction lifecycle, expert review, admin export, and cleanup.
2. Add service-level tests for preprocessing thresholds, model fallback, weather failures, and recommendations.
3. Add a worker/ARQ integration test with a temporary Redis instance or a mocked queue.
4. Run frontend TypeScript/build checks and add browser smoke tests.
5. Run `flutter analyze` and mobile parsing/widget tests.
6. Add a small end-to-end test from upload through stored result.

## 9. Priority Improvement Plan

### Priority 1: Make the core production-consistent

- Choose ARQ or FastAPI `BackgroundTasks` as the official prediction job system.
- If ARQ is chosen, enqueue predictions, return job IDs, run the worker, and implement retries/idempotency.
- Fix expert-review creation and automatic low-confidence escalation.
- Fix the feedback review import and persistence.
- Align MLOps export frontend and backend contracts.
- Replace relative/hard-coded storage and API paths with shared configuration.

### Priority 2: Make results trustworthy and observable (Completed)

- [x] Emit and persist every pipeline stage.
- [x] Record model, configuration, weather, recommendation-provider, and result-schema versions.
- [x] Label degraded states and confidence clearly.
- [x] Add metrics for processing duration, failures, fallbacks, queue depth, and expert corrections.
- [x] Add tests around every current known gap.

### Priority 3: Complete the client experience

- Finish web internationalization and persisted preferences.
- Add dedicated alert and role-specific workflows.
- Make mobile authentication, result parsing, offline synchronization, and API coverage match the web backend.
- Remove hard-coded demo data and development URLs.

### Priority 4: Build the MLOps loop

- Stabilize feedback and expert correction provenance.
- Make dataset export filters and splits real.
- Add reproducible training/evaluation commands.
- Add model registry/versioning and promotion gates.
- Monitor production drift and retraining candidates.

## 10. Reference Documents

- [Smart Farming roadmap v2](smart_farming_roadmap_v2.md)
- [Original Smart Farming roadmap](smart_farming_roadmap.md)
- [Screen specifications](screen_specifications.md)
- [Dataset descriptions](dataset%20descriptions.txt)
- [Weather research notes](research-notes_on_how-weather-affect-on-crop.txt)
