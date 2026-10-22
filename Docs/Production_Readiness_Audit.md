# Production Readiness Audit

**Reviewed:** 22 October 2026
**Scope:** Backend and AI service, React web app, Flutter mobile app, translation/localization, security, deployment, CI, and repository documentation.

## Executive Summary

The repository has a stronger production baseline after this review, but it does **not** yet meet every listed production standard. Critical exposure paths and unsafe defaults were hardened, deployment images and runtime configuration were improved, and the current architecture documentation was reconciled with implementation. Important work remains in full UI localization, strict service/repository boundaries, long-running inference handling, API versioning, automated security scans, and operational readiness.

## Findings by Area

| Area | Status | Current implementation and remaining work |
|---|---|---|
| Backend security and configuration | Improved / partial | Production hides OpenAPI/docs, requires explicit CORS origins, returns generic 500 responses with request IDs, adds security headers, and disables the unauthenticated local-media endpoint in production. Full-history Gitleaks scanning now runs in CI; provider-side secret review, rotation decisions, and a reviewed security-header policy remain. |
| Backend architecture | Partial | The app is modular and uses FastAPI dependencies, services, ORM models, and repositories in some areas. Router/service/repository separation is not consistently enforced; some route modules still own substantial orchestration and database work. |
| Concurrency and background work | Partial | Sync-only SQLAlchemy handlers were converted to standard `def` handlers. The application still uses synchronous SQLAlchemy, and remaining async handlers need a blocking-I/O audit. Production's default prediction flow performs long-running orchestration in the request; configure and operate the existing ARQ path or another worker for production workloads. |
| Database and lifecycle | Partial | Migrations and health/readiness checks are present, and database sessions use pooling. Production pool sizing, database backup/restore drills, and full startup/shutdown management for external services need deployment-level verification. |
| Web frontend | Improved / partial | Routes are lazy-loaded, an error boundary is present, TanStack Query is used, and frontend versions are pinned. The admin charts and icon bundles remain large; add frontend component/E2E tests, accessibility checks, and backend-to-frontend contract generation. |
| Flutter mobile | Improved / partial | Access and refresh tokens use secure storage, release signing no longer defaults to the debug key, and analysis/unit/widget tests pass. Feature/domain/data boundaries, dependency injection, signed release automation, obfuscation, and integration tests are not complete. |
| Translation and localization | Incomplete | EN/GU/HI catalog key parity is checked at build time and domain terms have translation helpers. The React login and Flutter login/password-recovery flows now use locale catalogs, but many other static web and mobile UI strings remain inline; catalog parity is not full localization coverage. |
| API contract | Improved / partial | `/api/v1` is canonical and is covered by backward-compatible aliases for current unversioned routes. A versioned OpenAPI snapshot and generated TypeScript schema are checked for drift in CI using a separately locked generator toolchain. The generated types are not yet integrated into application API calls; Dart client generation/integration and an N-1 support window still need definition. |
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
- Moved the web login strings and mobile authentication/password-recovery copy into EN/GU/HI catalogs; remaining client surfaces still require localization.
- Moved disease confidence evaluation into a lightweight pure module so it can be tested without importing the model runtime.
- Changed mobile token access to fail explicitly on secure-storage errors and removed debug signing as the release fallback.
- Updated stale architecture, deployment, localization, and storage documentation; added module READMEs and project contribution/lifecycle documents.

## Verification Snapshot

- Backend CI-selected run: **101 passed, 3 failed, 2 warnings** locally. Ruff and focused MyPy checks pass; the three image-preprocessing tests cannot import OpenCV because its bundled `libpng16` library is unavailable in this environment. The prior clean-run result was 104 passed; CI should be confirmed on its clean Ubuntu runner.
- Follow-up focused API, path, and AI tests: **12 passed**; OpenAPI and TypeScript regeneration matches checked-in files, including a repeated deterministic TypeScript output hash.
- Frontend production build and dependency audit after API-codegen/localization changes: passed; **0 vulnerabilities**.
- Locked backend runtime dependency audit: **no known vulnerabilities** after the dependency updates.
- Full backend suite: **138 passed, 1 skipped, 5 failed** in the previously observed local environment. Three image-preprocessing tests cannot load OpenCV because the installed wheel cannot find its bundled `libpng16` dependency; two model-inference tests are blocked because the available PyTorch wheel requires CUDA libraries (`libcudart.so.13` and `libcublasLt.so`) absent from this environment.
- Frontend production build/type-check: passed; `npm audit --audit-level=high`: **0 vulnerabilities**.
- Flutter analysis: passed; Flutter tests: **12 passed**.
- Docker Compose configuration and backend/frontend image builds: passed.

## Recommended Follow-up

1. Localize all user-facing web and mobile strings, then test actual rendered language coverage rather than catalog parity alone.
2. Move remaining route orchestration/database work into service and repository layers; audit every async handler for synchronous I/O.
3. Run inference and other long tasks through a production-configured worker; add AI-service CPU test coverage and GPU-specific tests in a suitable runner.
4. Establish `/api/v1` and client-generation/compatibility policy without breaking existing mobile clients.
5. Expand backend typing and AI-service coverage, and ensure the existing lint, dependency, and secret-scan jobs are required checks on protected branches.
6. Configure and verify staging, release approvals, monitoring/alerts, backups, and restore procedures.
7. Complete signed/obfuscated mobile release automation and obtain owner/legal decisions for license and privacy/terms publication.
