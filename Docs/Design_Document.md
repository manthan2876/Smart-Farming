# System Design Document (SDD)
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
**Standard:** Conforming to IEEE Std 1016-2009 (*Systems and software engineering — Life cycle processes — Requirements definition and analysis*)

---

## 1. Architectural Overview

The **AI-Powered Smart Farming Platform** follows a modern cloud-native, decoupled microservices architecture designed to support high-throughput, low-latency foliar disease diagnostics and agronomic intelligence.

```mermaid
flowchart TB
    subgraph PRESENTATION["Presentation Layer"]
        WEB["React 19 + TypeScript SPA\nVercel Edge Network\nFarmer · Expert · Admin UI"]
        MOB["Flutter Mobile App\nAndroid APK / iOS IPA\nOne-Tap Guest Mode · Offline SQLite"]
    end

    subgraph API_GATEWAY["API Gateway Tier (Render)"]
        GW["FastAPI (Python 3.12)\nGunicorn Process Manager + Uvicorn Workers\nSlowapi Rate Limiting · JWT HS256\nCORS Enforced · Security Headers"]
        ROUTERS["Routers Layer\n/api/v1/predict · /api/v1/farm · /api/v1/expert"]
        SERVICES["Service Layer\nAlertService · FarmService · ExpertService · FeedbackService"]
        CRUD["Repository / CRUD Layer\nSQLAlchemy 2.0 ORM"]
        
        GW --> ROUTERS
        ROUTERS --> SERVICES
        SERVICES --> CRUD
    end

    subgraph AI_TIER["AI Microservice Tier (Hugging Face Space)"]
        HF_API["FastAPI / Gradio App (Port 7860)\nZeroGPU / CPU PyTorch Runtime"]
        CV_STAGE["7-Stage Vision Pipeline\n1. OpenCV Quality Gate\n2. EfficientNet-B0 Crop ID\n3. EfficientNet-B2 Disease ID\n4. HSV Severity Mask\n5. YOLOv8-nano Pest Detection\n6. ICAR Advisory Engine\n7. IndicTrans2 / Edge-TTS"]
        
        HF_API --> CV_STAGE
    end

    subgraph DATA_TIER["Persistence & Cloud Infrastructure"]
        POSTGRES["Supabase PostgreSQL 15+\nSession Connection Pooler\nAlembic Database Migrations"]
        S3_OBJ["Supabase Object Storage\n15-Min Expiring Signed URLs\nLeaf Images · Grad-CAM Heatmaps · Audio"]
        REDIS["Upstash Serverless Redis REST\nImage Dedup (sf:dedup:*)\nTranslation Cache (sf:trans:*)\nWeather Cache (sf:weather:*)"]
        QSTASH["Upstash QStash\nServerless Scheduled Crons"]
    end

    WEB -->|HTTPS REST / OpenAPI| GW
    MOB -->|HTTPS REST| GW
    SERVICES -->|HTTP REST Client| HF_API
    CRUD -->|SQLAlchemy Sessions| POSTGRES
    SERVICES -->|REST API / Signed URLs| S3_OBJ
    SERVICES -->|HTTPS Bearer| REDIS
    QSTASH -->|Webhook POST| GW
```

---

## 2. Sequence Diagrams

### 2.1 Leaf Diagnostic Scan & Inference Flow

```mermaid
sequenceDiagram
    autonumber
    actor Farmer as Farmer (Mobile / Web)
    participant Gateway as FastAPI Backend
    participant Redis as Upstash Redis Cache
    participant Storage as Supabase Object Storage
    participant AIService as AI Vision Microservice
    participant DB as PostgreSQL Database

    Farmer->>Gateway: POST /api/v1/predict (Multipart Image + GPS)
    Gateway->>Gateway: PIL Magic-Byte Validation & 10MB Size Check
    Gateway->>Gateway: Compute SHA-256 Hash of Image Bytes
    Gateway->>Redis: Check Dedup Key (sf:dedup:{hash})
    
    alt Cache Hit (< 20ms)
        Redis-->>Gateway: Cached Completed Prediction JSON
        Gateway-->>Farmer: Return 200 OK (cached=True)
    else Cache Miss
        Gateway->>Storage: Upload Raw Leaf Image (smart-farming-data)
        Storage-->>Gateway: Stored Relative Path / Signed URL
        Gateway->>AIService: POST /vision/predict (Image Bytes + Metadata)
        
        Note over AIService: Stage 1: OpenCV Blur & Lighting Gate<br/>Stage 2: EfficientNet-B0 Crop Classifier<br/>Stage 3: Dedicated EfficientNet-B2 Disease Classifier<br/>Stage 4: Adaptive HSV Lesion Severity %<br/>Stage 5: YOLOv8 Pest Detection
        
        AIService-->>Gateway: Diagnosis Result (Crop, Disease, Conf, Severity)
        Gateway->>Gateway: Generate ICAR/KVK Grounded Treatment Advisory
        Gateway->>DB: Persist Prediction Record & Metadata
        Gateway->>Redis: Set Dedup Cache (sf:dedup:{hash}, 24h TTL)
        
        opt Confidence < 0.70
            Gateway->>DB: Create Pending Expert Review Record
        end
        
        Gateway-->>Farmer: Return 200 OK (Full Diagnostic Payload)
    end
```

