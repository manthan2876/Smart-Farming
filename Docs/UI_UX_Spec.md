# UI/UX Specification — AI-Powered Smart Farming

**Project:** AI-Powered Smart Farming  
**Version:** 1.0  
**Date:** September 2026  
**Status:** Active / Production Reference  

---

This document is the canonical design reference for the frontend implementation. It supersedes the legacy `screen_specifications.md` and documents the Tailwind CSS design system and Vercel edge deployment.

## Table of Contents

1. [Frontend Tech Stack](#1-frontend-tech-stack)
2. [Application Routes & Pages](#2-application-routes--pages)
3. [Design System — Component Reference](#3-design-system--component-reference)
4. [Layout Architecture](#4-layout-architecture)
5. [Key UX Flows](#5-key-ux-flows)
6. [i18n Strategy](#6-i18n-strategy)
7. [Design Principles](#7-design-principles)

---

## 1. Frontend Tech Stack

| Concern         | Technology                                              |
|-----------------|---------------------------------------------------------|
| Framework       | React 18 + TypeScript                                   |
| Build Tool      | Vite                                                    |
| Styling         | **Tailwind CSS** (migrated from CSS Modules)            |
| Routing         | React Router v6                                         |
| State           | React Context (`AuthContext`)                           |
| HTTP Client     | Axios — JWT bearer token injected via request interceptor |
| Internationalisation | `src/i18n/` — English / Hindi / Gujarati           |
| Real-time       | WebSocket (scan processing progress)                    |

> **Migration Note:** All new and refactored components must use Tailwind utility classes exclusively. CSS Module files (`.module.css`) should not be added during or after this migration.

---

## 2. Application Routes & Pages

### 2.1 Public Routes _(no authentication required)_

| Route       | Page Component    | Purpose                                                                 |
|-------------|-------------------|-------------------------------------------------------------------------|
| `/`         | `LandingPage`     | Product intro: hero section, how-it-works, features, trust/partnership section |
| `/login`    | `LoginPage`       | Email or phone + password login form                                    |
| `/register` | `RegisterPage`    | Multi-step registration including farm profile setup                    |
| `/about`    | `AboutPage`       | Project background and team information                                 |
| `/services` | `ServicesPage`    | Feature showcase and capability overview                                |

### 2.2 Farmer Routes _(accessible by `farmer`, `expert`, `admin` roles)_

| Route             | Page Component        | Purpose                                                                                                     |
|-------------------|-----------------------|-------------------------------------------------------------------------------------------------------------|
| `/dashboard`      | `DashboardPage`       | Personalised welcome, recent scan summary cards, quick-action shortcuts                                     |
| `/scan`           | `ScanPage`            | Upload a leaf photo; select output language; detect or manually enter location                              |
| `/processing`     | `ProcessingPage`      | Live WebSocket progress tracker showing each pipeline stage                                                 |
| `/results/:id`    | `PredictionResultPage`| Full diagnosis: crop ID, disease card, severity heatmap, pest list, weather strip, tabbed recommendations, audio TTS, feedback, expert-review request |
| `/history`        | `HistoryPage`         | Paginated scan history; filters by crop, disease, date range, plot                                          |
| `/farm`           | `FarmSettingsPage`    | Farm details, boundary map, plot management                                                                 |
| `/weather`        | `WeatherPage`         | Current conditions + proactive alerts for the farm location                                                 |
| `/crops`          | `CropsPage`           | Supported crops catalogue with disease information                                                          |
| `/alerts`         | `AlertsPage`          | Notification inbox — expert review completions, weather risk events                                         |
| `/settings`       | `SettingsPage`        | Language preference, password change, profile details                                                       |

### 2.3 Expert Routes _(accessible by `expert`, `admin` roles)_

| Route                 | Page Component      | Purpose                                                                                       |
|-----------------------|---------------------|-----------------------------------------------------------------------------------------------|
| `/expert/queue`       | `ExpertQueuePage`   | Pending-review card list showing crop, disease, confidence level, submission date             |
| `/expert/reviews/:id` | `ExpertReviewPage`  | Full diagnosis view with leaf images; approve / override / request-rescan workflow            |
| `/admin/feedback`     | `AdminFeedbackPage` | Aggregated farmer feedback with expert review controls                                        |

### 2.4 Admin Routes _(accessible by `admin` role only)_

| Route            | Page Component     | Purpose                                                                                                                      |
|------------------|--------------------|------------------------------------------------------------------------------------------------------------------------------|
| `/admin/metrics` | `AdminMetricsPage` | System dashboard: user stats, scan counts, model accuracy, drift signals, disease-distribution chart, confidence histogram   |
| `/admin/users`   | `AdminUsersPage`   | User management: searchable/filterable list, role assignment                                                                 |

---

## 3. Design System — Component Reference

All shared UI primitives live in **`src/components/ui/`**. Import from this path; do not re-implement primitives inline.

---

### 3.1 `Button.tsx`

A polymorphic action trigger. Renders `<button>` by default.

#### Props

| Prop        | Type                                           | Default     | Notes                                  |
|-------------|------------------------------------------------|-------------|----------------------------------------|
| `variant`   | `'primary' \| 'secondary' \| 'danger' \| 'ghost'` | `'primary'` | Controls fill and colour               |
| `size`      | `'sm' \| 'md' \| 'lg'`                         | `'md'`      | Controls padding and font size         |
| `isLoading` | `boolean`                                      | `false`     | Shows spinner; disables interaction    |
| `disabled`  | `boolean`                                      | `false`     |                                        |
| `onClick`   | `() => void`                                   | —           |                                        |
| `type`      | `'button' \| 'submit' \| 'reset'`              | `'button'`  |                                        |

#### Tailwind Style Reference

| Variant     | Base Classes                                                          |
|-------------|-----------------------------------------------------------------------|
| `primary`   | `bg-green-600 text-white hover:bg-green-700 focus:ring-green-500`     |
| `secondary` | `border border-green-600 text-green-700 hover:bg-green-50`            |
| `danger`    | `bg-red-600 text-white hover:bg-red-700 focus:ring-red-500`           |
| `ghost`     | `text-green-700 hover:bg-green-50 underline-offset-2`                 |

All variants share: `rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed`

---

### 3.2 `Card.tsx`

A surface container for grouped content.

#### Props

| Prop       | Type          | Notes                               |
|------------|---------------|-------------------------------------|
| `header`   | `ReactNode`   | Optional titled header slot         |
| `footer`   | `ReactNode`   | Optional action footer slot         |
| `children` | `ReactNode`   | Main body content                   |
| `className`| `string`      | Allows extending styles             |

**Base classes:** `bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden`

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

## 6. i18n Strategy

### File Structure

```
src/i18n/
├── index.ts       ← Sets up translation function (t()), exposes useTranslation hook
├── en.ts          ← English translation key map
├── hi.ts          ← Hindi translation key map
├── gu.ts          ← Gujarati translation key map
└── domain.ts      ← Domain-specific terms: crop names, disease names (all three languages)
```

### Language Selection

| Trigger               | Behaviour                                                             |
|-----------------------|-----------------------------------------------------------------------|
| Registration Step 3   | User selects preferred language; stored in user profile via API       |
| `/settings`           | Language can be changed post-registration                             |
| Unauthenticated pages | Browser `navigator.language` detected; falls back to English         |
| Per-scan override     | `/scan` page allows selecting a different language for TTS output only |

### Translation Key Convention

```ts
// Namespace-prefixed dot notation
t('scan.uploadPrompt')
t('results.severity.moderate')
t('expert.override.farmerGuidance')
t('common.button.submit')
```

### TTS Audio Localisation

- TTS narration is generated server-side in the language selected at scan time
- Audio language is independent of UI language (farmer can use Hindi UI but receive a Gujarati audio report)
- Playback component: `<audio>` element wrapped in a styled play/pause button with duration display

### Domain Terms (`domain.ts`)

Crop and disease names are stored separately in `domain.ts` to support:
- Consistent use across UI labels, TTS scripts, and expert override dropdowns
- Easier extension when adding new crops/diseases without touching general translation files

---

## 7. Design Principles

| Principle                        | Implementation                                                                                                  |
|----------------------------------|-----------------------------------------------------------------------------------------------------------------|
| **Mobile-first**                 | All layouts designed for 375 px wide first; breakpoints `md` and `lg` add complexity. Farmers primarily use smartphones in the field. |
| **High contrast for outdoors**   | Minimum WCAG AA contrast ratio. Prefer `text-gray-900` on white. Avoid light-gray-on-white combinations.        |
| **Progressive disclosure**       | Show only what the user needs at each step. Processing page is intentionally minimal. Results page uses tabs.   |
| **Confidence transparency**      | Confidence `Badge` is shown at every prediction surface — scan card, results hero, expert queue card.           |
| **Minimal cognitive load**       | One primary action per screen. Secondary actions are lower-contrast or below the fold.                          |
| **Heatmap visual semantics**     | Blue = diseased | Yellow/Green = healthy | Red = background. Consistent across all result and review pages.  |
| **Accessible by default**        | All interactive elements: keyboard-navigable, ARIA labels on icon-only buttons, `role` and `aria-live` on progress stages. |
| **Localisation-aware layout**    | Text containers must accommodate Hindi/Gujarati string lengths (typically 20–40% longer than English). Avoid fixed-width text containers. |

---

## Appendix A — Colour Palette (Tailwind Classes)

| Token            | Tailwind Class       | Hex       | Usage                                    |
|------------------|----------------------|-----------|------------------------------------------|
| Brand Primary    | `green-600`          | `#16a34a` | Primary buttons, active nav, accents     |
| Brand Light      | `green-50`           | `#f0fdf4` | Active nav background, badge backgrounds |
| Danger           | `red-600`            | `#dc2626` | Danger buttons, severe severity badge    |
| Warning          | `yellow-500`         | `#eab308` | Moderate severity, processing status     |
| Info             | `blue-500`           | `#3b82f6` | Pending badge, heatmap diseased area     |
| Surface          | `white`              | `#ffffff` | Card backgrounds                         |
| Border           | `gray-100`           | `#f3f4f6` | Card and input borders                   |
| Text Primary     | `gray-900`           | `#111827` | Body text                                |
| Text Muted       | `gray-500`           | `#6b7280` | Helper text, secondary labels            |

---

## Appendix B — Route–Role Access Matrix

| Route                | Farmer | Expert | Admin |
|----------------------|:------:|:------:|:-----:|
| `/`                  | ✓      | ✓      | ✓     |
| `/dashboard`         | ✓      | ✓      | ✓     |
| `/scan`              | ✓      | ✓      | ✓     |
| `/processing`        | ✓      | ✓      | ✓     |
| `/results/:id`       | ✓      | ✓      | ✓     |
| `/history`           | ✓      | ✓      | ✓     |
| `/farm`              | ✓      | ✓      | ✓     |
| `/weather`           | ✓      | ✓      | ✓     |
| `/crops`             | ✓      | ✓      | ✓     |
| `/alerts`            | ✓      | ✓      | ✓     |
| `/settings`          | ✓      | ✓      | ✓     |
| `/expert/queue`      | —      | ✓      | ✓     |
| `/expert/reviews/:id`| —      | ✓      | ✓     |
| `/admin/feedback`    | —      | ✓      | ✓     |
| `/admin/metrics`     | —      | —      | ✓     |
| `/admin/users`       | —      | —      | ✓     |

---

*AI-Powered Smart Farming — Documentation*  
*Last Updated: September 2026*
