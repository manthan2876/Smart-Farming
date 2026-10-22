# Changelog

## Unreleased — 2026-10-22

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
- Extracted alert query/update persistence into CRUD functions behind a service layer; database failures now return explicit service-unavailable responses instead of success-shaped empty results.
