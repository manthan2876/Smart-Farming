# Smart Farming Cloudflare Worker API Gateway

This directory contains the Cloudflare Worker gateway for the Smart Farming project. It acts as a stable, permanent reverse proxy forwarding requests to the three AI microservices hosted on Google Colab (Vision, IndicTrans2 Translation, and Qwen Advisory) via Cloudflare Quick Tunnels (`trycloudflare.com`).

---

## 🚀 Deployment Options

### Option 1: Via Cloudflare Web Dashboard (Quickest & Free)

1. Log into your [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Navigate to **Workers & Pages** -> **Create application** -> **Create Worker**.
3. Name your worker: `smart-farming-gateway` and click **Deploy**.
4. Click **Edit code** and paste the entire contents of [`worker.js`](worker.js). Click **Deploy**.
5. Go to Worker **Settings** -> **Variables and Secrets**:
   - Under **Secrets**, add `GATEWAY_API_KEY` (e.g. `smart-farming-cf-gateway-secret-2026`).
   - **For Zero-Touch Auto-Sync (Recommended)**: Leave `VISION_URL`, `TRANSLATION_URL`, and `ADVISORY_URL` empty! The Colab notebook will automatically create and update them as Secrets. *(Note: Do NOT add them as plain Environment Variables, otherwise Cloudflare returns error 10053 "Binding name already in use".)*
   - **For Manual Updates**: Under **Environment Variables**, add `VISION_URL`, `TRANSLATION_URL`, and `ADVISORY_URL`.

### Option 2: Via Wrangler CLI

```bash
# Navigate to this folder
cd cloudflare_gateway

# Login to Cloudflare
npx wrangler login

# Set secret key
npx wrangler secret put GATEWAY_API_KEY

# Deploy worker
npx wrangler deploy
```

---

## 📡 Gateway Routing Table

| Route | Upstream Service | Upstream Port on Colab | Sample Forwarded Request |
| :--- | :--- | :--- | :--- |
| `/vision/*` | `VISION_URL` | `8001` | `/vision/predict` -> `8001/predict` |
| `/translation/*` | `TRANSLATION_URL` | `8002` | `/translation/translate` -> `8002/translate` |
| `/advisory/*` | `ADVISORY_URL` | `8003` | `/advisory/advise` -> `8003/advise` |
| `/gateway/status` | Diagnostic (Built-in) | Edge | Check gateway & bound variables |

---

## 🧪 Testing the Gateway

```bash
# 1. Gateway Status (No auth required)
curl https://smart-farming-gateway.<YOUR-SUBDOMAIN>.workers.dev/gateway/status

# 2. Vision Health Check (Requires Bearer token)
curl -H "Authorization: Bearer <GATEWAY_API_KEY>" \
  https://smart-farming-gateway.<YOUR-SUBDOMAIN>.workers.dev/vision/health

# 3. Translation Health Check
curl -H "Authorization: Bearer <GATEWAY_API_KEY>" \
  https://smart-farming-gateway.<YOUR-SUBDOMAIN>.workers.dev/translation/health

# 4. Advisory Health Check
curl -H "Authorization: Bearer <GATEWAY_API_KEY>" \
  https://smart-farming-gateway.<YOUR-SUBDOMAIN>.workers.dev/advisory/health
```

