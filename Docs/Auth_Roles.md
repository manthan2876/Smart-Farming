# Authentication & Roles / Permissions Reference

**Project:** AI-Powered Smart Farming  
**Version:** 1.0  
**Date:** September 2026  
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

---

## 1. Authentication System

| Property | Value |
|---|---|
| **Token type** | JWT Bearer |
| **Signing algorithm** | HS256 |
| **Access token lifetime** | 30 minutes |
| **Refresh token lifetime** | 30 days |
| **Refresh token storage** | HttpOnly cookie — `refresh_token` |
| **Refresh token rotation** | Each `/auth/refresh` call issues a **new** access + refresh pair |
| **Password hashing** | `pwdlib` (argon2 or bcrypt recommended) |

> [!CAUTION]
> **Production guard:** The server refuses to start if `JWT_SECRET_KEY` is left at its default value. This prevents accidental deployment with an insecure secret.

---

## 2. Auth Endpoints

| Method | Endpoint | Description | Notes |
|---|---|---|---|
| `POST` | `/auth/register` | Create a new account | Phone **or** email required |
| `POST` | `/auth/login` | Obtain access + refresh tokens | Rate-limited: **5 requests / minute** |
| `POST` | `/auth/refresh` | Rotate token pair | Reads `refresh_token` HttpOnly cookie; issues new pair |
| `POST` | `/auth/logout` | Invalidate session | Clears the `refresh_token` cookie |
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
> The `X-User-ID` header bypass is **only** active when `DEBUG=true`. It must never be reachable in production. This header is accepted as a convenience during local development and testing.

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

*AI-Powered Smart Farming — Documentation*  
*Last Updated: September 2026*
