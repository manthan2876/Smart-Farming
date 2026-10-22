# Changelog

## Unreleased — 2026-10-22

### Security
- Removed automatic creation of accounts with public, hardcoded passwords.
- Replaced public production media serving with authenticated media routes and expiring signed storage URLs.
- Added production CORS configuration requirements and disabled interactive API documentation in production.
- Made mobile secure-storage failures visible instead of silently dropping token operations.
- Updated vulnerable backend runtime dependencies and added a hash-enforced `pip-audit` CI check.

### Operations
- Added a non-root, multi-stage backend image and a non-root frontend image.
- Added a local Docker Compose stack for the backend and web frontend.
- Switched the Render service command to Gunicorn with Uvicorn workers.
- Standardized backend CI and migration checks on the locked `uv` environment.
- Added route-level frontend code splitting and a localized render error boundary.
