# UI/UX Specification — AI-Powered Smart Farming

**Project:** AI-Powered Smart Farming  
**Version:** 2.3  
**Date:** 22 October 2026  
**Status:** Active / Production Reference  

---

This document is the canonical design reference for the frontend implementation. It documents the anti-vibecoded design system, Tailwind CSS architecture, trilingual localization (EN, GU, HI), Vercel Web Analytics, and Vercel edge deployment.

## Table of Contents

1. [Frontend Tech Stack](#1-frontend-tech-stack)
2. [Application Routes & Pages](#2-application-routes--pages)
3. [Design System — Anti-Vibecoded Component Reference](#3-design-system--anti-vibecoded-component-reference)
4. [Layout Architecture](#4-layout-architecture)
5. [Key UX Flows](#5-key-ux-flows)
6. [i18n & Localization Strategy](#6-i18n--localization-strategy)
7. [Design Principles](#7-design-principles)
8. [Mobile Application UI (Flutter)](#8-mobile-application-ui-flutter)
9. [Frontend Telemetry & Vercel Web Analytics](#9-frontend-telemetry--vercel-web-analytics)

---

## 1. Frontend Tech Stack

| Concern | Technology | Details |
|---|---|---|
| Framework | React 19 + TypeScript 7 | Strict typing across components and translation catalogs |
| Build Tool | Vite 8 | Fast HMR and optimized production bundle |
| Styling | Tailwind CSS 4 | Utility-first with custom farmer-green and warm-neutral theme |
| Iconography | Lucide React | Consistent, tree-shakable icon components |
| Routing | React Router v7 | Client-side routing with role-aware protected route guards |
| State | React Context (`AuthContext`, `ThemeContext`) | Authentication state, user profile, theme, and language state |
| HTTP Client | Centralized fetch client (`src/api/client.ts`) | Shared API URL, authentication, and error handling |
| Internationalization | `src/i18n/` | EN/GU/HI catalogs are checked for key parity; some UI copy remains inline and untranslated |
| Real-time | WebSocket | Live diagnostic pipeline stage progress tracker |
| Telemetry & Analytics | `@vercel/analytics` (v2.0+) | Privacy-preserving pageview, client-side route, and custom event tracking |

---

## 2. Application Routes & Pages

### 2.1 Public Routes (no authentication required)

| Route | Page Component | Purpose |
|---|---|---|
| `/` | `LandingPage` | Product overview with interactive live diagnostic pipeline demo and Grad-CAM viewer |
| `/auth/login` | `LoginPage` | Email or phone and password authentication |
| `/auth/register` | `RegisterPage` | Account registration with preferred language selection |
| `/auth/forgot-password` | `ForgotPasswordPage` | Request password reset token via email |
| `/auth/reset-password` | `ResetPasswordPage` | Set new password using email verification token |
| `/about` | `AboutPage` | Project mission, agronomic context, and engineering background |
| `/services` | `ServicesPage` | Feature showcase and capabilities |
| `/crops` | `CropsPage` | Supported crop catalogue, symptoms, and pathogen reference |
| `/terms` | `TermsPage` | Terms of Service agreement (linked in footer) |
| `/privacy` | `PrivacyPage` | Data privacy and telemetry retention policy (linked in footer) |
| `/docs` | External redirect | Redirects to backend Swagger UI at `{API_URL}/docs` |

### 2.2 Farmer Routes (accessible by `farmer`, `expert`, `admin` roles)

| Route | Page Component | Purpose |
|---|---|---|
| `/dashboard` | `DashboardPage` | Personalized greeting, weather summary, recent scans, and quick actions |
| `/scan` | `ScanPage` | Drag-and-drop leaf photo upload with language selector |
| `/predictions/:id/processing` | `ProcessingPage` | Live pipeline progress tracker with skeleton loader states |
| `/predictions/:id` | `PredictionResultPage` | Full diagnosis report: disease, severity, pests, Grad-CAM viewer, audio advisory |
| `/history` | `HistoryPage` | Diagnostic Archive: longitudinal scan history with filter and pagination |
| `/farm/settings` | `FarmSettingsPage` | Farm details, interactive Leaflet field boundary map (OSM/Satellite), draggable vertex editing, plot renaming, and plot CRUD management |
| `/weather` | `WeatherPage` | Meteorological intelligence dashboard with TTS audio advisory |
| `/alerts` | `AlertsPage` | Notification center with live unread badge and auto-read on navigation |
| `/settings` | `SettingsPage` | Language selection, appearance theme, and password change |

### 2.3 Expert Routes (accessible by `expert`, `admin` roles)

| Route | Page Component | Purpose |
|---|---|---|
| `/admin/expert` | `ExpertQueuePage` | Agronomist triage desk for low-confidence (<70%) scans |
| `/admin/expert/:id` | `ExpertReviewPage` | Side-by-side verification: original leaf vs. Grad-CAM, diagnosis override |
| `/admin/feedback` | `AdminFeedbackPage` | Agronomist Review Desk: aggregated farmer feedback and review queue |

### 2.4 Admin Routes (accessible by `admin` role only)

| Route | Page Component | Purpose |
|---|---|---|
| `/admin/metrics` | `AdminMetricsPage` | System dashboard: model registry health, drift signals, candidate summary, dataset export, and export history |
| `/admin/users` | `AdminUsersPage` | User directory, role assignment, and account management |

---

## 3. Design System — Anti-Vibecoded Component Reference

Shared UI primitives live in **`src/components/ui/`**; icons use Lucide React.

### Design Philosophy
The design avoids AI-generated styling patterns:
- **No harsh gradients or radial glow orbs:** Surfaces use deliberate flat colors or subtle single-hue tints.
- **No drop shadows:** Depth is achieved using clean borders (`border border-neutral-200 dark:border-neutral-800`) and tonal contrast.
- **No bubbly, oversized corner radii:** Controlled sharp radius system (`rounded-sm` to `rounded-md`) applied consistently.
- **No glassmorphism:** Surfaces use solid, high-contrast backgrounds (`bg-neutral-50`, `bg-neutral-900`) for legibility in outdoor agricultural conditions.
- **Iconography:** Lucide React provides consistent icon components.
- **No decorative emojis in copy or UI:** Clean, concrete agronomic terminology.
- **No em dashes in copy:** Commas, periods, or colons are used throughout.

---

### 3.1 `Button.tsx`

Polymorphic action trigger with sharp borders and distinct interaction states.

#### Props

| Prop | Type | Default | Notes |
|---|---|---|---|
| `variant` | `'primary' \| 'secondary' \| 'danger' \| 'ghost'` | `'primary'` | Visual style |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Padding and font size |
| `isLoading` | `boolean` | `false` | Shows spinner; disables interaction |
| `disabled` | `boolean` | `false` | Disables interaction |
| `onClick` | `() => void` | — | Click handler |
| `type` | `'button' \| 'submit' \| 'reset'` | `'button'` | HTML button type |

#### Style Tokens

| Variant | Base Classes |
|---|---|
| `primary` | `bg-green-700 text-white hover:bg-green-800 active:bg-green-900 focus:ring-green-600 rounded-sm` |
| `secondary` | `border border-neutral-300 dark:border-neutral-700 text-neutral-800 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-sm` |
| `danger` | `bg-red-700 text-white hover:bg-red-800 active:bg-red-900 focus:ring-red-600 rounded-sm` |
| `ghost` | `text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-sm` |

---

### 3.2 `Card.tsx`

Surface container with tonal border depth instead of drop shadows.

```tsx
<div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-sm overflow-hidden">
  {children}
</div>
```

---

### 3.3 `LanguageToggle.tsx`

Language switcher supporting dropdown, segmented, and icon variants.

#### Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `variant` | `'dropdown' \| 'segmented' \| 'icon'` | `'dropdown'` | Render style |
| `showCode` | `boolean` | `true` | Show 2-letter uppercase code (EN, GU, HI) next to Globe icon |
| `className` | `string` | `''` | Extra CSS class names |

- **Dropdown variant:** Globe icon + 2-letter uppercase code (`EN`, `GU`, `HI`). Clicking opens a clean dropdown with language options in their native script.
- **Segmented variant:** Horizontal button group showing all three languages as pill buttons.
- **Icon variant:** Globe icon only, with tooltip showing current language.
- Present in `PublicNav`, `Sidebar`, `Footer`, `LoginPage`, `RegisterPage`, `ForgotPasswordPage`, `ResetPasswordPage`.

**Usage contexts:** prediction summary cards, weather widget, expert review queue items, dashboard quick-action tiles.

---

### 3.3 `Input.tsx`

Controlled form field with accessibility baked in.

#### Props

| Prop          | Type                                                   | Notes                                 |
|---------------|--------------------------------------------------------|---------------------------------------|
| `label`       | `string`                                               | Always visible above the input        |
| `type`        | `'text' \| 'email' \| 'tel' \| 'password' \| 'number' \| 'file'` | —               |
| `error`       | `string`                                               | Triggers red border + message below   |
| `helperText`  | `string`                                               | Muted hint text when no error         |
| `...rest`     | `InputHTMLAttributes<HTMLInputElement>`                | Forwarded to `<input>`                |

**Error state classes:** `border-red-500 focus:ring-red-500` + `<p className="text-red-600 text-sm mt-1">`

---

### 3.4 `Badge.tsx`

Compact status indicator pill.

| Variant / Semantic      | Tailwind Classes                            | Used For                                      |
|-------------------------|---------------------------------------------|-----------------------------------------------|
| `green` — healthy       | `bg-green-100 text-green-800`               | Disease: none / severity: healthy             |
| `yellow` — moderate     | `bg-yellow-100 text-yellow-800`             | Severity: moderate / scan status: processing  |
| `red` — severe          | `bg-red-100 text-red-800`                   | Severity: severe / scan status: failed        |
| `blue` — pending        | `bg-blue-100 text-blue-800`                 | Expert review: pending                        |
| `gray` — unknown        | `bg-gray-100 text-gray-700`                 | Confidence: unknown / status: unknown         |

**Base classes:** `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium`

---

### 3.5 `Modal.tsx`

Accessible overlay dialog with focus trap.

#### Props

| Prop          | Type         | Notes                                  |
|---------------|--------------|----------------------------------------|
| `isOpen`      | `boolean`    | Controls visibility                    |
| `onClose`     | `() => void` | Called on backdrop click or Escape key |
| `title`       | `string`     | Dialog heading                         |
| `children`    | `ReactNode`  | Body content                           |
| `confirmLabel`| `string`     | Label for primary action button        |
| `onConfirm`   | `() => void` | Primary action handler                 |

**Backdrop:** `fixed inset-0 bg-black/50 flex items-center justify-center z-50`  
**Dialog card:** `bg-white rounded-2xl shadow-xl p-6 w-full max-w-md mx-4`

**Usage contexts:** expert override form, admin user-purge confirmation, image preview.

---

### 3.6 `Table.tsx`

Data grid with sortable columns and mobile responsiveness.

#### Props

| Prop       | Type                                            | Notes                              |
|------------|-------------------------------------------------|------------------------------------|
| `columns`  | `{ key: string; label: string; sortable?: boolean }[]` | Column definitions        |
| `data`     | `Record<string, ReactNode>[]`                   | Row data keyed by column key       |
| `onSort`   | `(key: string, direction: 'asc' \| 'desc') => void` | Sort callback                 |
| `isLoading`| `boolean`                                       | Renders skeleton rows              |

**Usage contexts:** scan history list, admin user management table, expert review queue.  
**Responsive strategy:** horizontal scroll on viewports `< md`; consider card-list fallback for `< sm`.

---

## 4. Layout Architecture

```
AppShell (authenticated)
├── SideBar           ← role-aware navigation
│   ├── Farmer links  (dashboard, scan, history, farm, weather, crops, alerts, settings)
│   ├── Expert links  (+ expert/queue, expert/reviews, admin/feedback)
│   └── Admin links   (+ admin/metrics, admin/users)
└── Main Content Area
    └── <Outlet />    ← React Router nested route renders here

PublicNav (unauthenticated)
└── Header with logo, language switcher, login/register buttons

ProtectedRoute
└── Reads AuthContext → redirects to /login if unauthenticated
```

### `AppShell.tsx`
- Persistent sidebar on `md+`; collapsible drawer on mobile (`sm`)
- Clean layout without redundant notification bells; all navigation items, alerts badge, language switch, and theme controls are neatly anchored in the sidebar
- Sidebar width: `w-64` expanded, `w-16` collapsed (icon-only mode)

### `Sidebar.tsx`
- Renders link groups based on `user.role` from `AuthContext`
- Dedicated **Alerts** navigation tab with live unread badge count (eliminating the need for a separate top navbar bell)
- Bottom controls: Language selector (English, Hindi, Gujarati) and Dark/Light theme toggle anchored above user profile
- Active link: `bg-green-50 text-green-700 font-semibold border-r-2 border-green-600`
- Inactive link: `text-gray-600 hover:bg-gray-50 hover:text-gray-900`

### `PublicNav.tsx`
- Sticky top header for public pages
- Contains: logo, nav links (About, Services), language picker, Login + Register CTAs

### `ProtectedRoute.tsx`
- Wraps all authenticated routes
- Checks `AuthContext.isAuthenticated`; redirects to `/login` with `state.from` for post-login redirect

---

## 5. Key UX Flows

### 5.1 Scan Flow

```
/scan
  │  User uploads leaf photo
  │  Selects output language (auto-detected or manual)
  │  Location auto-detected via Geolocation API or manually entered
  │
  ↓  POST /predict  →  returns { prediction_id } immediately
/processing
  │  WebSocket connection established
  │  Live stage progress (e.g., Upload → Preprocessing → Inference → Weather → Complete)
  │  Each stage: progress bar step + status badge update
  │
  ↓  WebSocket "complete" event
/results/:prediction_id
  ├── Crop identification card + confidence badge
  ├── Disease card (name, description) + confidence badge
  ├── Severity heatmap image
  │     Blue = diseased area | Yellow/Green = healthy | Red = background
  ├── Pest risk list
  ├── Weather strip (current conditions relevant to disease progression)
  ├── Recommendation tabs
  │     [Immediate Action] [Treatment] [Prevention] [Monitoring]
  ├── Audio TTS playback button (narration in user's selected language)
  ├── Feedback row: 👍 / 👎 buttons
  └── "Request Expert Review" button (shown when confidence < threshold)
```

**Edge cases:**
- Upload failure → inline error on `/scan` with retry option
- WebSocket disconnect → polling fallback with reconnect toast
- Low-confidence result → prominent advisory banner + expert-review CTA

---

### 5.2 Expert Review Flow

```
/expert/queue
  │  Card list of pending submissions
  │  Each card shows: crop, predicted disease, confidence badge, submission date, farmer name
  │
  ↓  Click card
/expert/reviews/:id
  ├── Leaf image(s) gallery
  ├── Original AI prediction (read-only): crop, disease, severity, confidence
  ├── Action toolbar
  │     [✅ Approve]  [✏️ Override / Correct]  [🔄 Request Rescan]
  │
  └── Override form (visible on "Override / Correct")
        ├── Corrected disease (dropdown — domain terms from i18n/domain.ts)
        ├── Corrected severity (dropdown: none / mild / moderate / severe)
        ├── Farmer-facing guidance (textarea — sent as notification)
        ├── Internal note (textarea — not visible to farmer)
        ├── Flag for model retraining (checkbox)
        └── [Submit] → PATCH /expert/reviews/:id → redirect to /expert/queue
```

---

### 5.3 Registration Flow (Multi-Step)

```
Step 1 — Account Details
  Name, email/phone, password, role selection (farmer / expert)

Step 2 — Farm Profile (farmer role only)
  Farm name, village/district, state, approx. land size (acres), primary crops

Step 3 — Language & Preferences
  Preferred language (en / hi / gu)
  Notification opt-in

Step 4 — Confirmation
  Summary + submit → POST /auth/register → redirect to /dashboard
```

Progress indicator: step dots at top of `Card`, back/next `Button` navigation.

---

## 6. i18n & Localization Strategy

### File Structure

```
src/i18n/
├── index.ts       ← Re-exports Language type and dictionaries
├── en.ts          ← English source of truth (670+ camelCase translation keys)
├── hi.ts          ← Hindi translation key map: Record<keyof typeof en, string>
├── gu.ts          ← Gujarati translation key map: Record<keyof typeof en, string>
└── domain.ts      ← Runtime domain translators (crops, diseases, pests, severity, weather, alerts)
```

### Compile-Time Key Parity
Type safety is strictly enforced at TypeScript compile time:
```ts
// gu.ts and hi.ts are typed against en.ts
import { en } from './en';
export const gu: Record<keyof typeof en, string> = { ... };
export const hi: Record<keyof typeof en, string> = { ... };
```
Adding a key to `en.ts` without corresponding entries in `gu.ts` and `hi.ts` triggers a `tsc` compilation error (`Property is missing in type`).

### Language Selection & Toggles

| Component / Trigger | Location | Presentation & Behavior |
|---|---|---|
| `LanguageToggle` (dropdown) | `PublicNav`, `Sidebar`, `Footer` | Globe icon + uppercase 2-letter code (`EN`, `GU`, `HI`). Dropdown displays full vernacular labels. |
| `LanguageToggle` (compact/icon) | Modals / Compact headers | Globe icon with current language tooltip. |
| Auth forms | `LoginPage`, `RegisterPage`, `ForgotPasswordPage`, `ResetPasswordPage` | Globe icon + code toggle anchored in header or top corner. |
| User Settings | `/settings` | Saved to user profile via `PUT /api/v1/profile` and cached in `localStorage`. |
| Per-scan TTS | `/scan` | Selects output audio language for Google Cloud TTS generation. |

### Translation Key Convention

Keys use camelCase naming across feature domains:
```ts
t('scanReference')         // "Scan Reference"
t('diagnosticArchive')     // "Diagnostic Archive"
t('agronomistReviewDesk')  // "Agronomist Review Desk"
t('termsTitle')            // "Terms of Service"
t('privacyTitle')          // "Privacy Policy"
```

### Runtime Domain Translators (`domain.ts`)

Dynamic API backend strings are mapped to localized terms at runtime:
- `translateCrop(crop, lang)`: Localizes crop names (`Tomato` → `ટમેટા` / `टमाटर`)
- `translateDisease(disease, lang)`: Localizes diagnosis labels (`Early Blight` → `અગાઉનો સુકારો` / `अगेती झुलसा`)
- `translatePest(pest, lang)`: Localizes detected agricultural pests
- `translateSeverityBucket(bucket, lang)`: Localizes severity tiers (Healthy, Mild, Moderate, Severe)
- `translateWeather(condition, lang)`: Localizes meteorological status terms
- `translateAlertTitle(title, lang)`: Localizes system and agronomist triage alerts

### Mobile Flutter Localization
The Flutter mobile app mirrors the web translation architecture via `mobile/lib/i18n/app_translations.dart` and `mobile/lib/i18n/domain_translations.dart`, using `context.tr('key')`.

---

## 7. Design Principles

| Principle | Implementation |
|---|---|
| **Anti-Vibecoded Visuals** | Flat colors or subtle single-hue tints only. No harsh gradients, glowing blobs, dot grids, or glassmorphism. |
| **Authentic Agronomic Palette** | Deep agricultural greens (`#15803d`), warm neutrals, and crisp contrast. No purple-and-black or neon colors. |
| **Sharp Radius System** | Deliberate, sharp corner radius system (`rounded-sm` / `rounded-xs`). No bubbly oversized curves. |
| **Iconography** | Lucide React icon components. |
| **No Emojis or Em Dashes** | Clean, professional copy without decorative emojis. Punctuated with commas, colons, or periods. |
| **Real Product Demonstration** | The landing page features a real interactive diagnostic pipeline demo with Grad-CAM visualization. |
| **Complete Transparency** | Full Terms of Service (`/terms`) and Privacy Policy (`/privacy`) pages, linked in the public footer. |
| **Loading and Error Resilience** | High-fidelity skeleton loaders for all asynchronous states, plus structured empty and error states. |
| **Outdoor Contrast & Legibility** | High contrast ratios for outdoor direct sunlight field use (minimum WCAG AA). |

---

## Appendix A — Colour Palette (Tailwind Tokens)

| Token | Tailwind Class | Hex Value | Usage |
|---|---|---|---|
| Primary | `green-700` | `#15803d` | Brand primary buttons, active tabs, core highlights |
| Primary Dark | `green-800` | `#166534` | Hover and active interaction states |
| Primary Light | `green-50` | `#f0fdf4` | Soft agricultural background tints |
| Surface Light | `white` / `neutral-50` | `#ffffff` / `#fafafa` | Card surfaces and page canvas |
| Surface Dark | `neutral-900` | `#171717` | Dark mode surface background |
| Border | `neutral-200` / `neutral-800` | `#e5e5e5` / `#262626` | Structural borders providing depth |
| Text Primary | `neutral-900` / `neutral-100` | `#171717` / `#f5f5f5` | Main body copy and headings |
| Text Muted | `neutral-600` / `neutral-400` | `#525252` / `#a3a3a3` | Secondary labels and helper text |
| Danger | `red-700` | `#b91c1c` | High severity, destructive actions, error badges |
| Warning | `amber-600` | `#d97706` | Moderate severity, pending triage notices |

---

## Appendix B — Route–Role Access Matrix

| Route | Farmer | Expert | Admin |
|---|:---:|:---:|:---:|
| `/` | Yes | Yes | Yes |
| `/about` | Yes | Yes | Yes |
| `/services` | Yes | Yes | Yes |
| `/crops` | Yes | Yes | Yes |
| `/terms` | Yes | Yes | Yes |
| `/privacy` | Yes | Yes | Yes |
| `/auth/login` | Yes | Yes | Yes |
| `/auth/register` | Yes | Yes | Yes |
| `/auth/forgot-password` | Yes | Yes | Yes |
| `/auth/reset-password` | Yes | Yes | Yes |
| `/dashboard` | Yes | Yes | Yes |
| `/scan` | Yes | Yes | Yes |
| `/predictions/:id/processing` | Yes | Yes | Yes |
| `/predictions/:id` | Yes | Yes | Yes |
| `/history` | Yes | Yes | Yes |
| `/farm/settings` | Yes | Yes | Yes |
| `/weather` | Yes | Yes | Yes |
| `/alerts` | Yes | Yes | Yes |
| `/settings` | Yes | Yes | Yes |
| `/admin/expert` | No | Yes | Yes |
| `/admin/expert/:id` | No | Yes | Yes |
| `/admin/feedback` | No | Yes | Yes |
| `/admin/metrics` | No | No | Yes |
| `/admin/users` | No | No | Yes |

---

## 8. Mobile Application UI (Flutter)

### 8.1 Overview & Persona Alignment

The farmer-facing Flutter mobile app (`mobile/`) runs on Android (API 21+) and iOS, sharing the backend REST API with the web dashboard. It is strictly dedicated to the **farmer persona**, optimized for outdoor field conditions, regional languages, low digital literacy, and variable rural network connectivity. Administrative, user management, and expert side-by-side verification dashboards remain strictly web-based to maintain focused mobile ergonomics.

### 8.2 Entry, Onboarding & Phone-First Auth

1. **`LanguageSplashScreen` (`lib/screens/splash/language_splash_screen.dart`):**
   - Displayed immediately upon first launch before any authentication prompts.
   - High-contrast visual language cards for English, ગુજરાતી (Gujarati), and हिन्दी (Hindi).
   - Generous touch targets ($\ge 64\text{px}$ card height) with native script typography.
2. **Phone-First Authentication (`lib/screens/auth/login_screen.dart`):**
   - Phone number input field prioritized over email identifiers.
   - Simplified password entry with toggleable visibility.
   - Automatic backend validation rejecting `expert` or `admin` logins with clear advisory notices directing them to the web dashboard.
3. **1-Tap Guest Mode ("Try Without Account"):**
   - Solves registration drop-off by allowing immediate field scanning without up-front sign-up.
   - Calls `POST /api/v1/auth/guest` behind the scenes to allocate an ephemeral farmer session.
   - Prompts the farmer to attach a permanent phone number or password only when attempting to save scan history permanently or configure multiple plots.

### 8.3 Navigation Shell (`FarmerShell`)

`FarmerShell` provides a 5-tab bottom navigation bar designed with high-contrast active indicators and minimum 48px touch targets:

| Tab | Icon | Screen | Primary Capabilities |
|---|---|---|---|
| **Today** | `home` | `TodayScreen` | Real-time weather card, agricultural spray window advisory, pending sync counter, quick scan trigger |
| **Farm** | `agriculture` | `FarmScreen` | Farm overview, crop plots list, area calculations, boundary drawing |
| **Scan** | `center_focus_strong` (FAB) | `CreatePredictionSheet` | Camera viewfinder with edge detection guidance, image compression, live upload |
| **Alerts** | `notifications` | `AlertsScreen` | Weather risk warnings, fungal outbreak alerts, expert diagnostic review notifications |
| **History** | `history` | `HistoryScreen` | Historical scan timeline, filter by crop/plot, rescan progression comparison |

### 8.4 Leaf Diagnostic Workflow & Result Sheet

The scan workflow transitions through three cohesive modal bottom sheets:
1. **`CreatePredictionSheet`:**
   - On-device image compression (JPEG 85% quality, max 1024px dimension) ensuring rapid upload over 2G/3G connections.
   - Quality gate checks before network transmission (blur and darkness heuristics).
2. **`ProcessingSheet`:**
   - Real-time diagnostic pipeline stages visualized with animated step indicators: Quality Assessment → Crop Identification → Disease Classification → Generating Advisory.
3. **`ResultDetailSheet`:**
   - **Qualitative Confidence Chips:** Replaces confusing raw probabilities (e.g. `91.4%`) with intuitive qualitative indicators:
     - 🟢 **High Confidence:** Established diagnosis with standard agronomic protocol.
     - 🟡 **Moderate Confidence:** Presumptive diagnosis with cautionary monitoring advice.
     - 🔴 **Needs Expert Review:** Automatic routing to human agricultural extension experts.
   - **Four-Section Agronomic Advisory:** Clearly segmented into:
     - 🚨 *Immediate Actions* (What to do today)
     - 💊 *Treatment Protocol* (Organic and chemical options)
     - 🛡️ *Preventive Measures* (Cultural practices to halt spread)
     - 👁️ *Monitoring Schedule* (Follow-up timeline)
   - **Dual Text-to-Speech (TTS) Engine:** Regional audio readback button allowing farmers to listen to the full diagnostic advisory in their native language (EN, GU, HI).

### 8.5 Offline Resilience & Queue Service

- **Local SQLite Store (`lib/services/offline_queue_db.dart`):** Scans taken in dead zones or intermittent network coverage are persisted locally with on-device compressed leaf photos, selected plot IDs, and timestamps.
- **Background Synchronization (`lib/services/offline_sync_service.dart`):** Monitors network connectivity and executes exponential backoff retries when connectivity is restored, notifying the farmer via an in-app banner upon successful upload.

### 8.6 History & Rescan Progression (`RescanComparisonSheet`)

- Accessible via `HistoryScreen` when multiple scans exist for a specific plot or crop.
- Opens `RescanComparisonSheet` providing a side-by-side visual and diagnostic comparison of two scans over time.
- Enables farmers and field officers to evaluate whether treatments (fungicides, pruning) are arresting disease progression.

### 8.7 Boundary Drawing Screen (`FieldBoundaryScreen`)

Activated when tapping "Draw Boundary" for a farm or plot in `FarmScreen`.

| UI Element | Description |
|---|---|
| **Center crosshair** | Small `+` icon (20px, white/colored, high-contrast shadow). Represents the coordinate that will be added as a vertex. Map pans behind it. |
| **Map tiles** | Satellite (default) or OSM, toggled via bottom bar icon |
| **Bottom bar - `+` button** | Adds a boundary vertex at the crosshair position (center of screen). Snaps to farm boundary edge if plot point is within ~20m outside the farm. |
| **Bottom bar - complete button** | Closes the polygon (requires ≥3 points). Disabled until 3+ vertices placed. |
| **Vertex marker** | Numbered circle on each placed point. Tap to highlight/select; long-press to delete. |
| **Move mode** | Tap a highlighted vertex then move map to reposition; crosshair turns cyan. Tap `✓` to confirm move. |
| **Rubber-band line** | White dashed line from last placed vertex to current crosshair position (preview). |
| **Magnetic snap indicator** | Amber floating badge and amber crosshair when a plot point would snap to the farm boundary. |
| **Context badge** | Floating label above crosshair showing current state: Moving Corner #N, Hovering Start Point, Snapping to Farm Boundary, etc. |
| **AppBar** | Title (Draw/Edit Farm/Plot Boundary). Delete boundary icon if editing existing boundary. Undo button. |

**Crosshair color states:**

| State | Color |
|---|---|
| Default | White |
| Hovering start point (close polygon) | Neon Green (`#00e676`) |
| Hovering an existing corner | Amber (`#ffab00`) |
| Moving a corner | Cyan (`#00b0ff`) |
| Magnetic snapping to farm edge | Orange-Amber (`#f57f17`) |

### 8.8 Design Tokens & Outdoor Accessibility (Mobile)

| Token | Value | Outdoor UX Rationale |
|---|---|---|
| `AppColors.primary` | `Color(0xff2e7d32)` | Forest green; readable under direct sunlight |
| `AppColors.primaryLight` | `Color(0xffe8f5e9)` | High-contrast tint for active chips and cards |
| `AppColors.textPrimary` | `Color(0xff1b1b1b)` | Deep near-black for maximum contrast on field devices |
| `AppColors.textMuted` | `Color(0xff616161)` | Secondary metadata labels |
| `Touch Target Minimum` | `48 × 48 dp` | Ergonomic touch sizing for gloved or outdoor hands |

---

## 9. Frontend Telemetry & Vercel Web Analytics

### 9.1 Overview & Architecture

The web dashboard integrates `@vercel/analytics` (v2.0+) to provide privacy-first, zero-cookie observability into real-world application performance, usage hotspots, and drop-off points.

```
User Action / Route Change ──► <Analytics /> or trackEvent() ──► Vercel Edge Ingestion (/_vercel/insights/*) ──► Analytics Dashboard
```

- **Client-Side SPA Route Tracking:** The `<Analytics />` component is mounted at the root of `frontend/src/App.tsx` within `<BrowserRouter>`, automatically tracking route transitions across all public and authenticated paths.
- **Zero Third-Party Cookies:** Operates entirely without cross-site tracking cookies, honoring user privacy and data protection standards.
- **Environment Isolation:** In development (`NODE_ENV === 'development'`), events are logged to the browser console and excluded from production datasets.

### 9.2 Custom Domain Event Architecture (`src/lib/analytics.ts`)

High-value diagnostic milestones are tracked through the typed helper module `frontend/src/lib/analytics.ts`:

| Event Name | Trigger Location | Tracked Parameters | Purpose |
|---|---|---|---|
| `scan_initiated` | `ScanPage.tsx` | `has_plot`, `language`, `is_offline` | Measure scan volume, offline scan prevalence, and language distribution |
| `offline_sync_completed` | `ScanPage.tsx` | `count` | Measure effectiveness of offline queue syncing upon reconnect |
| `prediction_viewed` | `PredictionResultPage.tsx` | `crop`, `disease`, `confidence_pct` | Identify most frequently diagnosed crop diseases and low-confidence clusters |
| `feedback_submitted` | `PredictionResultPage.tsx` | `vote` (`up` \| `down`), `crop`, `disease` | Track farmer diagnostic satisfaction by disease category |
| `expert_review_requested` | `PredictionResultPage.tsx` | `crop`, `disease` | Monitor edge-case escalation rate to extension experts |
| `language_changed` | `AuthContext.tsx` | `language` | Measure UI localization adoption across EN, GU, HI |
| `auth_action` | `AuthContext.tsx` | `action` (`login` \| `register` \| `guest_login` \| `logout`) | Track onboarding conversion and session churn |

### 9.3 Privacy & Data Governance Guards

- **Strict PII Exclusion:** No passwords, email addresses, phone numbers, individual user IDs, or exact latitude/longitude coordinates are attached to analytics events.
- **Safe Fallback:** All tracking invocations are wrapped in non-blocking try-catch blocks to ensure that ad-blockers or network hiccups never interrupt application execution or diagnostic flows.

---

*AI-Powered Smart Farming — UI/UX Specification Reference*  
*Lead Developer & Model Architect: Manthan Kuvadiya*  
*Monorepo Repository: [github.com/manthan2876/Smart-Farming](https://github.com/manthan2876/Smart-Farming)*  
*Hugging Face Space: [Maharsh8805/smart-farming-ai](https://huggingface.co/spaces/Maharsh8805/smart-farming-ai)*  
*Last Updated: 22 October 2026*
