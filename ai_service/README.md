---
title: Smart Farming AI Microservices
emoji: 🌾
colorFrom: green
colorTo: emerald
sdk: docker
app_port: 7860
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

## Environment Variables / Space Secrets

- `GROQ_API_KEY`: *(Optional)* Free Groq API key for ultra-fast (0.4s) advisory generation.
- `GATEWAY_SECRET`: *(Optional)* Bearer token required for requests coming from Cloudflare Gateway.