### 2.2 Expert Review & Concurrency Lock Lease Flow

```mermaid
sequenceDiagram
    autonumber
    actor Expert as Agronomist (Expert)
    participant Gateway as FastAPI Backend
    participant Service as ExpertService
    participant CRUD as ExpertReview CRUD
    participant DB as PostgreSQL Database
    participant Farmer as Farmer

    Expert->>Gateway: GET /api/v1/expert/queue
    Gateway->>Service: get_queue_items()
    Service->>CRUD: get_pending_reviews()
    CRUD->>DB: SELECT * FROM expert_reviews WHERE status = 'pending'
    DB-->>CRUD: Pending Review List
    CRUD-->>Service: Review Records
    Service-->>Gateway: Formatted Queue Items
    Gateway-->>Expert: 200 OK (Queue List)

    Expert->>Gateway: POST /api/v1/expert/reviews/{id}/claim
    Gateway->>Service: claim_review_lease(review_id, expert_id)
    Service->>DB: Check active lease (< 15 min old)
    alt Claimed by another expert
        Service-->>Gateway: Raise 409 Conflict (Lease Active)
        Gateway-->>Expert: 409 Conflict
    else Available or Expired
        Service->>CRUD: claim_review(expert_id, now)
        CRUD->>DB: UPDATE expert_reviews SET claimed_by = expert_id
        DB-->>CRUD: Success
        Service-->>Gateway: Claim Confirmation
        Gateway-->>Expert: 200 OK (status="claimed", lease=900s)
    end

    Expert->>Gateway: POST /api/v1/expert/reviews/{id} (Action, Guidance, Retrain)
    Gateway->>Service: submit_review_decision(review_id, payload)
    Service->>DB: Update Review, Update Prediction, Insert Alert & DatasetCandidate
    DB-->>Service: Committed
    Service-->>Gateway: Success Result
    Gateway-->>Farmer: Push Notification / Alert ("Expert Verified Scan #101")
    Gateway-->>Expert: 200 OK (status="success")
```

---

## 3. Data Flow Diagrams (DFD)

### 3.1 DFD Level 0 (Context Diagram)

```mermaid
flowchart LR
    FARMER((Farmer))
    EXPERT((Agronomist))
    ADMIN((System Admin))
    WEATHER_API[OpenWeatherMap API]
    
    SYSTEM[AI-Powered Smart Farming Platform]

    FARMER -->|Uploads Leaf Image & GPS| SYSTEM
    SYSTEM -->|Delivers Crop Diagnosis & Voice Advisory| FARMER
    
    EXPERT -->|Reviews Uncertain Diagnoses & Prescribes Guidance| SYSTEM
    SYSTEM -->|Provides Review Queue & High-Res Imagery| EXPERT

    ADMIN -->|Configures Thresholds & Monitors MLOps| SYSTEM
    SYSTEM -->|Exports Datasets & Model Drift Metrics| ADMIN

    WEATHER_API -->|Real-Time Atmospheric Forecasts| SYSTEM
```

### 3.2 DFD Level 1 (Functional Decomposition)

