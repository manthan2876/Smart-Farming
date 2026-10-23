## Summary

<!-- Briefly explain the purpose and context of this change. Include relevant issue numbers if applicable. -->

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactor / Performance optimization
- [ ] CI/CD, Documentation, or Dependencies

## Verification & Testing

- [ ] Backend tests passing (`uv run pytest backend/tests`)
- [ ] Frontend typecheck & build passing (`npm run build`)
- [ ] Mobile analyzer passing (`flutter analyze`)
- [ ] OpenAPI contract check verified (`git diff --exit-code -- Docs/openapi.json`)
- [ ] No exposed secrets or sensitive keys added

## Security & Compliance Checklist

- [ ] No hardcoded tokens, API keys, or default secrets committed.
- [ ] Endpoint input data validated with Pydantic schemas.
- [ ] Production database migrations (Alembic) are reversible.
- [ ] Relevant documentation updated (SRS, Architecture, Runbooks).

