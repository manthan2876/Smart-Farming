# Production Readiness Audit

**Reviewed:** 22 October 2026
**Scope:** Backend and AI service, React web app, Flutter mobile app, translation/localization, security, deployment, CI, and repository documentation.

## Executive Summary

The Phase 1 API compatibility and quality-gate acceptance criteria are implemented: web REST modules use generated OpenAPI contracts, the mobile-consumed API operations are represented in the generated Dart SDK, and CI regenerates and drift-checks both clients. The repository still does **not** meet every production standard. Important work remains in full UI localization, strict service/repository boundaries, long-running inference handling, and operational readiness.

## Findings by Area

| Area | Status | Current implementation and remaining work |
|---|---|---|
| Backend security and configuration | Improved / partial | Production hides OpenAPI/docs, requires explicit CORS origins, returns generic 500 responses with request IDs, adds security headers, and disables the unauthenticated local-media endpoint in production. Full-history Gitleaks scanning now runs in CI; provider-side secret review, rotation decisions, and a reviewed security-header policy remain. |
| Backend architecture | Partial | The app is modular and uses FastAPI dependencies, services, ORM models, and CRUD repositories in some areas. Alert listing and updates now follow router → service → CRUD boundaries, with explicit database error responses. Separation remains inconsistent; other route modules still own substantial orchestration and database work. |
| Concurrency and background work | Partial | Sync-only SQLAlchemy handlers were converted to standard `def` handlers. The application still uses synchronous SQLAlchemy, and remaining async handlers need a blocking-I/O audit. Production's default prediction flow performs long-running orchestration in the request; configure and operate the existing ARQ path or another worker for production workloads. |
| Database and lifecycle | Partial | Migrations and health/readiness checks are present, and database sessions use pooling. Production pool sizing, database backup/restore drills, and full startup/shutdown management for external services need deployment-level verification. |
| Web frontend | Improved / partial | Routes are lazy-loaded, an error boundary is present, TanStack Query is used, and frontend versions are pinned. The admin charts and icon bundles remain large; add frontend component/E2E tests and broader accessibility checks. |
| Flutter mobile | Improved / partial | Access and refresh tokens use secure storage, release signing no longer defaults to the debug key, and analysis/unit/widget tests pass. Feature/domain/data boundaries, dependency injection, signed release automation, obfuscation, and integration tests are not complete. |
| Translation and localization | Incomplete | EN/GU/HI catalog key parity is checked by TypeScript and mobile tests, and domain terms have translation helpers. Web login, shared language/theme controls and accessibility labels, account settings validation/feedback, mobile authentication/password-recovery, history filtering, and weather status/speech labels now use locale catalogs. Many other static web and mobile strings remain inline; catalog parity is not full localization coverage. |
| API contract | Phase 1 acceptance implemented; N-1 policy pending | `/api/v1` is canonical and unversioned aliases remain available. CI regenerates and drift-checks the OpenAPI snapshot, TypeScript bindings, and Dart SDK for the mobile-consumed operations. Web REST API modules use the typed contract client; mobile keeps its existing HTTP retry, refresh, and multipart flows on compatibility aliases. The specification documents versioning/deprecation expectations; a formal N-1 app/API support window remains an owner/product decision. |
| Deployment and CI | Improved / partial | Backend and frontend have non-root container images; Compose builds both. Render uses a production Gunicorn/Uvicorn worker and readiness check. CI runs backend tests, Ruff lint, focused MyPy checks, locked dependency and full-history secret audits, frontend build/type-check and dependency audit, and Flutter analyze/tests; CPU-only AI confidence tests and Dependabot updates were added. Broader backend typing, AI-service coverage, and staged release approvals remain gaps. |
| Observability and operations | Incomplete | Request IDs and structured backend logs are present. Centralized error tracking, metrics/tracing, alerting, uptime monitoring, tested database backups, and incident runbooks are not verified as deployed. |
| Documentation | Improved / partial | Root and module READMEs, architecture/config/API/deployment docs, contributing guidance, changelog, and code of conduct are present and were reconciled where they contradicted source. A license requires owner/legal direction; academic SRS, design, and test-plan artifacts are not complete. |

## Secret Scan

A pattern scan checked 457 current tracked/non-ignored files and 1,987 reachable historical text blobs; nine ignored local environment/key files were checked separately. No high-confidence private key, provider token, or live credential was confirmed in tracked/reachable Git content. Matches were classified as test configuration, code references to environment variables, the public Supabase anonymous key used by the mobile client, and the well-known AWS documentation example key in historical deployment-guide revisions.

Ignored local `backend/.env` and `backend/.env.production` files do contain non-placeholder credentials, including a Supabase `service_role` key, JWT/cron secrets, and Upstash/QStash tokens. These files are ignored by Git and are absent from tracked/reachable history, but must be treated as sensitive local secrets and not copied into logs, tickets, or shared artifacts. Rotate them if this workspace or its backups have been exposed outside the trusted team. The frontend's ignored `.env` files contain a Google Maps key; restrict it by allowed referrers and API scope.

