# Software Requirements Specification (SRS)
## AI-Powered Smart Farming Platform

**Degree:** Bachelor of Technology (B.Tech) in Information Technology  
**Department:** Department of Information Technology  
**Institute:** Chandubhai S. Patel Institute of Technology (CSPIT)  
**University:** Charotar University of Science and Technology (CHARUSAT), Changa, Gujarat, India  
**Academic Year:** 2026 – 2027  

**Student Contributors:**  
- **Manthan Kuvadiya** (Full-Stack Engineering & MLOps Pipeline)  
- **Kunj Lunagariya** (Computer Vision, Deep Learning & Backend Services)  

**Project Guide:**  
- **Prof. Rajnik Katariya**, Assistant Professor, IT Department, CSPIT, CHARUSAT  

**Document Version:** 1.0 (Final Academic Baseline)  
**Standard:** Conforming to IEEE Std 830-1998 / ISO/IEC/IEEE 29148  

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 [Purpose](#11-purpose)
   - 1.2 [Document Conventions](#12-document-conventions)
   - 1.3 [Project Scope](#13-project-scope)
   - 1.4 [References](#14-references)
2. [Overall Description](#2-overall-description)
   - 2.1 [Product Perspective](#21-product-perspective)
   - 2.2 [User Classes and Characteristics](#22-user-classes-and-characteristics)
   - 2.3 [Operating Environment](#23-operating-environment)
   - 2.4 [Design and Implementation Constraints](#24-design-and-implementation-constraints)
   - 2.5 [Assumptions and Dependencies](#25-assumptions-and-dependencies)
3. [System Features & Functional Requirements](#3-system-features--functional-requirements)
   - 3.1 [FR-1: Leaf Image Acquisition & Quality Pre-Check](#31-fr-1-leaf-image-acquisition--quality-pre-check)
   - 3.2 [FR-2: 7-Stage Deep Learning Diagnostic Inference](#32-fr-2-7-stage-deep-learning-diagnostic-inference)
   - 3.3 [FR-3: ICAR/KVK Agronomic Advisory Generation](#33-fr-3-icarkvk-agronomic-advisory-generation)
   - 3.4 [FR-4: Trilingual Localization (EN, HI, GU)](#34-fr-4-trilingual-localization-en-hi-gu)
   - 3.5 [FR-5: Regional Voice Synthesis (Text-to-Speech)](#35-fr-5-regional-voice-synthesis-text-to-speech)
   - 3.6 [FR-6: Microclimate Weather Risk Alert Engine](#36-fr-6-microclimate-weather-risk-alert-engine)
   - 3.7 [FR-7: Expert-in-the-Loop Review & Concurrency Control](#37-fr-7-expert-in-the-loop-review--concurrency-control)
   - 3.8 [FR-8: Farm & GeoJSON Plot Boundary Management](#38-fr-8-farm--geojson-plot-boundary-management)
   - 3.9 [FR-9: Authentication, Authorization & Security](#39-fr-9-authentication-authorization--security)
   - 3.10 [FR-10: Closed-Loop MLOps & Model Retraining](#310-fr-10-closed-loop-mlops--model-retraining)
4. [External Interface Requirements](#4-external-interface-requirements)
   - 4.1 [User Interfaces](#41-user-interfaces)
   - 4.2 [Hardware Interfaces](#42-hardware-interfaces)
   - 4.3 [Software Interfaces](#43-software-interfaces)
   - 4.4 [Communications Interfaces](#44-communications-interfaces)
5. [Non-Functional Requirements](#5-non-functional-requirements)
   - 5.1 [Performance Requirements](#51-performance-requirements)
   - 5.2 [Safety & Statutory Agronomic Requirements](#52-safety--statutory-agronomic-requirements)
   - 5.3 [Security Requirements](#53-security-requirements)
   - 5.4 [Software Quality Attributes](#54-software-quality-attributes)

---

## 1. Introduction

### 1.1 Purpose
The purpose of this Software Requirements Specification (SRS) is to provide a complete, rigorous, and verifiable definition of the **AI-Powered Smart Farming Platform**. It specifies both functional and non-functional requirements for the FastAPI backend, the React.js web portal, the Flutter mobile app, the Hugging Face AI microservice, and the automated MLOps continuous learning lifecycle. This document serves as the formal contractual baseline for academic evaluation and production deployment.

### 1.2 Document Conventions
- **MUST / SHALL**: Mandatory requirement.
- **SHOULD**: High-priority recommendation.
- **MAY**: Optional capability.
- **FR**: Functional Requirement identifier.
- **NFR**: Non-Functional Requirement identifier.

### 1.3 Project Scope
Indian smallholder farmers frequently suffer 20% to 40% crop yield destruction due to late or inaccurate identification of foliar pathogens, improper agrochemical dosage, and pesticide overuse. The Smart Farming platform bridges this gap by:
1. Enabling farmers to snap a photo of an unhealthy leaf on a mobile smartphone or web browser.
2. Validating photo quality (blur, lighting, leaf presence) via an OpenCV computer vision pipeline before inference.
3. Automatically identifying the crop species (EfficientNet-B0) and classifying the pathogen across 32 disease categories (dedicated EfficientNet-B2 classifiers for Cotton, Groundnut, Pepper Bell, Potato, and Tomato).
4. Providing infection severity percentages (HSV adaptive mask) and pest detection (Ultralytics YOLOv8-nano).
5. Grounding treatments in certified Indian Council of Agricultural Research (ICAR) and Krishi Vigyan Kendra (KVK) guidance.
6. Localizing all recommendations into Gujarati (`gu`), Hindi (`hi`), and Indian English (`en`) with natural neural audio playback.
7. Providing a human-in-the-loop expert review workflow when confidence is below 70%.

### 1.4 References
1. IEEE Std 830-1998: *Recommended Practice for Software Requirements Specifications*.
2. ICAR Package of Practices for Field and Vegetable Crops.
3. FastAPI Documentation: High performance, easy to learn, fast to code, ready for production.
4. PyTorch / Torchvision Neural Architecture Guidelines.

---

## 2. Overall Description

### 2.1 Product Perspective
Smart Farming is an autonomous, distributed multi-tier system comprised of:
- **Presentation Tier**:
  - React 19 + TypeScript SPA for Farmers, Agricultural Experts, and System Admins.
  - Flutter Mobile App (Android/iOS) optimized for one-handed offline-resilient field operation.
- **Application & API Gateway Tier**:
  - FastAPI (Python 3.12) deployed with Gunicorn and Uvicorn workers on Render.
- **AI / Deep Learning Tier**:
  - Standalone FastAPI/PyTorch microservice on Hugging Face Spaces port `7860`.
- **Persistence & Cloud Data Tier**:
  - Supabase Managed PostgreSQL with Alembic database migrations.
  - Supabase S3-compatible Object Storage for leaf images and audio.
  - Upstash Serverless Redis REST for fast distributed caching.

### 2.2 User Classes and Characteristics

| User Role | Technical Literacy | Key Permissions & Responsibilities |
|---|---|---|
| **Farmer** | Low to Moderate | Capture leaf scans, view diagnoses, listen to audio advisories, configure farm/plot boundaries, manage weather alerts, submit feedback. |
| **Agricultural Expert (Agronomist)** | High (Domain Expert) | Claim escalated uncertain scans, override diagnoses, prescribe specialized chemical treatments, review farmer feedback. |
| **System Administrator** | High (Technical) | Monitor API health and model drift, promote candidate weights in Model Registry, trigger MLOps retraining pipelines, purge storage. |
| **Guest User** | Variable | Allowed 1 free leaf diagnostic scan without mandatory registration. |

### 2.3 Operating Environment
- **Server**: Linux x86_64 (Ubuntu 22.04 LTS / Alpine), Python 3.12.
- **Web Client**: Chrome 115+, Firefox 115+, Safari 16+, Edge 115+. Responsive down to 320px viewport.
- **Mobile Client**: Android 8.0+ (API level 26+), iOS 14.0+. Camera hardware with autofocus.

### 2.4 Design and Implementation Constraints
1. **Statutory Agronomic Compliance**: The platform must never recommend unverified synthetic pesticides on uncalibrated models. Disclaimers instructing consultation with local KVK officers are mandatory.
2. **Cold-Start Resilience**: The backend web service must bind port `$PORT` within 1000ms. Database migrations or deep learning weight warming must execute asynchronously in background tasks.
3. **No Secret Ingestion**: All sensitive credentials must remain in environment variables; tracked repository files and commits must pass continuous Gitleaks audits.

---

## 3. System Features & Functional Requirements

### 3.1 FR-1: Leaf Image Acquisition & Quality Pre-Check
- **FR-1.1**: The system shall accept leaf images in JPEG, PNG, and WebP formats up to 10 MB.
- **FR-1.2**: The system shall perform magic-byte content validation (PIL `Image.verify()`) to prevent file disguise attacks.
- **FR-1.3**: The system shall compute a Laplacian variance score; images with variance < 50.0 shall be rejected with `failed_blur` and actionable guidance ("Hold phone steady in bright daylight").
- **FR-1.4**: The system shall compute pixel brightness; images with mean brightness < 40.0 or > 240.0 shall be rejected with `failed_lighting`.

### 3.2 FR-2: 7-Stage Deep Learning Diagnostic Inference
- **FR-2.1**: The system shall classify the crop species using an EfficientNet-B0 network. Supported crops: Cotton, Groundnut, Pepper Bell, Potato, Tomato.
- **FR-2.2**: If crop confidence is ≥ 0.70, the system shall dynamically route the image to the dedicated per-crop EfficientNet-B2 disease classifier.
- **FR-2.3**: The system shall compute lesion surface area percentage using adaptive HSV color-space segmentation.
- **FR-2.4**: The system shall run YOLOv8-nano object detection for visible pest vectors (aphids, mites, whiteflies).
- **FR-2.5**: The system shall attach an immutable `provenance` block recording model checkpoint name, weights SHA-256 hash, and inference execution latency.

### 3.3 FR-3: ICAR/KVK Agronomic Advisory Generation
- **FR-3.1**: The system shall generate a structured 4-point advisory: Immediate Action, Chemical/Biological Treatment, Prevention, and Foliage Monitoring.
- **FR-3.2**: Recommended chemical formulations must include standard dosages (e.g., Mancozeb @ 2.5 g/L) and safety withholding intervals before harvest.

### 3.4 FR-4: Trilingual Localization (EN, HI, GU)
- **FR-4.1**: All farmer-facing UI strings on web and mobile must be localized into English, Hindi, and Gujarati with zero untranslated English literals in UI components.
- **FR-4.2**: Agronomic treatment texts must be translated through verified domain lexicons and IndicTrans2 neural translation with Google Translate zero-hang fallback.

### 3.5 FR-5: Regional Voice Synthesis (Text-to-Speech)
- **FR-5.1**: The system shall generate natural regional audio narration in Hindi (`hi-IN-SwaraNeural`), Gujarati (`gu-IN-DhwaniNeural`), and Indian English (`en-IN-NeerjaNeural`).
- **FR-5.2**: Numbers and dosages must be expanded into spoken regional words prior to speech synthesis (e.g., "2.5 g/L" → "બે પોઇન્ટ પાંચ ગ્રામ પ્રતિ લિટર").

### 3.6 FR-6: Microclimate Weather Risk Alert Engine
- **FR-6.1**: The system shall fetch 5-day / 3-hour forecasts from OpenWeatherMap for all farm plot coordinates.
- **FR-6.2**: High humidity (>75%) + warm temperature (20–30°C) shall trigger an automatic Early Blight risk alert.
- **FR-6.3**: Sustained temperatures > 38°C shall trigger an Extreme Heat Stress alert.
- **FR-6.4**: Forecast precipitation > 20mm within 24 hours shall trigger a Heavy Rain / Waterlogging alert.

### 3.7 FR-7: Expert-in-the-Loop Review & Concurrency Control
- **FR-7.1**: Any prediction with crop or disease confidence < 0.70 shall automatically be placed in the expert review queue.
- **FR-7.2**: An expert can claim a pending review, establishing an atomic 15-minute lease lock to prevent conflicting concurrent submissions.
- **FR-7.3**: Experts can confirm AI findings, correct disease labels, adjust severity scores, and prescribe personalized farmer guidance.

### 3.8 FR-8: Farm & GeoJSON Plot Boundary Management
- **FR-8.1**: Farmers can draw, edit vertices, and rename closed Polygon field boundaries on interactive Leaflet GIS maps (OpenStreetMap and Satellite layers) with draggable vertex markers and edge insertion.
- **FR-8.2**: The system shall validate coordinates, calculate geodesic area in acres, reject self-intersecting polygons, and ensure child plots are fully contained inside the parent farm boundary.

### 3.9 FR-9: Authentication, Authorization & Security
- **FR-9.1**: Passwords must be hashed using Argon2id (`pwdlib`).
- **FR-9.2**: Authentication must issue short-lived JWT access tokens (30 minutes) and secure database-tracked refresh tokens (30 days).
- **FR-9.3**: Role-Based Access Control (RBAC) must restrict `/admin/*` routes to Administrators and `/expert/*` routes to verified Agronomists.
- **FR-9.4**: All API endpoints must enforce strict CORS origin validation, security headers (`nosniff`, `DENY`), and Slowapi rate limiting.

### 3.10 FR-10: Closed-Loop MLOps & Model Retraining
- **FR-10.1**: Verified expert corrections and farmer feedback shall be staged as `dataset_candidates`.
- **FR-10.2**: Administrators can inspect candidate summaries, trigger dataset exports (filtering by crop and verification status) with train/validation/test splits, spatial deterministic splitting by `plot_id`, replay buffer mixing, and review export history.
- **FR-10.3**: Model registry shall track active candidate checkpoints, allowing 1-click promotion and instant rollback.

---

## 4. External Interface Requirements

### 4.1 User Interfaces
- **Web Application**: Accessible, high-contrast agricultural design system built with Tailwind CSS, supporting dark/light theme toggle, custom SVG icons, and responsive layouts.
- **Mobile Application**: Flutter mobile application with phone-number authentication, 1-tap guest diagnosis mode, camera viewfinder overlay, and trilingual language selection.

### 4.2 Software Interfaces
- **PostgreSQL 15+**: Relational data store accessed via SQLAlchemy 2.0 ORM.
- **Alembic**: Database schema migration manager.
- **OpenWeatherMap API**: REST client for atmospheric weather metrics.
- **Hugging Face Inference API**: REST communication with PyTorch vision microservice.

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements
- **NFR-1.1**: Cached prediction responses from Upstash Redis REST shall return in under 50 milliseconds.
- **NFR-1.2**: End-to-end fresh leaf diagnosis (upload, quality gate, 7-stage vision inference, ICAR advisory) shall complete in under 3.5 seconds on CPU.
- **NFR-1.3**: Text-to-Speech synthesis shall complete in under 2.0 seconds for standard advisories.

### 5.2 Security Requirements
- **NFR-2.1**: Interactive documentation endpoints (`/docs`, `/redoc`, `/openapi.json`) shall be disabled in production mode.
- **NFR-2.2**: All image media served in production must be accessed via time-bounded signed URLs (15-minute expiration). Unauthenticated public `/data` paths must return 404 in production.
- **NFR-2.3**: Every HTTP response must return an `X-Request-ID` header for distributed tracing and audit logging.

### 5.3 Reliability & Availability
- **NFR-3.1**: The API server shall achieve 99.5% uptime during daytime agricultural operational hours.
- **NFR-3.2**: Database connection pools shall implement `pool_pre_ping=True` and connection recycling to withstand dropped cloud sockets.