```mermaid
flowchart TD
    FARMER((Farmer)) -->|1. Leaf Photo| P1[1.0 Image Validation & Quality Gate]
    P1 -->|Valid Image| P2[2.0 7-Stage Vision Pipeline]
    P1 -->|Rejected (Blur/Dark)| FARMER
    
    P2 -->|Inference Findings| P3[3.0 Agronomic Advisory Generator]
    P3 -->|English Advisory| P4[4.0 Regional Translation & TTS Engine]
    P4 -->|Audio & Vernacular Text| FARMER
    
    P2 -->|Low Confidence < 0.70| D1[(Expert Reviews Store)]
    EXPERT((Agronomist)) <-->|Review & Correct| D1
    
    P2 -->|Prediction Record| D2[(Predictions Store)]
    D2 --> D3[(Dataset Candidates for MLOps)]
    ADMIN((Administrator)) <-->|Export Dataset & Retrain| D3
```

---

## 4. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ FARMS : owns
    USERS ||--o{ PREDICTIONS : submits
    USERS ||--o{ ALERTS : receives
    USERS ||--o{ FEEDBACK : submits
    USERS ||--o{ REFRESH_TOKENS : maintains
    
    FARMS ||--o{ PLOTS : contains
    PLOTS ||--o{ PREDICTIONS : associates
    
    PREDICTIONS ||--o| IMAGES : stores
    PREDICTIONS ||--o| EXPERT_REVIEWS : escalates
    PREDICTIONS ||--o{ FEEDBACK : receives
    PREDICTIONS ||--o| DATASET_CANDIDATES : contributes
    
    USERS {
        uuid id PK
        string email UK
        string phone UK
        string password_hash
        string name
        string role
        string language
        boolean is_email_verified
        datetime created_at
    }

    FARMS {
        int id PK
        uuid user_id FK
        string name
        string location
        float latitude
        float longitude
        float area_acres
        json boundary
        json crop_history
    }

    PLOTS {
        int id PK
        int farm_id FK
        string name
        string crop
        float area_acres
        string status
        json geometry
    }

    PREDICTIONS {
        int id PK
        uuid user_id FK
        int plot_id FK
        string crop
        string disease
        float crop_conf
        float disease_conf
        float severity_pct
        string status
        json result
        datetime created_at
    }

    EXPERT_REVIEWS {
        int id PK
        int prediction_id FK
        uuid expert_id FK
        string status
        string claimed_by
        datetime claimed_at
        string decision
        string corrected_disease
        text farmer_guidance
        datetime reviewed_at
    }

    FEEDBACK {
        int id PK
        int prediction_id FK
        boolean is_correct
        text farmer_note
        string review_status
        uuid reviewer_id FK
        datetime created_at
    }

    ALERTS {
        int id PK
        uuid user_id FK
        int plot_id FK
        string kind
        string severity
        string title
        text body
        boolean is_read
        datetime created_at
    }

    DATASET_CANDIDATES {
        int id PK
        int prediction_id FK
        string source
        string original_label
        string corrected_label
        string image_path
        string status
        text provenance_note
        datetime created_at
    }
```

---

## 5. Architectural Decision Records (ADRs)

### ADR-01: Adoption of Layered Architecture (Router → Service → Repository)
- **Status**: Accepted
- **Context**: Route handlers previously contained raw SQL queries, file handling, and external API requests, making testing difficult and leading to tight coupling.
- **Decision**: Enforce strict separation: Routers handle HTTP parsing/validation, Service layer owns domain business logic, and CRUD layer manages ORM persistence.
- **Consequence**: Enhances testability, eliminates code duplication, and enables isolated mock testing.

### ADR-02: FastAPI Event Loop Concurrency Model
- **Status**: Accepted
- **Context**: Mixing `async def` with blocking synchronous SQLAlchemy queries caused main thread event loop starvation.
- **Decision**: Declare SQLAlchemy-dependent endpoints as standard `def` functions. FastAPI offloads them automatically to an external worker threadpool (`run_in_threadpool`). CPU-bound ML inference is dispatched via `asyncio.to_thread` or the background ARQ worker.
- **Consequence**: Event loop remains responsive (<5ms latency for non-blocking routes) even during heavy database operations.

### ADR-03: Multi-Tiered Translation Architecture
- **Status**: Accepted
- **Context**: Pure machine translation via neural models (IndicTrans2) occasionally mistranslates critical chemical dosages or suffers cold-start timeouts.
- **Decision**: Deploy a multi-tier pipeline:
  1. Instant offline verified agronomic lexicon (0ms).
  2. Upstash Redis REST cached translations.
  3. IndicTrans2 neural model on Hugging Face Spaces.
  4. Google Translate public fallback endpoint for zero-hang availability.
- **Consequence**: Zero translation downtime while guaranteeing 100% accuracy for statutory ICAR chemical dosage warnings.

