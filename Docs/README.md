# Smart Farming — Project Documentation Index

> Comprehensive documentation suite for the **AI-Powered Smart Farming Platform** (Version 1.0.0).

---

## 📚 Documentation Directory

### 1. Architecture, Specifications & APIs
| Document | Description |
|---|---|
| [**Architecture.md**](Architecture.md) | High-level system architecture, decoupled microservice topologies, data flows, and infrastructure models. |
| [**API_Specification.md**](API_Specification.md) | Canonical REST API reference: `/api/v1` routes, schemas, request bodies, query parameters, and responses. |
| [**Config_Reference.md**](Config_Reference.md) | Single source of truth for `config.yaml`, environment variables across all tiers, and runtime hot-reloading. |
| [**Auth_Roles.md**](Auth_Roles.md) | Role-Based Access Control (RBAC), Argon2id hashing, JWT token rotation, and Supabase Auth integration. |
| [**UI_UX_Spec.md**](UI_UX_Spec.md) | Canonical UI/UX specification: Tailwind design system, Leaflet GIS mapping, routing, and Vercel Analytics. |

### 2. Formal Academic Specifications (IEEE Standards)
| Document | Description | Standard Conformance |
|---|---|---|
| [**SRS.md**](SRS.md) | Software Requirements Specification detailing functional and non-functional requirements. | **IEEE Std 830-1998** / ISO/IEC/IEEE 29148 |
| [**Design_Document.md**](Design_Document.md) | System Design Document (SDD) with microservices, schemas, and sequence diagrams. | **IEEE Std 1016-2009** |
| [**Test_Plan.md**](Test_Plan.md) | Verification plan, test execution matrices, and security audits. | **IEEE Std 829-2008** |
| [**User_Manual.md**](User_Manual.md) | User & Operations Manual for Farmers, Agricultural Experts, and System Administrators. | Capstone Operations Standard |
| [**report/README.md**](report/README.md) | Academic IEEE conference paper source (`main.tex`), compiled report (`main.pdf`), and figures. | **IEEEtran LaTeX v1.8b** |
| [**Publication_Scope.md**](Publication_Scope.md) | University publication scope, capstone project governance, and academic attribution. | CHARUSAT Governance Charter |

### 3. Operations, Deployment & Runbooks
| Document | Description |
|---|---|
| [**Deployment_Guide.md**](Deployment_Guide.md) | Production cloud deployment runbook (Render, Hugging Face Spaces, Vercel, Supabase, Upstash). |
| [**Production_Readiness_Audit.md**](Production_Readiness_Audit.md) | Security audit report, zero-alert CodeQL verification, supply chain scans, and hardening log. |
| [**functionality-status.md**](functionality-status.md) | Authoritative implementation status, capability gap analysis, and roadmap tracking. |
| [**Worker_Architecture_Runbook.md**](Worker_Architecture_Runbook.md) | ARQ background worker architecture, Redis broker settings, health monitoring, and scaling. |
| [**Backup_Restore_Runbook.md**](Backup_Restore_Runbook.md) | Database disaster recovery runbook, automated backup scripts, and SHA-256 integrity verification. |
| [**Incident_Runbook.md**](Incident_Runbook.md) | Incident management runbook with SEV classifications, fast diagnosis checklists, and recovery steps. |
| [**Supabase_Email_Templates.md**](Supabase_Email_Templates.md) | Production branded HTML email templates for signup confirmation, password reset, and invites. |

### 4. Machine Learning, Datasets & MLOps
| Document | Description |
|---|---|
| [**Model_Cards.md**](Model_Cards.md) | Detailed specifications, benchmarks, training datasets, and limitations for all 7 loaded models. |
| [**MLOps_Retraining.md**](MLOps_Retraining.md) | Closed-loop retraining architecture, candidate curation, spatial splitting, and model promotion. |
| [**mlops_training_guide.md**](mlops_training_guide.md) | Reproducible model training procedures, hyperparameters, and PyTorch execution guide. |
| [**DATASET.md**](DATASET.md) | Dataset sources, merging methodology, class distributions, and closed/uncontrolled environment categorization. |

### 5. Legal, Privacy & Compliance
| Document | Description | Regulatory Framework |
|---|---|---|
| [**Terms_of_Service.md**](Terms_of_Service.md) | User agreement, advisory disclaimers, fair use, and intellectual property terms. | Indian Contract Act |
| [**Privacy_Policy.md**](Privacy_Policy.md) | Personal data protection policy and farmer data rights. | **DPDP Act, 2023** & **GDPR** |

---

## 🏛️ Project & University Metadata

- **Project Title:** AI-Powered Smart Farming Platform for Foliar Disease Diagnosis & Precision Agronomy
- **Version:** 1.0.0 (Production Release)
- **Date:** 27 October 2026
- **Institution:** Department of Information Technology, Chandubhai S. Patel Institute of Technology (CSPIT)
- **University:** Charotar University of Science and Technology (CHARUSAT), Anand, Gujarat, India
- **Faculty Guide:** Prof. Rajnik Katariya
- **Student Authors:** Manthan Kuvadiya (`23it050@charusat.edu.in`), Kunj Lunagariya (`23it053@charusat.edu.in`)
- **License:** Apache License, Version 2.0 ([`LICENSE`](../LICENSE)) with third-party attributions in [`NOTICE`](../NOTICE).

