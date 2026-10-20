# Authentication & Roles / Permissions Reference

**Project:** AI-Powered Smart Farming  
**Version:** 2.1  
**Date:** 20 October 2026  
**Status:** Active / Production Reference  

---

## Table of Contents

1. [Authentication System](#1-authentication-system)
2. [Auth Endpoints](#2-auth-endpoints)
3. [Token Usage](#3-token-usage)
4. [Roles Overview](#4-roles-overview)
5. [Permission Matrix](#5-permission-matrix)
6. [Role Dependency Chain](#6-role-dependency-chain)
7. [Media Access Control](#7-media-access-control)
8. [Expert Review State Machine](#8-expert-review-state-machine)
9. [Prediction Status Lifecycle](#9-prediction-status-lifecycle)
10. [Admin Role-Change Guards](#10-admin-role-change-guards)
11. [Supabase Auth Trigger Security](#11-supabase-auth-trigger-security)

---

## 1. Authentication System

| Property | Value |
|---|---|
| **Token type** | JWT Bearer |
| **Signing algorithm** | HS256 |
| **Access token lifetime** | 30 minutes |
| **Refresh token lifetime** | 30 days |
| **Refresh token storage** | HttpOnly cookie — `refresh_token` (also available via mobile headers) |
| **Refresh token rotation** | Database-backed rotation in `refresh_tokens` table. Every refresh issues a new pair and revokes the old token |
| **Reuse detection** | If a previously used refresh token is presented, all tokens in the family are revoked immediately (session termination) |
| **Guest Mode** | 1-Tap guest login (`POST /auth/guest`) issuing ephemeral tokens with `guest_` ID prefix |
| **Password hashing** | Argon2id (Version 19, 64 MB memory cost, 3 iterations, 4 parallel threads) via `pwdlib[argon2]` |

> [!CAUTION]
> **Production guard:** The server refuses to start if `JWT_SECRET_KEY` is left at its default value. This prevents accidental deployment with an insecure secret.
>
> **Note:** `DEBUG=True` is required for local development. When `DEBUG=True` is set, the default JWT key is also permitted, so the startup guard described above is not enforced in that mode.

---

## 2. Auth Endpoints

| Method | Endpoint | Description | Notes |
|---|---|---|---|
| `POST` | `/auth/register` | Create a new account | Phone **or** email required; default role is `farmer` |
| `POST` | `/auth/login` | Obtain access + refresh tokens | Rate-limited: **5 requests / minute** |
| `POST` | `/auth/guest` | 1-Tap Guest login | Issues temporary token (role: `farmer`, `guest_` prefix, no registration required) |
| `POST` | `/auth/forgot-password` | Request password reset token | Dispatches secure, ephemeral single-use token via SMTP email |
| `POST` | `/auth/reset-password` | Set new password with email token | Validates token expiry and resets password |
| `POST` | `/auth/refresh` | Rotate token pair | Reads `refresh_token` cookie; validates DB state, issues new pair |
| `POST` | `/auth/logout` | Invalidate session | Revokes DB refresh token and clears the `refresh_token` cookie |
| `POST` | `/auth/change-password` | Change own password | Requires current password; auth required |

---

## 3. Token Usage

### Standard (all environments)

```http
Authorization: Bearer <access_token>
```

### Development fallback (`DEBUG=true` only)

```http
X-User-ID: <user_id>
```

> [!WARNING]
> The `X-User-ID` header bypass is **only** active when the `DEBUG=True` environment variable is set. It must never be reachable in production. This header is accepted as a convenience during local development and testing.

---

## 4. Roles Overview

The platform has three roles arranged in a strict hierarchy. Every registered user starts as a **farmer**; elevated roles are assigned by an admin.

```
admin
  └── expert  (all farmer permissions + expert-specific permissions)
        └── farmer  (base role — assigned at registration)
```

| Role | Description | Assigned By |
|---|---|---|
| `farmer` | Default role for all new registrations | Automatic |
| `expert` | Agronomist with access to the expert review queue | Admin |
| `admin` | Full platform control including user management and MLOps | Admin (or bootstrap) |

---

## 5. Permission Matrix

### 5.1 Farmer

> Base role. All registered users inherit these permissions.

| Category | Permission | Endpoint(s) |
|---|---|---|
| **Diagnosis** | Upload leaf photo and trigger AI diagnosis | `POST /predict` |
| **Diagnosis** | View own prediction results | `GET /predictions/{id}` |
| **History** | View own prediction history | `GET /history` |
| **Feedback** | Submit feedback on own predictions | `POST /feedback` |
| **Expert Review** | Request expert review for own prediction | `POST /predictions/{id}/request-expert` |
| **Farm** | View and manage own farm and plots | `GET/POST/PUT /farm`, `/farm/plots` |
| **Alerts** | View own alerts | `GET /alerts` |
| **Media** | Access raw image, processed overlay, and audio — **own predictions only** | `/media/*` |
| **Account** | Change own password | `POST /auth/change-password` |
| **Weather** | View weather data for own farm | `GET /weather` |
| **Crops** | View crops reference list | `GET /crops` |
| **TTS** | Request text-to-speech narration | `POST /tts/generate` |

---

### 5.2 Expert

> Inherits **all Farmer permissions**, plus the following.

| Category | Permission | Endpoint(s) |
|---|---|---|
| **Review Queue** | View expert review queue | `GET /expert/queue` |
| **Review Queue** | View full review details including images | `GET /expert/reviews/{id}` |
| **Review Queue** | Submit review decision (approve / override / request rescan) | `POST /expert/reviews/{id}` |
| **Review Queue** | Flag cases for retraining dataset (`add_to_retraining` field in payload) | `POST /expert/reviews/{id}` |
| **Feedback** | View all farmer feedback | `GET /admin/feedback` |
| **Feedback** | Mark farmer feedback as reviewed | `POST /feedback/{id}/review` |
| **Media** | Access media for any prediction **in their review queue** (status: `pending` or `verified`) | `/media/*` |

> [!NOTE]
> **Frontend vs. backend routes:** The expert pages are mounted on the frontend at `/admin/expert` (queue list) and `/admin/expert/:id` (review detail). The backend API routes they call remain `/expert/queue` and `/expert/reviews/{id}` as shown in the table above.

---

### 5.3 Admin

> Inherits **all Expert permissions**, plus the following.

| Category | Permission | Endpoint(s) |
|---|---|---|
| **Metrics** | View platform-wide metrics and drift signals | `GET /admin/metrics` |
| **Users** | List all users | `GET /admin/users` |
| **Users** | Change user roles | `PATCH /admin/users/{id}/role` |
| **Config** | Read inference thresholds from `config.yaml` | `GET /admin/config` |
| **Config** | Update inference thresholds in `config.yaml` | `PUT /admin/config` |
| **Maintenance** | Purge entire database (requires confirmation token) | `DELETE /admin/purge` |
| **Maintenance** | Purge orphaned storage blobs | `DELETE /admin/blobs` |
| **Weather** | Manually trigger proactive weather risk analysis | `POST /admin/weather-risk/trigger` |
| **MLOps** | Promote models, view training runs | `GET/POST /admin/mlops/`, `/admin/models/` |
| **Media** | Access media for **all** predictions platform-wide | `/media/*` |

> [!IMPORTANT]
> Two hard constraints apply to admin role changes — see [§ 10 Admin Role-Change Guards](#10-admin-role-change-guards).

---

## 6. Role Dependency Chain

Roles are enforced through a FastAPI dependency injection chain. Each dependency wraps the previous one, so a route that requires `require_admin_role` automatically also validates the user token and the expert-level role check.

```
get_current_user                        ← validates JWT, returns UserModel
    └── require_expert_role             ← asserts user.role in ["expert", "admin"]
            └── require_admin_role      ← asserts user.role == "admin"
```

| Dependency | Resolves to | Used on |
|---|---|---|
| `get_current_user` | Any authenticated user | All protected routes |
| `require_expert_role` | `expert` or `admin` | Expert review routes |
| `require_admin_role` | `admin` only | Admin management routes |

---

## 7. Media Access Control

Access to prediction media (raw image, processed overlay, audio) is scoped by role:

| Accessor | Own Prediction | Expert Queue Prediction | Any Prediction |
|:---:|:---:|:---:|:---:|
| **Farmer** | ✅ | ❌ | ❌ |
| **Expert** | ✅ | ✅ *(pending / verified reviews only)* | ❌ |
| **Admin** | ✅ | ✅ | ✅ |

> [!NOTE]
> An expert's access to media is tied to the review record. If a prediction is in their queue with status `pending` or `verified`, they may access its associated media. Media for predictions outside their queue is blocked.

---

## 8. Expert Review State Machine

Each expert review request follows a two-state lifecycle. Only a review in `pending` status can receive a decision.

```
                         POST /expert/reviews/{id}
                        (decision: "approve" | "override")
                        ┌─────────────────────────────────────────→ [verified]
                        │
[pending] ──────────────┤
                        │
                        └─────────────────────────────────────────→ [rescan_requested]
                        (decision: "request_rescan")
```

| Transition | Trigger | Resulting Status |
|---|---|---|
| Farmer requests review | `POST /predictions/{id}/request-expert` | `pending` |
| Expert approves or overrides | `POST /expert/reviews/{id}` → `approve` / `override` | `verified` |
| Expert requests rescan | `POST /expert/reviews/{id}` → `request_rescan` | `rescan_requested` |

> [!WARNING]
> Submitting a decision to a review that is already `verified` returns **409 Conflict**. Only `pending` reviews accept decisions.

### Flagging for Retraining

When submitting a review decision, the expert may include `"add_to_retraining": true` in the request payload to flag the case for inclusion in the next retraining dataset. This does not affect the review status transition.

---

## 9. Prediction Status Lifecycle

A prediction moves through the following statuses from upload to final resolution:

```
(farmer uploads image)
        │
        ▼
  [processing]          ← AI inference in progress
        │
        ├──────────────→ [ready]                    ← inference succeeded, no review needed
        │
        ├──────────────→ [failed]                   ← inference error
        │
        └──────────────→ [pending_expert_review]    ← low-confidence result; review requested
                                │
                                ├──────────────────→ [verified]             ← expert approved/overrode
                                │
                                └──────────────────→ [rescan_requested]     ← expert requested new image
```

| Status | Description |
|---|---|
| `processing` | Image received; AI model inference is running |
| `ready` | Inference complete; result available to farmer |
| `completed` | Inference complete; synonym for `ready`; used by synchronous execution mode |
| `failed` | Inference encountered an error |
| `pending_expert_review` | Flagged for agronomist review (low confidence or explicit request) |
| `verified` | Expert has reviewed and confirmed or corrected the result |
| `rescan_requested` | Expert determined a new/clearer image is required |

---

## 10. Admin Role-Change Guards

Two hard constraints prevent the platform from being left without an accessible admin account.

### Guard 1 — Self-Demotion Lockout

An admin **cannot change their own role** to any non-admin role via `PATCH /admin/users/{id}/role`. This prevents an admin from accidentally locking themselves out.

```
if request.user.id == target_user.id AND new_role != "admin":
    → 403 Forbidden ("Cannot demote your own account")
```

### Guard 2 — Last Admin Lockout

If the target user is the **last remaining admin** on the platform, their role cannot be changed to a non-admin role. At least one admin must always exist.

```
if target_user.role == "admin" AND admin_count == 1 AND new_role != "admin":
    → 403 Forbidden ("Cannot demote the last remaining admin")
```

| Scenario | Allowed? |
|---|---|
| Admin promotes farmer → expert | ✅ |
| Admin promotes farmer → admin | ✅ |
| Admin demotes expert → farmer | ✅ |
| Admin demotes another admin → farmer (other admins still exist) | ✅ |
| Admin demotes their own account | ❌ 403 |
| Admin demotes the only remaining admin | ❌ 403 |

---

## 11. Supabase Auth Trigger Security

The PostgreSQL database maintains an automated integration trigger that mirrors Supabase Auth (`auth.users`) registrations into the application database (`public.users`) and provisions default farm records.

### 11.1 Hardened Trigger Architecture (`handle_new_user()`)

To eliminate privilege escalation risks, the trigger enforces strict architectural safety rules:

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
  v_role text;
  v_name text;
  v_language text;
  v_farm_name text;
  v_location text;
BEGIN
  -- Strict security guard: Read role ONLY from server-controlled raw_app_meta_data.
  -- Client-controlled raw_user_meta_data can NEVER set role to expert or admin.
  v_role := coalesce(new.raw_app_meta_data->>'role', 'farmer');
  IF v_role NOT IN ('farmer', 'expert', 'admin') THEN
    v_role := 'farmer';
  END IF;

  v_name := coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1));
  v_language := coalesce(new.raw_user_meta_data->>'language', 'English');
  v_location := coalesce(new.raw_user_meta_data->>'location', 'Gujarat, India');
  v_farm_name := coalesce(new.raw_user_meta_data->>'farm_name', (v_name || '''s Farm'));

  -- Insert public.users. NEVER overwrite existing user role on conflict.
  INSERT INTO public.users (
    id, email, phone, name, language, role, created_at
  )
  VALUES (
    new.id::text, new.email, new.phone, v_name, v_language, v_role, coalesce(new.created_at, now())
  )
  ON CONFLICT (id) DO UPDATE SET
    email = excluded.email,
    phone = coalesce(excluded.phone, public.users.phone),
    name = coalesce(excluded.name, public.users.name);

  -- Provision initial Farm record for farmers
  IF v_role = 'farmer' THEN
    INSERT INTO public.farms (
      user_id, name, location, area_acres, latitude, longitude, crop_history
    )
    VALUES (
      new.id::text,
      v_farm_name,
      v_location,
      nullif(new.raw_user_meta_data->>'farm_area_acres', '')::double precision,
      nullif(new.raw_user_meta_data->>'latitude', '')::double precision,
      nullif(new.raw_user_meta_data->>'longitude', '')::double precision,
      '[]'::json
    )
    ON CONFLICT (user_id) DO NOTHING;
  END IF;

  RETURN new;
END;
$$;
```

### 11.2 Safety Invariants
1. **No Client Role Escalation:** Reads role exclusively from `raw_app_meta_data` (writable only by the service-role admin key), defaulting strictly to `'farmer'`. Client-supplied `raw_user_meta_data` is ignored for role determination.
2. **Immutable Role on Profile Updates:** In `ON CONFLICT (id) DO UPDATE`, `role` is omitted, ensuring that subsequent profile or metadata updates cannot modify a user's assigned role.
3. **Execution Context Isolation:** `SECURITY DEFINER SET search_path = ''` mitigates schema search-path injection vulnerabilities.
4. **Trigger Event Restriction:** Bound strictly to `AFTER INSERT ON auth.users` (omits `UPDATE`).
5. **Alembic Versioning:** Packaged into migration [`0003_supabase_auth_sync.py`](file:///home/manthan/Projects/Smart-Farming/backend/alembic/versions/0003_supabase_auth_sync.py) with dialect guards for automated deployment in CI/CD.

---

*AI-Powered Smart Farming — Authentication & Roles Reference*  
*Lead Developer & Model Architect: Manthan Kuvadiya*  
*Monorepo Repository: [github.com/manthan2876/Smart-Farming](https://github.com/manthan2876/Smart-Farming)*  
*Hugging Face Space: [Maharsh8805/smart-farming-ai](https://huggingface.co/spaces/Maharsh8805/smart-farming-ai)*  
*Last Updated: 20 October 2026*
