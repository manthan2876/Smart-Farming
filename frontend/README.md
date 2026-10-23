# Smart Farming Web Frontend

The web dashboard is a modern single-page application built with React 19, TypeScript, Vite, and Tailwind CSS. It provides multi-role portals for Farmers, Agronomists (Experts), and System Administrators.

---

## Key Features

- **Leaf Disease Diagnostic Portal (`/scan`, `/predictions/:id`)**:
  - Drag-and-drop / camera leaf image uploads.
  - Interactive Grad-CAM visual evidence heatmap viewer with opacity sliders.
  - 4-point ICAR agronomic advisory with neural Text-to-Speech (TTS) voice narration.
  - Instant vernacular language switching (English, Hindi, Gujarati).
- **Interactive GIS Farm & Plot Management (`/farm/settings`)**:
  - Powered by open-source **Leaflet** (`react-leaflet`, `leaflet`) with dual-layer toggling: OpenStreetMap (street view) and Esri World Imagery (high-resolution satellite view).
  - Keyless operation—no Google Maps API key or billing required.
  - Interactive polygon boundary drawing, geodesic area calculation in acres, and GPS "Locate Me" positioning.
  - Interactive boundary vertex editing: draggable circular handles, click edge to insert vertex, and double-click to delete vertex.
  - In-place plot renaming and boundary updating via `PUT /farm/plots/{plot_id}`.
- **Alerts & Notifications (`/alerts`)**:
  - Consolidated notification center with real-time unread badges in the sidebar.
  - Auto-marks alerts as read upon navigation to relevant scan results.
- **Agronomist Expert Review Queue (`/admin/expert`)**:
  - Triage desk for low-confidence (<70%) or safety-flagged scans.
  - Atomic 15-minute lease locking to prevent concurrent adjudication.
  - Side-by-side diagnostic verification, label correction, and custom guidance.
- **Administrator Telemetry & MLOps (`/admin/metrics`)**:
  - Real-time model registry health and accuracy metrics across all 7 loaded vision models.
  - **Candidate Summary Tab**: vetted agricultural scans breakdown by crop and source.
  - **Dataset Export Tab**: dataset export with crop/status filters, OpenCV normalized (224x224) or raw images, PyTorch / YOLO / CSV / TFRecord formats, train/val/test split sliders, replay ratio buffer mixing, and direct Supabase signed URL or streamed ZIP download.
  - **Export History Tab**: audit log of all previous dataset exports with timestamps and download links.

---

## Tech Stack & Architecture

- **Core**: React 19, Vite 8, TypeScript 7
- **Routing & State**: React Router DOM (v7), TanStack Query (v5)
- **Mapping & GIS**: Leaflet 1.9, React-Leaflet 5 (OpenStreetMap & Esri World Imagery)
- **Styling & Motion**: Tailwind CSS 4, Motion/React
- **Charts & Data**: Recharts
- **Storage & Auth**: Supabase JS client (`@supabase/supabase-js`)
- **Telemetry**: `@vercel/analytics`

---

## Environment Variables

Configure these in `frontend/.env` (local) or Vercel project environment variables (production):

| Variable | Description | Example |
|---|---|---|
| `VITE_API_URL` | Backend REST API gateway base URL | `https://smart-farming-backend.onrender.com` |
| `VITE_SUPABASE_URL` | Supabase project URL for authentication & storage | `https://<ref>.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous public key | `your_supabase_anon_public_key` |

> [!IMPORTANT]
> Vite only exposes variables prefixed with `VITE_` to client-side code. Never place private keys or administrative secrets in frontend configuration.

---

## Development & Verification

```bash
# Install dependencies cleanly
npm ci

# Start local Vite development server
npm run dev

# Check localization consistency (EN, HI, GU parity & literals)
npm run localization:check

# Typecheck and build production bundle
npm run build
```

---

## Deployment

The production web bundle is deployed automatically to Vercel upon git push to `main`, or can be built into a production-hardened non-root Nginx container via `Dockerfile`.