The Supabase anonymous key is intended to be public and must remain protected by correct Supabase Row Level Security policies. Full-history Gitleaks scanning now runs in CI, but it does not replace provider-side key review, rotation, or remediation of the ignored local credentials described above.

## Changes Made in This Review

- Removed automatic startup seeding of fixed-password users; explicit user seeding now requires environment-provided passwords and does not print them.
- Tightened production CORS, docs/OpenAPI exposure, error responses, request IDs, security headers, readiness checks, and local media serving.
- Preserved signed Supabase media URLs and prevented production from serving unauthenticated `/data` paths.
- Converted synchronous-only SQLAlchemy endpoints to normal `def` handlers and corrected storage-path mapping for separately configured storage roots.
- Added backend security regression tests and isolated test configuration/model-registry files from test storage.
- Added non-root multi-stage backend and frontend images, local Compose orchestration, production Render startup settings, frontend route splitting/error handling, and dependency/version hardening.
- Fixed all 42 findings from the locked backend runtime dependency audit by updating `certifi`, Pillow, PyJWT, and `urllib3`; added a hash-enforced backend dependency audit to CI and raised the backend minimum Python version to 3.11 for the patched Pillow release.
- Switched the CI migration cycle to the same locked backend environment and added image-validation tests to the CI-selected suite.
- Added backend Ruff linting and focused MyPy checks, fixed concrete undefined-name issues found in authentication, prediction rescan, MLOps typing, and AI-service warmup, and added CPU-only confidence tests.
- Added `/api/v1` aliases for all API routers while preserving unversioned compatibility routes; OpenAPI documents the versioned surface.
- Added a checked-in OpenAPI snapshot, generated TypeScript schema bindings, CI drift detection with a locked isolated generator toolchain, and a full-history Gitleaks CI scan.
- Added explicit request/response schemas for prediction, history, weather, TTS, translation, and admin operations; migrated remaining web REST consumers to generated OpenAPI contracts and expanded reproducible Dart generation across mobile-used endpoints.
- Added mobile generated-contract serialization tests for alert, crop, prediction/status, auth, weather, and TTS payloads.
- Moved web login, settings email/phone flows, shared language/theme control labels, and shared navigation accessibility labels into EN/GU/HI catalogs. Mobile authentication/password-recovery, settings, history filtering, cached-weather status, and weather speech labels also use catalogs. A mobile catalog-completeness test and a rendered Hindi history test cover these additions; remaining client surfaces still require localization.
- Extracted alert listing and read-state persistence into CRUD functions, composed by an alert service and called from thin FastAPI route handlers. Database errors are logged and returned as explicit 503 responses instead of silently returning empty data.
- Moved disease confidence evaluation into a lightweight pure module so it can be tested without importing the model runtime.
- Changed mobile token access to fail explicitly on secure-storage errors and removed debug signing as the release fallback.
- Updated stale architecture, deployment, localization, and storage documentation; added module READMEs and project contribution/lifecycle documents.

## Verification Snapshot

- Backend CI-selected run: **105 passed, 3 failed, 2 warnings** locally. Ruff and focused MyPy checks pass; the three image-preprocessing tests cannot import OpenCV because its bundled `libpng16` library is unavailable in this environment. These failures are environment-level and unrelated to API contract changes; confirm them on the clean CI runner.
- Follow-up focused API/auth/farm/admin/translation contract tests: **30 passed**. OpenAPI, TypeScript, and Dart generation completed; repeated Dart generation produced identical checked-in artifacts.
- Frontend production build and dependency audit after API-codegen/localization changes: passed; **0 vulnerabilities**.
- Locked backend runtime dependency audit: **no known vulnerabilities** after the dependency updates.
- Full backend suite: **138 passed, 1 skipped, 5 failed** in the previously observed local environment. Three image-preprocessing tests cannot load OpenCV because the installed wheel cannot find its bundled `libpng16` dependency; two model-inference tests are blocked because the available PyTorch wheel requires CUDA libraries (`libcudart.so.13` and `libcublasLt.so`) absent from this environment.
- Frontend production build/type-check after migrating web REST modules to contract-backed APIs: passed; the previously recorded `npm audit --audit-level=high` result was **0 vulnerabilities**.
- Flutter analysis: passed; Flutter tests: **18 passed**, including generated OpenAPI model serialization tests; standalone generated Dart client analysis: passed.
- Alert service and CRUD boundary tests: **3 passed**.
- Docker Compose configuration and backend/frontend image builds: passed.

## Recommended Follow-up

1. Localize all user-facing web and mobile strings, then test actual rendered language coverage rather than catalog parity alone.
2. Move remaining route orchestration/database work into service and repository layers; audit every async handler for synchronous I/O.
3. Run inference and other long tasks through a production-configured worker; add AI-service CPU test coverage and GPU-specific tests in a suitable runner.
4. Expand backend typing and AI-service coverage, and ensure the existing lint, dependency, and secret-scan jobs are required checks on protected branches.
5. Configure and verify staging, release approvals, monitoring/alerts, backups, and restore procedures.
6. Complete signed/obfuscated mobile release automation and obtain owner/legal decisions for license and privacy/terms publication.
