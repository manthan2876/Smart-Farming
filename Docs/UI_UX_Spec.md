# UI/UX Specification — AI-Powered Smart Farming

**Project:** AI-Powered Smart Farming  
**Version:** 2.0  
**Date:** 06 October 2026  
**Status:** Active / Production Reference  

---

This document is the canonical design reference for the frontend implementation. It documents the anti-vibecoded design system, Tailwind CSS architecture, trilingual localization (EN, GU, HI), and Vercel edge deployment.

## Table of Contents

1. [Frontend Tech Stack](#1-frontend-tech-stack)
2. [Application Routes & Pages](#2-application-routes--pages)
3. [Design System — Anti-Vibecoded Component Reference](#3-design-system--anti-vibecoded-component-reference)
4. [Layout Architecture](#4-layout-architecture)
5. [Key UX Flows](#5-key-ux-flows)
6. [i18n & Localization Strategy](#6-i18n--localization-strategy)
7. [Design Principles](#7-design-principles)
8. [Mobile Application UI (Flutter)](#8-mobile-application-ui-flutter)

---

## 1. Frontend Tech Stack

| Concern | Technology | Details |
|---|---|---|
| Framework | React 18 + TypeScript 5.6 | Strict typing across components and translation keys |
| Build Tool | Vite 6 | Fast HMR and optimized production bundle |
| Styling | Tailwind CSS | Utility-first with custom farmer-green and warm-neutral theme |
| Iconography | Custom SVG Icon Set (`src/components/icons/`) | Purpose-built SVG icons; third-party icon packages replaced |
| Routing | React Router v6 | Client-side routing with role-aware protected route guards |
| State | React Context (`AuthContext`, `ThemeContext`) | Authentication state, user profile, theme, and language state |
| HTTP Client | Axios | JWT bearer token interceptor with automatic 401 refresh |
| Internationalization | `src/i18n/` | 670+ translation keys with 100% compile-time parity across EN, GU, HI |
| Real-time | WebSocket | Live diagnostic pipeline stage progress tracker |

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
| `/farm/settings` | `FarmSettingsPage` | Farm details, field boundary map, and plot CRUD management |
| `/weather` | `WeatherPage` | Meteorological intelligence dashboard with TTS audio advisory |
| `/alerts` | `AlertsPage` | Notification center with auto-read on navigation |
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
| `/admin/metrics` | `AdminMetricsPage` | System dashboard: user metrics, scan volume, model accuracy, drift signals |
| `/admin/users` | `AdminUsersPage` | User directory, role assignment, and account management |

---

## 3. Design System — Anti-Vibecoded Component Reference

All shared UI primitives live in **`src/components/ui/`** and **`src/components/icons/`**.

### Design Philosophy
The design avoids AI-generated styling patterns:
- **No harsh gradients or radial glow orbs:** Surfaces use deliberate flat colors or subtle single-hue tints.
- **No drop shadows:** Depth is achieved using clean borders (`border border-neutral-200 dark:border-neutral-800`) and tonal contrast.
- **No bubbly, oversized corner radii:** Controlled sharp radius system (`rounded-sm` to `rounded-md`) applied consistently.
- **No glassmorphism:** Surfaces use solid, high-contrast backgrounds (`bg-neutral-50`, `bg-neutral-900`) for legibility in outdoor agricultural conditions.
- **No Lucide or generic icons:** Replaced with a unified custom SVG icon library in `src/components/icons/`.
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
- Top navigation bar: breadcrumb, notification bell (links to `/alerts`), user avatar menu
- Sidebar width: `w-64` expanded, `w-16` collapsed (icon-only mode)

### `SideBar.tsx`
- Renders link groups based on `user.role` from `AuthContext`
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
- `translateSeverityBucket(bucket, lang)`: Localizes severity tiers (Healthy, Low, Medium, High)
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
| **Custom SVG Iconography** | Fully custom SVG icons in `src/components/icons/`. Zero reliance on generic third-party icon libraries. |
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

### 8.1 Overview

The farmer-facing Flutter mobile app (`mobile/`) runs on Android (API 21+) and shares the backend REST API with the web dashboard. It is exclusively for the `farmer` role. Expert and admin roles are rejected at login with a clear error message.

### 8.2 Navigation Shell

`FarmerShell` provides a 5-tab bottom navigation bar:

| Tab | Icon | Screen |
|---|---|---|
| Today | `home` | `TodayScreen` — dashboard with current weather and recent alerts |
| Farm | `agriculture` | `FarmScreen` — farm details, plots list, boundary drawing |
| Scan | `center_focus_strong` (FAB) | `CreatePredictionSheet` → `ProcessingSheet` → `ResultDetailSheet` |
| Alerts | `notifications` | `AlertsScreen` — expert review and weather alerts with unread badge |
| History | `history` | `HistoryScreen` — past scan list |

### 8.3 Login Screen

- Header row: app logo (green `eco` icon on primary-color rounded rectangle) + language selector button (`TextButton.icon` with `Icons.language`)
- No server settings or backend URL input (removed; URL governed by Supabase Remote Config)
- Supports registration (name, location, identifier, password) and login (identifier + password)
- Forgot password flow via bottom sheet

### 8.4 Boundary Drawing Screen (`FieldBoundaryScreen`)

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

### 8.5 Settings Screen

`SettingsScreen` — language preference, password change. Accessed via Settings icon in `FarmerShell` app bar.

### 8.6 Design Tokens (Mobile)

| Token | Value | Usage |
|---|---|---|
| `AppColors.primary` | `Color(0xff2e7d32)` | Primary green — buttons, icons, accents |
| `AppColors.primaryLight` | Light green tint | Backgrounds, chips |
| `AppColors.textPrimary` | Dark text | Body text |
| `AppColors.textMuted` | Muted text | Subtitles, hints |

---

*AI-Powered Smart Farming — Documentation*  
*Last Updated: 06 October 2026*
