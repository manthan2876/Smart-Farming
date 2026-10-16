---
title: Smart Farming AI Microservices
emoji: 🌾
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.16.0
app_file: app.py
pinned: false
---

# Smart Farming AI Microservices

High-performance unified microservice combining Computer Vision, IndicTrans2 Machine Translation, Agronomic Advisory, and Neural Indian Text-to-Speech (TTS).

## Endpoints

| Service | Endpoint | Method | Description |
| :--- | :--- | :--- | :--- |
| **Diagnostics** | `/health` | `GET` | Health status and loaded model information |
| **Vision** | `/vision/predict` | `POST` | Crop identification, disease classification, and pest detection |
| **Translation** | `/translation/translate` | `POST` | English to Hindi (`hi`) and Gujarati (`gu`) translation |
| **Advisory** | `/advisory/advise` | `POST` | Agronomic diagnosis and treatment recommendation |
| **Speech** | `/tts/synthesize` | `POST` | Studio-quality neural voice synthesis in Gujarati, Hindi, English |

## Architecture & Models
- **Advisory LLM**: 100% In-Memory `Qwen/Qwen2.5-1.5B-Instruct` (no external API keys required; runs locally in 16 GB RAM).
- **Translation**: AI4Bharat `IndicTrans2-dist-200M` (English to Hindi & Gujarati).
- **Vision**: EfficientNet-B0 + 5 Crop Disease Classifiers + YOLO Pest Classifier.
- **Speech**: Microsoft Neural Voices (`gu-IN-DhwaniNeural`, `hi-IN-SwaraNeural`).

## Optional Environment Variables / Space Secrets

- `USE_LOCAL_LLM`: `true` (default). Set to `false` if using Groq cloud API.
- `LOCAL_LLM_MODEL`: `Qwen/Qwen2.5-1.5B-Instruct` (default).
- `GROQ_API_KEY`: *(Optional)* Only if using cloud Groq API instead of local Qwen model.
- `GATEWAY_SECRET`: *(Optional)* Bearer token required for requests coming from Cloudflare Gateway.

