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
- Localized English, Hindi, and Gujarati copy in the web and mobile authentication/password-recovery flows.
