# Web frontend

The web client is a React, TypeScript, and Vite single-page application. Route pages are lazy-loaded, TanStack Query manages server state, and translation catalogs live in `src/i18n/`.

## Development and validation

```bash
npm ci
npm run dev
npm run build
```

Set `VITE_API_URL` to the backend base URL. Only public, browser-safe values may use the `VITE_` prefix; never place credentials in frontend environment variables.

## Deployment

The production web bundle can be deployed to Vercel or built as a non-root Nginx image with `Dockerfile`. The local Compose setup builds the image and serves it on port `8080`.
