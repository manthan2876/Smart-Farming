# Contributing

## Development setup

- Follow the setup instructions in the root and module-specific READMEs.
- Keep credentials in local environment files or approved secret managers. Never commit `.env` files, signing keys, tokens, or production data.
- Add or update tests with behavior changes, and update the relevant architecture or deployment documentation.

## Validation

Before opening a pull request, run the checks relevant to your changes:

```bash
(cd backend && uv sync --extra dev && uv run pytest tests/)
(cd frontend && npm ci && npm run build)
(cd mobile && flutter pub get && flutter analyze && flutter test)
```

Use a separate shell for each module command. Pull requests should describe user-visible changes, migration or configuration requirements, and the validation performed.

## Change conventions

- Use focused pull requests and conventional commit prefixes such as `feat:`, `fix:`, `docs:`, and `test:`.
- Do not include generated model weights, uploaded user media, or local database files.
- Do not add a license or change legal terms without project-owner approval.
