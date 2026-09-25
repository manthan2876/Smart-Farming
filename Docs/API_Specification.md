# Smart Farming — Backend API Specification

**Project:** AI-Powered Smart Farming  
**Version:** 1.0  
**Date:** September 2026  
**Status:** Active / Production Reference  

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication & Security](#2-authentication--security)
3. [Common Conventions](#3-common-conventions)
4. [Error Reference](#4-error-reference)
5. [Auth Endpoints](#5-auth-endpoints-auth)
6. [Prediction Endpoints](#6-prediction-endpoints)
7. [History Endpoints](#7-history-endpoints)
8. [Feedback Endpoints](#8-feedback-endpoints)
9. [Expert Endpoints](#9-expert-endpoints)
10. [Farm Endpoints](#10-farm-endpoints-farm)
11. [Admin Endpoints](#11-admin-endpoints-admin)
12. [Weather Endpoints](#12-weather-endpoints)
13. [Crops Endpoints](#13-crops-endpoints)
14. [Alerts Endpoints](#14-alerts-endpoints)
15. [TTS Endpoint](#15-tts-endpoint)
16. [Translation Endpoint](#16-translation-endpoint)
17. [MLOps / Model Registry Endpoints](#17-mlops--model-registry-endpoints)
18. [Health Endpoint](#18-health-endpoint)
19. [WebSocket Protocol](#19-websocket-protocol)
20. [Data Models](#20-data-models)

---

## 1. Overview

The Smart Farming backend is an AI-powered crop disease detection and advisory platform. It exposes a REST API consumed by mobile and web clients. The platform operates in two modes:

- **Serverless Production (Google Cloud Run):** Prediction requests run synchronously (`REQUIRE_REDIS=False`) to allow scaling to 0 instances when idle. Image deduplication (`sf:dedup:{hash}`), phrase translations (`sf:trans:{lang}:{hash}`), and weather (`sf:weather:{lat}:{lon}`) are cached via Upstash Serverless Redis REST.
- **Asynchronous Task Queue (Local Dev / Dedicated Host):** `REQUIRE_REDIS=True` enqueues prediction jobs into ARQ, publishing real-time stage progress over WebSocket.

### Technology Stack

| Layer | Technology | Deployment Details |
|---|---|---|
| **API Gateway** | FastAPI (Python 3.11) | Cloud Run Service #1 (`smart-farming-backend`, 512MiB, Public) |
| **Inference Microservice** | FastAPI + PyTorch CPU | Cloud Run Service #2 (`inference-service`, 2GiB, Private OIDC) |
| **Auth** | JWT (HS256) | Bearer tokens in headers, HttpOnly refresh cookies |
| **Serverless Cache** | Upstash Redis REST | HTTPS Token Auth (`sf:*` namespace, sub-20ms latency) |
| **Task Queue** | ARQ (async Redis Queue) | Active when `REQUIRE_REDIS=True` |
| **Relational Database** | PostgreSQL 15+ | Supabase Managed PostgreSQL with SSL (`sslmode=require`) |
| **Object Storage** | Google Cloud Storage | Multi-regional bucket `smart-farming-data` via S3 HMAC XML API |
| **Real-time** | WebSocket | `/ws/predictions/{id}` |
| **ML Models** | EfficientNet-B0/B2, YOLOv8 | Qwen3-4B Agronomist LLM via HuggingFace API |

---

## 2. Authentication & Security

### JWT Bearer Token

All protected endpoints require an `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Token Lifecycle

| Token | Transport | Expiry |
|---|---|---|
| Access Token | `Authorization: Bearer` header | 30 minutes |
| Refresh Token | HttpOnly cookie `refresh_token` | 30 days |

- **Algorithm:** HS256  
- The refresh token is set as an `HttpOnly`, `Secure`, `SameSite=Strict` cookie on login and cleared on logout.  
- Use `POST /auth/refresh` to obtain a new access token before expiry.

### Roles

| Role | Capabilities |
|---|---|
| `farmer` | Default role. Full prediction, farm, history, alerts access. |
| `expert` | All farmer capabilities + expert review queue, feedback review. |
| `admin` | All expert capabilities + admin metrics, user management, config, MLOps. |

### Rate Limits

| Endpoint | Limit |
|---|---|
| `POST /auth/login` | 5 requests / minute |
| `POST /predict` | 20 requests / minute |
| `POST /predictions/{id}/request-expert` | 5 requests / minute |

Exceeded limits return **429 Too Many Requests**.

---

## 3. Common Conventions

### Request Headers

```
Content-Type: application/json       (for JSON bodies)
Content-Type: multipart/form-data    (for file uploads)
Authorization: Bearer <access_token>
```

### Pagination

History and list endpoints support cursor-based pagination:

| Query Param | Type | Description |
|---|---|---|
| `offset` | integer | Number of records to skip (offset-based) |
| `limit` | integer | Records per page. Range: `1–100`. Default: `20` |
| `last_id` | integer | Cursor ID for keyset pagination (alternative to offset) |

### Date Filtering

Use ISO 8601 format for date query parameters:

```
start_date=2025-01-01T00:00:00Z
end_date=2025-12-31T23:59:59Z
```

### Language Support

All endpoints accepting a `language` parameter use a string matching the user's preferred locale (e.g., `"Gujarati"`, `"Hindi"`, `"English"`). Responses such as recommendations and TTS are generated in that language.

---

## 4. Error Reference

All error responses follow the structure:

```json
{
  "detail": "Human-readable error message"
}
```

### HTTP Status Codes

| Status Code | Meaning | Common Causes |
|---|---|---|
| `400 Bad Request` | Client-side input error | Blurry image, bad lighting, no leaf detected, invalid request data |
| `401 Unauthorized` | Authentication failure | Missing, expired, or invalid JWT token |
| `403 Forbidden` | Authorization failure | Insufficient role (e.g., farmer accessing expert route) |
| `404 Not Found` | Resource missing | Prediction, feedback, plot, or review not found |
| `409 Conflict` | Duplicate resource | Phone/email already registered; feedback already submitted |
| `413 Content Too Large` | File too large | Image exceeds 10 MB limit |
| `415 Unsupported Media Type` | Wrong file type | Non-image or unsupported format uploaded |
| `422 Unprocessable Entity` | Validation error | Missing required field, invalid field type/value |
| `429 Too Many Requests` | Rate limit exceeded | See rate limit table above |
| `503 Service Unavailable` | Backend unavailable | Database or ARQ worker is down |

---

## 5. Auth Endpoints (`/auth`)

### 5.1 Register User

```
POST /auth/register
```

Creates a new user account and returns tokens alongside the user profile. Farm details provided here are stored and associated with the user.

**Authentication:** None required.

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✅ | Full name of the user |
| `password` | string | ✅ | Account password |
| `phone` | string | ❌ | Phone number (used as login identifier) |
| `email` | string | ❌ | Email address (used as login identifier) |
| `language` | string | ❌ | Preferred language (e.g., `"Gujarati"`) |
| `location` | string | ❌ | Human-readable farm location |
| `latitude` | float | ❌ | Farm latitude coordinate |
| `longitude` | float | ❌ | Farm longitude coordinate |
| `crop_history` | array | ❌ | List of previously grown crops |
| `farm_name` | string | ❌ | Name of the farm |
| `farm_area_acres` | float | ❌ | Total farm area in acres |

> At least one of `phone` or `email` must be provided to enable login.

#### Example Request

```json
{
  "name": "Ramesh Patel",
  "phone": "9876543210",
  "password": "farming123",
  "language": "Gujarati",
  "location": "Anand, Gujarat",
  "farm_name": "Patel Farms"
}
```

#### Example Response `201 Created`

```json
{
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Ramesh Patel",
    "phone": "9876543210",
    "email": null,
    "role": "farmer",
    "language": "Gujarati",
    "location": "Anand, Gujarat",
    "farm_name": "Patel Farms"
  }
}
```

#### Error Responses

| Status | Condition |
|---|---|
| `409 Conflict` | Phone or email already registered |
| `422 Unprocessable Entity` | Missing required fields or invalid values |

---

### 5.2 Login

```
POST /auth/login
```

Authenticates a user by phone or email and password. Sets the `refresh_token` HttpOnly cookie on the response.

**Authentication:** None required.  
**Rate Limit:** 5 requests / minute per IP.

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `identifier` | string | ✅ | Phone number or email address |
| `password` | string | ✅ | Account password |

#### Example Request

```json
{
  "identifier": "9876543210",
  "password": "farming123"
}
```

#### Example Response `200 OK`

```json
{
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Ramesh Patel",
    "phone": "9876543210",
    "role": "farmer",
    "language": "Gujarati"
  }
}
```

**Side effect:** Response sets `Set-Cookie: refresh_token=<token>; HttpOnly; Secure; SameSite=Strict`.

#### Error Responses

| Status | Condition |
|---|---|
| `401 Unauthorized` | Invalid identifier or password |
| `429 Too Many Requests` | Rate limit exceeded |

---

### 5.3 Refresh Token

```
POST /auth/refresh
```

Issues a new access token using the refresh token stored in the HttpOnly cookie. Also rotates the refresh token (issues a new one).

**Authentication:** HttpOnly `refresh_token` cookie (no Bearer header required).

#### Request Body

No body required.

#### Example Response `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Error Responses

| Status | Condition |
|---|---|
| `401 Unauthorized` | Missing, expired, or revoked refresh cookie |

---

### 5.4 Logout

```
POST /auth/logout
```

Invalidates the current session by clearing the refresh token cookie.

**Authentication:** Bearer token (optional but recommended).

#### Request Body

No body required.

#### Example Response `200 OK`

```json
{
  "detail": "Successfully logged out"
}
```

**Side effect:** Response sets `Set-Cookie: refresh_token=; HttpOnly; Max-Age=0` to clear the cookie.

---

### 5.5 Change Password

```
POST /auth/change-password
```

Updates the authenticated user's password.

**Authentication:** Bearer token required.

#### Request Body (`application/json`)

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `old_password` | string | ✅ | — | Current password for verification |
| `new_password` | string | ✅ | Min 8 characters | New password to set |

#### Example Request

```json
{
  "old_password": "farming123",
  "new_password": "newSecure#456"
}
```

#### Example Response `200 OK`

```json
{
  "detail": "Password updated successfully"
}
```

#### Error Responses

| Status | Condition |
|---|---|
| `401 Unauthorized` | Old password is incorrect |
| `422 Unprocessable Entity` | New password shorter than 8 characters |

---

## 6. Prediction Endpoints

The prediction pipeline is asynchronous. Submitting `POST /predict` enqueues an ARQ job and returns immediately. Clients should track progress via WebSocket and fetch results via `GET /predictions/{id}`.

### 6.1 Submit Prediction

```
POST /predict
```

Uploads a leaf image for AI-based crop disease analysis. Validates the image before enqueuing the processing job.

**Authentication:** Bearer token required.  
**Rate Limit:** 20 requests / minute.  
**Content-Type:** `multipart/form-data`

#### Image Validation Rules

| Check | Rule |
|---|---|
| File type | JPEG, PNG, or WebP only (validated by magic bytes) |
| File size | Maximum 10 MB |
| Blur | Image must not be excessively blurry |
| Lighting | Image must have adequate exposure |
| Leaf presence | At least one leaf-like region must be detectable |

#### Form Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | file | ✅ | Leaf image (JPEG / PNG / WebP, max 10 MB) |
| `location` | string | ❌ | Human-readable location string |
| `lat` | float | ❌ | Latitude for weather correlation |
| `lon` | float | ❌ | Longitude for weather correlation |
| `language` | string | ❌ | Override user's default language for this result |
| `plot_id` | integer | ❌ | Associate scan with a specific farm plot |

#### Example Request

```
POST /predict HTTP/1.1
Content-Type: multipart/form-data; boundary=----FormBoundary

------FormBoundary
Content-Disposition: form-data; name="file"; filename="leaf.jpg"
Content-Type: image/jpeg

<binary image data>
------FormBoundary
Content-Disposition: form-data; name="lat"

22.5
------FormBoundary
Content-Disposition: form-data; name="lon"

72.9
------FormBoundary
Content-Disposition: form-data; name="location"

Anand, Gujarat
------FormBoundary
Content-Disposition: form-data; name="language"

Gujarati
------FormBoundary--
```

#### Example Response `200 OK` (Immediate Placeholder)

```json
{
  "prediction_id": 42,
  "job_id": "abc123-def456-ghi789",
  "status": {
    "pipeline": "processing",
    "preprocessing": "completed",
    "crop_identification": "pending",
    "disease_identification": "pending",
    "severity_analysis": "pending",
    "pest_detection": "pending",
    "recommendation": "pending"
  },
  "crop": {},
  "disease": {},
  "severity": {}
}
```

#### Error Responses

| Status | Condition |
|---|---|
| `400 Bad Request` | Blurry image, bad lighting, or no leaf detected |
| `413 Content Too Large` | Image exceeds 10 MB |
| `415 Unsupported Media Type` | Not a JPEG/PNG/WebP image |

---

### 6.2 Get Prediction Result

```
GET /predict/{prediction_id}
GET /predictions/{prediction_id}
```

Returns the full prediction result for a completed or in-progress scan. Both paths are equivalent aliases.

**Authentication:** Bearer token required (own predictions only, unless `expert` or `admin`).

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `prediction_id` | integer | The prediction ID returned by `POST /predict` |

#### Example Response `200 OK` (Completed)

```json
{
  "prediction_id": 42,
  "plot_id": 7,
  "created_at": "2026-09-22T10:35:00Z",
  "crop": {
    "label": "Tomato",
    "confidence": 0.97,
    "confidence_rating": "high"
  },
  "disease": {
    "label": "Early Blight",
    "confidence": 0.89,
    "confidence_rating": "high",
    "is_uncertain": false
  },
  "severity": {
    "percent": 34.2,
    "bucket": "Moderate",
    "affected_area": 0.342
  },
  "pests": [
    {
      "label": "Aphid",
      "confidence": 0.61
    }
  ],
  "weather": {
    "temperature_celsius": 28.4,
    "humidity_percent": 75,
    "condition": "Clouds"
  },
  "recommendation": {
    "immediate_action": "Remove and dispose of heavily infected leaves immediately to prevent spread.",
    "treatment": "Apply chlorothalonil fungicide at label rate every 7–10 days.",
    "prevention": "Ensure proper plant spacing for adequate airflow. Avoid overhead irrigation.",
    "monitoring": "Check daily for spread over next 7 days. Look for new lesions on upper leaves.",
    "provider": "HuggingFace / nscale",
    "is_fallback": false
  },
  "status": {
    "pipeline": "completed",
    "preprocessing": "completed",
    "crop_identification": "completed",
    "disease_identification": "completed",
    "severity_analysis": "completed",
    "pest_detection": "completed",
    "recommendation": "completed"
  },
  "provenance": {
    "schema_version": "2.0.0",
    "pipeline_duration_ms": 4230,
    "models": {
      "crop": {
        "name": "EfficientNet-B0",
        "version": "v1.0"
      },
      "disease": {
        "name": "DiseaseNet-v2",
        "version": "v2.1"
      }
    }
  },
  "historical_images": [],
  "expert_review_data": null,
  "follow_up": null
}
```

#### Rescan-specific Fields

| Field | Present When | Description |
|---|---|---|
| `historical_images` | Prediction is a rescan | Array of parent prediction summaries (chain) |
| `expert_review_data` | Expert has verified the prediction | Expert review details and corrections |
| `follow_up` | A newer rescan exists | Summary of the latest child prediction |

---

### 6.3 Submit Rescan

```
POST /predictions/{prediction_id}/rescan
```

Upload a follow-up image for the same crop/plot. Creates a new child prediction linked to the parent, enabling progress tracking over time.

**Authentication:** Bearer token required.  
**Content-Type:** `multipart/form-data`

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `prediction_id` | integer | The original (parent) prediction ID |

#### Form Fields

Same as `POST /predict` (see [Section 6.1](#61-submit-prediction)).

#### Example Response `200 OK`

Same structure as `POST /predict` response, with `historical_images` populated.

---

### 6.4 Get Job Status

```
GET /job/{job_id}
```

Checks the status of an ARQ background job. Useful as a fallback if WebSocket is unavailable.

**Authentication:** None required.

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `job_id` | string | ARQ job ID returned by `POST /predict` |

#### Example Response `200 OK`

```json
{
  "job_id": "abc123-def456-ghi789",
  "status": "in_progress",
  "result": null,
  "error": null
}
```

#### Job Status Values

| Value | Meaning |
|---|---|
| `queued` | Job is waiting to be picked up by a worker |
| `in_progress` | Job is currently being processed |
| `complete` | Job finished successfully |
| `not_found` | No job with this ID exists |
| `failed` | Job encountered an unrecoverable error |

---

### 6.5 Request Expert Review

```
POST /predictions/{prediction_id}/request-expert
```

Allows a farmer to escalate a prediction for manual expert review when they disagree with or are unsatisfied by the automated result.

**Authentication:** Bearer token required.  
**Rate Limit:** 5 requests / minute.

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `prediction_id` | integer | The prediction to escalate |

#### Request Body

No body required.

#### Example Response `201 Created`

```json
{
  "detail": "Expert review requested successfully",
  "review_id": 15
}
```

---

### 6.6 Get Presigned Media URL

```
GET /predictions/{prediction_id}/media-url/{media_type}
```

Returns a short-lived presigned URL (15-minute expiry) for secure access to prediction media assets stored in object storage.

**Authentication:** Bearer token required.  
**Access Control:** Owner, reviewing expert, or admin only.

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `prediction_id` | integer | The prediction ID |
| `media_type` | string | See media type table below |

#### Media Types

| `media_type` | Description |
|---|---|
| `raw` | Original uploaded image (pre-processing) |
| `image` | Processed/normalized image |
| `processed` | Post-pipeline annotated image |
| `mask` | Disease segmentation mask overlay |
| `audio` | TTS audio narration file |
| `tts` | Alias for `audio` |

#### Example Response `200 OK`

```json
{
  "url": "https://storage.example.com/predictions/42/mask.png?X-Amz-Expires=900&X-Amz-Signature=...",
  "expires_in": 900,
  "media_type": "mask"
}
```

---

### 6.7 Stream Media Directly

```
GET /predictions/{prediction_id}/media/{media_type}
```

Streams the media file directly or redirects to the presigned URL. Suitable for direct browser `<img>` or `<audio>` src usage.

**Authentication:** Bearer token required.  
**Access Control:** Same as `/media-url`.

Response is either:
- `200 OK` with the binary file stream, or
- `302 Found` redirect to the presigned URL.

---

## 7. History Endpoints

### 7.1 Get Prediction History

```
GET /history
```

Returns a paginated list of the authenticated user's prediction summaries, with filtering options.

**Authentication:** Bearer token required.

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `offset` | integer | `0` | Number of records to skip |
| `limit` | integer | `20` | Records per page (`1–100`) |
| `last_id` | integer | — | Cursor ID for keyset pagination (use instead of offset) |
| `crop` | string | — | Filter by crop label (e.g., `Tomato`) |
| `disease` | string | — | Filter by disease label (e.g., `Early Blight`) |
| `status` | string | — | Filter by pipeline status (`completed`, `processing`, `failed`) |
| `start_date` | datetime | — | Filter scans on or after this date (ISO 8601) |
| `end_date` | datetime | — | Filter scans on or before this date (ISO 8601) |
| `plot_id` | integer | — | Filter by farm plot ID |

#### Example Response `200 OK`

```json
{
  "total": 156,
  "offset": 0,
  "limit": 20,
  "items": [
    {
      "prediction_id": 42,
      "created_at": "2026-09-22T10:35:00Z",
      "crop": "Tomato",
      "disease": "Early Blight",
      "severity_bucket": "Moderate",
      "status": "completed",
      "plot_id": 7,
      "has_expert_review": false
    }
  ]
}
```

---

## 8. Feedback Endpoints

### 8.1 Submit Feedback

```
POST /feedback
```

Allows a farmer to provide feedback on whether a prediction result was accurate.

**Authentication:** Bearer token required (own predictions only).

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `prediction_id` | integer | ✅ | The prediction being reviewed |
| `is_correct` | boolean | ✅ | Whether the farmer believes the diagnosis is correct |
| `farmer_note` | string | ❌ | Optional free-text note from the farmer |

#### Example Request

```json
{
  "prediction_id": 42,
  "is_correct": false,
  "farmer_note": "The disease looks more like Late Blight to me, not Early Blight."
}
```

#### Example Response `201 Created`

```json
{
  "feedback_id": 101,
  "prediction_id": 42,
  "is_correct": false,
  "farmer_note": "The disease looks more like Late Blight to me, not Early Blight.",
  "status": "pending",
  "created_at": "2026-09-22T11:00:00Z"
}
```

#### Error Responses

| Status | Condition |
|---|---|
| `404 Not Found` | Prediction does not exist or belongs to another user |
| `409 Conflict` | Feedback already submitted for this prediction |

---

### 8.2 Update Feedback

```
PUT /feedback/{feedback_id}
```

Update previously submitted feedback (own feedback only).

**Authentication:** Bearer token required.

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `feedback_id` | integer | The feedback record to update |

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `is_correct` | boolean | ❌ | Updated correctness flag |
| `farmer_note` | string | ❌ | Updated free-text note |

#### Example Response `200 OK`

```json
{
  "feedback_id": 101,
  "is_correct": true,
  "farmer_note": "On reflection it was correct.",
  "status": "pending",
  "updated_at": "2026-09-22T12:00:00Z"
}
```

---

### 8.3 Review Feedback (Expert)

```
POST /feedback/{feedback_id}/review
```

Allows an expert to approve or reject farmer feedback. If a feedback is approved and the original prediction was incorrect, a `DatasetCandidate` record is created for model retraining.

**Authentication:** Bearer token required.  
**Role Required:** `expert` or `admin`.

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `feedback_id` | integer | The feedback to review |

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `status` | string | ✅ | `"approved"` or `"rejected"` |
| `reviewer_note` | string | ❌ | Internal note from the expert |
| `corrected_label` | string | ❌ | Correct disease label if the prediction was wrong |

#### Example Request

```json
{
  "status": "approved",
  "reviewer_note": "Farmer is correct. Image clearly shows Late Blight symptoms.",
  "corrected_label": "Late Blight"
}
```

#### Example Response `200 OK`

```json
{
  "feedback_id": 101,
  "status": "approved",
  "corrected_label": "Late Blight",
  "dataset_candidate_created": true
}
```

---

## 9. Expert Endpoints

Expert endpoints are restricted to users with the `expert` or `admin` role. They manage the manual review workflow for escalated predictions.

### 9.1 Get Expert Review Queue

```
GET /expert/queue
```

Returns all pending expert review requests.

**Authentication:** Bearer token required.  
**Role Required:** `expert` or `admin`.

#### Example Response `200 OK`

```json
{
  "total": 3,
  "items": [
    {
      "review_id": 15,
      "prediction_id": 42,
      "farmer_id": "uuid-...",
      "farmer_name": "Ramesh Patel",
      "crop": "Tomato",
      "disease": "Early Blight",
      "severity_bucket": "Moderate",
      "requested_at": "2026-09-22T11:05:00Z",
      "status": "pending"
    }
  ]
}
```

---

### 9.2 Get Review Detail

```
GET /expert/reviews/{review_id}
```

Returns full detail for a single expert review, including crop/disease predictions and image URLs.

**Authentication:** Bearer token required.  
**Role Required:** `expert` or `admin`.

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `review_id` | integer | The expert review ID |

#### Example Response `200 OK`

```json
{
  "review_id": 15,
  "prediction_id": 42,
  "status": "pending",
  "farmer": {
    "id": "uuid-...",
    "name": "Ramesh Patel",
    "phone": "9876543210",
    "location": "Anand, Gujarat"
  },
  "prediction": {
    "crop": "Tomato",
    "disease": "Early Blight",
    "severity": {"percent": 34.2, "bucket": "Moderate"},
    "confidence": 0.89
  },
  "images": {
    "raw_url": "https://storage.example.com/...",
    "processed_url": "https://storage.example.com/...",
    "mask_url": "https://storage.example.com/..."
  },
  "farmer_feedback": {
    "is_correct": false,
    "farmer_note": "Looks like Late Blight to me."
  },
  "requested_at": "2026-09-22T11:05:00Z"
}
```

---

### 9.3 Submit Expert Review Decision

```
POST /expert/reviews/{review_id}
```

Submits an expert's decision on a pending review. Triggers farmer notification via the Alerts system.

**Authentication:** Bearer token required.  
**Role Required:** `expert` or `admin`.

> **State Machine:** Only reviews with `status = "pending"` can be submitted. Attempting to resubmit a completed review returns `409 Conflict`.

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `review_id` | integer | The expert review to decide on |

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | string | ✅ | One of `"Approve"`, `"Override / Correct Findings"`, `"Request Rescan"` |
| `corrected_disease` | string | ❌ | Required if action is `"Override / Correct Findings"` |
| `corrected_severity` | string | ❌ | Corrected severity bucket (e.g., `"Severe"`) |
| `farmer_guidance` | string | ❌ | Advice for the farmer (included in the alert) |
| `internal_note` | string | ❌ | Internal note not shown to farmer |
| `add_to_retraining` | boolean | ❌ | If `true`, creates a `DatasetCandidate` for model retraining |

#### Action Outcomes

| `action` | Outcome |
|---|---|
| `"Approve"` | Confirms existing prediction. Sets review `status = "verified"`. Sends farmer alert. |
| `"Override / Correct Findings"` | Updates prediction with corrections. Sends updated alert with `farmer_guidance`. |
| `"Request Rescan"` | Notifies farmer to upload a new image. Review remains open pending rescan. |

#### Example Request

```json
{
  "action": "Override / Correct Findings",
  "corrected_disease": "Late Blight",
  "corrected_severity": "Severe",
  "farmer_guidance": "This is Late Blight, which spreads rapidly. Remove infected plants immediately and apply copper-based fungicide.",
  "internal_note": "Farmer's original diagnosis was incorrect. Lesions show water-soaked appearance typical of Late Blight.",
  "add_to_retraining": true
}
```

#### Example Response `200 OK`

```json
{
  "review_id": 15,
  "status": "verified",
  "action": "Override / Correct Findings",
  "corrected_disease": "Late Blight",
  "alert_id": 88,
  "dataset_candidate_created": true
}
```

---

## 10. Farm Endpoints (`/farm`)

### 10.1 Get Farm

```
GET /farm
```

Returns the authenticated user's farm profile and all associated plots.

**Authentication:** Bearer token required.

#### Example Response `200 OK`

```json
{
  "farm": {
    "id": 5,
    "name": "Patel Farms",
    "location": "Anand, Gujarat",
    "latitude": 22.5,
    "longitude": 72.9,
    "area_acres": 12.5,
    "crop_history": ["Tomato", "Cotton", "Wheat"],
    "boundary": {
      "type": "Polygon",
      "coordinates": [[[72.88, 22.50], [72.92, 22.50], [72.92, 22.54], [72.88, 22.54], [72.88, 22.50]]]
    }
  },
  "plots": [
    {
      "plot_id": 7,
      "name": "North Field",
      "crop": "Tomato",
      "area_acres": 4.0,
      "boundary": null
    }
  ]
}
```

---

### 10.2 Create or Update Farm

```
POST /farm
PUT  /farm
```

Creates the farm if it does not exist for this user, or updates it if it does. Both methods are functionally equivalent (upsert).

**Authentication:** Bearer token required.

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | ❌ | Farm name |
| `location` | string | ❌ | Human-readable location |
| `latitude` | float | ❌ | Latitude coordinate |
| `longitude` | float | ❌ | Longitude coordinate |
| `area_acres` | float | ❌ | Total farm area in acres |
| `crop_history` | array[string] | ❌ | List of historically grown crops |
| `boundary` | GeoJSON Polygon | ❌ | Farm boundary as GeoJSON Polygon geometry |

#### Example Request

```json
{
  "name": "Patel Farms",
  "location": "Anand, Gujarat",
  "latitude": 22.5,
  "longitude": 72.9,
  "area_acres": 12.5,
  "boundary": {
    "type": "Polygon",
    "coordinates": [[[72.88, 22.50], [72.92, 22.50], [72.92, 22.54], [72.88, 22.54], [72.88, 22.50]]]
  }
}
```

#### Example Response `200 OK`

```json
{
  "id": 5,
  "name": "Patel Farms",
  "location": "Anand, Gujarat",
  "latitude": 22.5,
  "longitude": 72.9,
  "area_acres": 12.5
}
```

---

### 10.3 List Plots

```
GET /farm/plots
```

Returns all plots associated with the current user's farm.

**Authentication:** Bearer token required.

#### Example Response `200 OK`

```json
[
  {
    "plot_id": 7,
    "name": "North Field",
    "crop": "Tomato",
    "area_acres": 4.0,
    "boundary": null
  },
  {
    "plot_id": 8,
    "name": "South Field",
    "crop": "Cotton",
    "area_acres": 8.5,
    "boundary": null
  }
]
```

---

### 10.4 Create Plot

```
POST /farm/plots
```

Creates a new plot under the current user's farm.

**Authentication:** Bearer token required.

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✅ | Plot name |
| `crop` | string | ✅ | Current crop grown in this plot |
| `area_acres` | float | ❌ | Plot area in acres |
| `boundary` | GeoJSON Polygon | ❌ | Plot boundary as GeoJSON Polygon geometry |

#### Example Request

```json
{
  "name": "East Plot",
  "crop": "Wheat",
  "area_acres": 2.5
}
```

#### Example Response `201 Created`

```json
{
  "plot_id": 9,
  "name": "East Plot",
  "crop": "Wheat",
  "area_acres": 2.5,
  "boundary": null
}
```

---

### 10.5 Update Plot

```
PUT /farm/plots/{plot_id}
```

Updates an existing plot. Accepts the same fields as `POST /farm/plots` (all optional).

**Authentication:** Bearer token required.

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `plot_id` | integer | The plot to update |

---

### 10.6 Delete Plot

```
DELETE /farm/plots/{plot_id}
```

Permanently deletes a plot. Associated predictions retain the `plot_id` reference.

**Authentication:** Bearer token required.

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `plot_id` | integer | The plot to delete |

#### Example Response `200 OK`

```json
{
  "detail": "Plot deleted successfully"
}
```

---

## 11. Admin Endpoints (`/admin`)

All admin endpoints require the `admin` role unless otherwise noted.

### 11.1 Get System Metrics

```
GET /admin/metrics
```

Returns comprehensive system health, performance, and ML drift metrics.

**Authentication:** Bearer token required.  
**Role Required:** `admin`.

#### Example Response `200 OK`

```json
{
  "total_users": 1240,
  "total_scans": 8735,
  "accuracy": 0.912,
  "queue_depth": 3,
  "failures": 12,
  "processing_duration": {
    "avg_ms": 4100,
    "p95_ms": 7800
  },
  "fallbacks": 45,
  "expert_metrics": {
    "pending_reviews": 3,
    "completed_reviews": 87,
    "avg_resolution_hours": 14.2
  },
  "disease_distribution": {
    "Early Blight": 1240,
    "Late Blight": 870,
    "Leaf Miner": 612
  },
  "confidence_histogram": {
    "0.0-0.2": 23,
    "0.2-0.4": 91,
    "0.4-0.6": 430,
    "0.6-0.8": 2100,
    "0.8-1.0": 6091
  },
  "drift": {
    "avg_confidence_7d": 0.847,
    "avg_confidence_30d": 0.861,
    "low_confidence_rate": 0.034,
    "retraining_candidates": 17,
    "expert_correction_rate": 0.089
  }
}
```

---

### 11.2 Purge All Data

```
DELETE /admin/purge
```

Irreversibly deletes all data from the system. Requires explicit confirmation.

**Authentication:** Bearer token required.  
**Role Required:** `admin`.

> **⚠ CAUTION:** This action is irreversible. Always run with `dry_run=true` first.

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `dry_run` | boolean | `false` | Preview what would be deleted without deleting |

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `confirmation` | string | ✅ | Must be exactly `"PURGE_ALL_DATA"` |

#### Example Response `200 OK` (dry_run=true)

```json
{
  "dry_run": true,
  "would_delete": {
    "users": 1240,
    "predictions": 8735,
    "feedback": 342,
    "expert_reviews": 90,
    "alerts": 2100
  }
}
```

---

### 11.3 List Users

```
GET /admin/users
```

Returns a paginated list of all registered users with optional filters.

**Authentication:** Bearer token required.  
**Role Required:** `admin`.

#### Query Parameters

| Parameter | Type | Description |
|---|---|---|
| `skip` | integer | Offset (default `0`) |
| `limit` | integer | Page size (default `20`) |
| `role` | string | Filter by role: `farmer`, `expert`, `admin` |
| `search` | string | Search by name, phone, or email |

#### Example Response `200 OK`

```json
{
  "total": 1240,
  "items": [
    {
      "id": "uuid-...",
      "name": "Ramesh Patel",
      "phone": "9876543210",
      "email": null,
      "role": "farmer",
      "created_at": "2025-06-01T08:00:00Z",
      "total_scans": 14
    }
  ]
}
```

---

### 11.4 Change User Role

```
PATCH /admin/users/{user_id}/role
```

Updates the role of a specific user.

**Authentication:** Bearer token required.  
**Role Required:** `admin`.

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `user_id` | string (UUID) | The user whose role should change |

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `role` | string | ✅ | New role: `"farmer"`, `"expert"`, or `"admin"` |
| `reason` | string | ❌ | Reason for the role change (audit log) |

#### Guards

| Guard | Behavior |
|---|---|
| Self-demotion | An admin cannot change their own role |
| Last-admin protection | The last remaining admin cannot be demoted |

#### Example Response `200 OK`

```json
{
  "user_id": "uuid-...",
  "old_role": "farmer",
  "new_role": "expert",
  "changed_by": "uuid-admin-...",
  "reason": "Promoted after verification."
}
```

---

### 11.5 Trigger Weather Risk Evaluation

```
POST /admin/weather-risk/trigger
```

Manually triggers the proactive weather risk evaluation job for all farms. Normally runs on a schedule.

**Authentication:** Bearer token required.  
**Role Required:** `admin`.

#### Example Response `200 OK`

```json
{
  "detail": "Weather risk evaluation triggered",
  "job_id": "weather-risk-xyz"
}
```

---

### 11.6 Get All Feedback (Admin/Expert)

```
GET /admin/feedback
```

Returns all feedback records across all users.

**Authentication:** Bearer token required.  
**Role Required:** `expert` or `admin`.

#### Example Response `200 OK`

```json
{
  "total": 342,
  "items": [
    {
      "feedback_id": 101,
      "prediction_id": 42,
      "farmer_id": "uuid-...",
      "is_correct": false,
      "farmer_note": "Looks like Late Blight.",
      "status": "approved",
      "created_at": "2026-09-22T11:00:00Z"
    }
  ]
}
```

---

### 11.7 Get System Config

```
GET /admin/config
```

Returns the current system configuration thresholds.

**Authentication:** Bearer token required.  
**Role Required:** `admin`.

#### Example Response `200 OK`

```json
{
  "crop_routing_threshold": 0.75,
  "expert_escalation_cutoff": 0.50
}
```

---

### 11.8 Update System Config

```
PUT /admin/config
```

Updates configuration thresholds. Changes take effect immediately (hot-reload) in the API and are broadcast via Redis to all workers.

**Authentication:** Bearer token required.  
**Role Required:** `admin`.

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `crop_routing_threshold` | float | ✅ | Minimum confidence to route to disease model |
| `expert_escalation_cutoff` | float | ✅ | Confidence below which to recommend expert review |

#### Example Request

```json
{
  "crop_routing_threshold": 0.80,
  "expert_escalation_cutoff": 0.55
}
```

#### Example Response `200 OK`

```json
{
  "crop_routing_threshold": 0.80,
  "expert_escalation_cutoff": 0.55,
  "reloaded": true,
  "workers_notified": 4
}
```

---

### 11.9 Purge Orphaned Blobs

```
DELETE /admin/blobs
```

Removes storage objects that are no longer referenced by any prediction record.

**Authentication:** Bearer token required.  
**Role Required:** `admin`.

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `dry_run` | boolean | `false` | Preview orphans without deleting |

#### Example Response `200 OK`

```json
{
  "dry_run": false,
  "deleted_count": 23,
  "freed_bytes": 182374920
}
```

---

## 12. Weather Endpoints

### 12.1 Get Current Weather

```
GET /weather
```

Returns current weather data for the authenticated user's farm location (using stored latitude/longitude).

**Authentication:** Bearer token required.

#### Example Response `200 OK`

```json
{
  "location": "Anand, Gujarat",
  "latitude": 22.5,
  "longitude": 72.9,
  "temperature_celsius": 28.4,
  "humidity_percent": 75,
  "wind_speed_kmh": 14,
  "condition": "Clouds",
  "condition_code": 803,
  "fetched_at": "2026-09-22T10:00:00Z"
}
```

---

## 13. Crops Endpoints

### 13.1 Get Supported Crops

```
GET /crops
```

Returns the list of crops supported by the AI pipeline.

**Authentication:** None required.

#### Example Response `200 OK`

```json
{
  "crops": [
    {"id": "tomato", "label": "Tomato", "diseases": ["Early Blight", "Late Blight", "Leaf Curl"]},
    {"id": "cotton", "label": "Cotton", "diseases": ["Leaf Miner", "Bollworm", "Blight"]},
    {"id": "wheat", "label": "Wheat", "diseases": ["Rust", "Smut", "Blight"]}
  ]
}
```

---

## 14. Alerts Endpoints

### 14.1 Get Alerts

```
GET /alerts
```

Returns all alerts for the authenticated user (e.g., expert review decisions, weather risk warnings).

**Authentication:** Bearer token required.

#### Example Response `200 OK`

```json
{
  "total": 5,
  "unread": 2,
  "items": [
    {
      "alert_id": 88,
      "type": "expert_review_complete",
      "title": "Expert Review Complete",
      "message": "An expert has reviewed your scan #42. The diagnosis has been updated to Late Blight.",
      "is_read": false,
      "created_at": "2026-09-22T14:30:00Z",
      "metadata": {
        "prediction_id": 42,
        "review_id": 15
      }
    }
  ]
}
```

#### Alert Types

| `type` | Trigger |
|---|---|
| `expert_review_complete` | Expert finishes reviewing a prediction |
| `weather_risk` | Proactive weather risk detected for farm location |
| `rescan_requested` | Expert requests a follow-up image |

---

### 14.2 Mark Alert as Read

```
POST /alerts/{alert_id}/read
```

Marks a specific alert as read.

**Authentication:** Bearer token required (own alerts only).

#### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `alert_id` | integer | The alert to mark as read |

#### Example Response `200 OK`

```json
{
  "alert_id": 88,
  "is_read": true
}
```

---

## 15. TTS Endpoint

### 15.1 Generate Audio Narration

```
POST /tts/generate
```

Generates an audio narration of the prediction diagnosis and recommendation in the user's preferred language. The resulting audio file is stored and accessible via the media endpoints.

**Authentication:** Bearer token required.

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `prediction_id` | integer | ✅ | The prediction to narrate |

#### Example Request

```json
{
  "prediction_id": 42
}
```

#### Example Response `200 OK`

```json
{
  "prediction_id": 42,
  "audio_url": "https://storage.example.com/predictions/42/audio.mp3?...",
  "duration_seconds": 47,
  "language": "Gujarati"
}
```

---

## 16. Translation Endpoint

### 16.1 Translate Text

```
POST /translate
```

Translates arbitrary text into the authenticated user's preferred language. Used by the client for dynamic content not covered by static i18n.

**Authentication:** Bearer token required.

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `text` | string | ✅ | Source text to translate |
| `target_language` | string | ❌ | Override target language; defaults to user's profile language |

#### Example Request

```json
{
  "text": "Remove infected leaves and apply fungicide."
}
```

#### Example Response `200 OK`

```json
{
  "original": "Remove infected leaves and apply fungicide.",
  "translated": "ચેપગ્રસ્ત પાંદડા દૂર કરો અને ફૂગનાશક લગાવો.",
  "target_language": "Gujarati"
}
```

---

## 17. MLOps / Model Registry Endpoints

### 17.1 List Training Runs

```
GET /admin/mlops/runs
```

Returns the history of model training runs.

**Authentication:** Bearer token required.  
**Role Required:** `admin`.

#### Example Response `200 OK`

```json
{
  "runs": [
    {
      "run_id": "run-2026-09-20-001",
      "model_type": "disease",
      "started_at": "2026-09-20T02:00:00Z",
      "completed_at": "2026-09-20T05:35:00Z",
      "status": "success",
      "metrics": {
        "accuracy": 0.921,
        "f1_score": 0.908,
        "dataset_size": 14200
      },
      "checkpoint_path": "s3://models/disease/run-2026-09-20-001/"
    }
  ]
}
```

---

### 17.2 Promote Model to Production

```
POST /admin/models/promote
```

Promotes a trained model checkpoint to the production serving slot.

**Authentication:** Bearer token required.  
**Role Required:** `admin`.

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `run_id` | string | ✅ | The training run ID whose checkpoint to promote |
| `model_type` | string | ✅ | `"crop"` or `"disease"` |
| `reason` | string | ❌ | Reason for promotion (audit log) |

#### Example Request

```json
{
  "run_id": "run-2026-09-20-001",
  "model_type": "disease",
  "reason": "Improved F1 by 1.3% on held-out validation set."
}
```

#### Example Response `200 OK`

```json
{
  "model_type": "disease",
  "promoted_run_id": "run-2026-09-20-001",
  "previous_version": "v2.0",
  "new_version": "v2.1",
  "promoted_at": "2026-09-22T16:00:00Z"
}
```

---

### 17.3 List Registered Models

```
GET /admin/models
```

Lists all registered model types and their current production versions.

**Authentication:** Bearer token required.  
**Role Required:** `admin`.

#### Example Response `200 OK`

```json
{
  "models": [
    {
      "model_type": "crop",
      "current_version": "v1.0",
      "promoted_at": "2026-01-15T09:00:00Z",
      "run_id": "run-2026-01-14-001",
      "architecture": "EfficientNet-B0"
    },
    {
      "model_type": "disease",
      "current_version": "v2.1",
      "promoted_at": "2026-09-22T16:00:00Z",
      "run_id": "run-2026-09-20-001",
      "architecture": "DiseaseNet-v2"
    }
  ]
}
```

---

## 18. Health Endpoint

### 18.1 System Health Check

```
GET /health
```

Returns the health status of all system components. Can be used for uptime monitoring and readiness probes.

**Authentication:** None required.

#### Example Response `200 OK`

```json
{
  "status": "healthy",
  "timestamp": "2026-09-22T16:07:55Z",
  "components": {
    "database": "healthy",
    "redis": "healthy",
    "worker": "healthy",
    "storage": "healthy"
  }
}
```

#### Degraded Response `503 Service Unavailable`

```json
{
  "status": "degraded",
  "timestamp": "2026-09-22T16:07:55Z",
  "components": {
    "database": "healthy",
    "redis": "unhealthy",
    "worker": "unhealthy",
    "storage": "healthy"
  }
}
```

---

## 19. WebSocket Protocol

### 19.1 Real-time Prediction Progress

```
WebSocket /ws/predictions/{prediction_id}
```

Streams real-time pipeline progress events for a prediction. Connect immediately after `POST /predict` to receive live stage updates.

**Authentication:** Pass the access token as a query parameter:

```
ws://localhost:8000/ws/predictions/42?token=<access_token>
```

#### Connection Flow

```
Client                              Server
  |                                   |
  |--- WS Connect (token in query) -->|
  |<-- Connected (handshake) ---------|
  |<-- Event: preprocessing started--|
  |<-- Event: preprocessing done ----|
  |<-- Event: crop_identification ----|
  |<-- Event: disease_identification--|
  |<-- Event: severity_analysis ------|
  |<-- Event: recommendation ---------|
  |<-- Event: pipeline completed -----|
  |--- WS Close ----------------------|
```

#### Event Message Schema

```json
{
  "stage": "disease_identification",
  "status": "completed",
  "message": "Disease identified as Early Blight",
  "duration_ms": 1240,
  "data": {
    "crop": {
      "label": "Tomato",
      "confidence": 0.97
    },
    "disease": {
      "label": "Early Blight",
      "confidence": 0.89
    },
    "pests": [],
    "severity": {
      "percent": 34.2,
      "bucket": "Moderate"
    }
  }
}
```

#### Pipeline Stages

| `stage` | Description |
|---|---|
| `preprocessing` | Image validation, resize, normalization |
| `crop_identification` | Crop species classification |
| `disease_identification` | Disease label inference |
| `severity_analysis` | Segmentation-based severity estimation |
| `pest_detection` | Secondary pest presence detection |
| `recommendation` | LLM-generated treatment recommendation |

#### Stage Statuses

| `status` | Meaning |
|---|---|
| `pending` | Stage has not started |
| `processing` | Stage is actively running |
| `completed` | Stage finished successfully |
| `failed` | Stage encountered an error |
| `skipped` | Stage was bypassed (e.g., no pest detected) |

---

## 20. Data Models

### `AuthResponse`

```json
{
  "tokens": {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "user": {
    "id": "uuid",
    "name": "string",
    "phone": "string | null",
    "email": "string | null",
    "role": "farmer | expert | admin",
    "language": "string | null",
    "location": "string | null",
    "farm_name": "string | null"
  }
}
```

---

### `PredictionResponse` (completed)

```json
{
  "prediction_id": "integer",
  "plot_id": "integer | null",
  "created_at": "ISO 8601 datetime",
  "crop": {
    "label": "string",
    "confidence": "float (0–1)",
    "confidence_rating": "low | medium | high"
  },
  "disease": {
    "label": "string",
    "confidence": "float (0–1)",
    "confidence_rating": "low | medium | high",
    "is_uncertain": "boolean"
  },
  "severity": {
    "percent": "float",
    "bucket": "Healthy | Mild | Moderate | Severe | Critical",
    "affected_area": "float (0–1)"
  },
  "pests": [
    {"label": "string", "confidence": "float"}
  ],
  "weather": {
    "temperature_celsius": "float",
    "humidity_percent": "integer",
    "condition": "string"
  },
  "recommendation": {
    "immediate_action": "string",
    "treatment": "string",
    "prevention": "string",
    "monitoring": "string",
    "provider": "string",
    "is_fallback": "boolean"
  },
  "status": {
    "pipeline": "processing | completed | failed",
    "preprocessing": "pending | processing | completed | failed",
    "crop_identification": "pending | processing | completed | failed",
    "disease_identification": "pending | processing | completed | failed",
    "severity_analysis": "pending | processing | completed | failed",
    "pest_detection": "pending | processing | completed | failed",
    "recommendation": "pending | processing | completed | failed"
  },
  "provenance": {
    "schema_version": "string",
    "pipeline_duration_ms": "integer",
    "models": {
      "crop": {"name": "string", "version": "string"},
      "disease": {"name": "string", "version": "string"}
    }
  },
  "historical_images": "array | null",
  "expert_review_data": "ExpertReviewData | null",
  "follow_up": "PredictionSummary | null"
}
```

---

### `ExpertReviewData`

```json
{
  "review_id": "integer",
  "status": "pending | verified",
  "action": "Approve | Override / Correct Findings | Request Rescan",
  "corrected_disease": "string | null",
  "corrected_severity": "string | null",
  "farmer_guidance": "string | null",
  "reviewed_by": "string (expert name)",
  "reviewed_at": "ISO 8601 datetime"
}
```

---

### `GeoJSON Polygon`

Boundary fields accept a standard GeoJSON Polygon geometry object:

```json
{
  "type": "Polygon",
  "coordinates": [
    [
      [longitude, latitude],
      [longitude, latitude],
      [longitude, latitude],
      [longitude, latitude]
    ]
  ]
}
```

> The first and last coordinate pairs must be identical (closed ring). Coordinates are `[longitude, latitude]` in WGS84.

---

*AI-Powered Smart Farming — Documentation*  
*Last Updated: September 2026*
