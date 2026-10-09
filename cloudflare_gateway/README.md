# Smart Farming Cloudflare Worker Gateway

This Worker provides a stable public URL for the Smart Farming AI services hosted in Google Colab. Colab Quick Tunnel URLs can change whenever a runtime restarts; the notebooks should write the latest URLs to Cloudflare KV.

## How routing works

| Public path | KV key | Colab service |
|---|---|---|
| `/vision/*` | `VISION_URL` | Vision API (port 8001) |
| `/translation/*` | `TRANSLATION_URL` | IndicTrans2 API (port 8002) |
| `/advisory/*` | `ADVISORY_URL` | Advisory API (port 8003) |
| `/tts/*` | `TTS_URL` | AI4Bharat Indic-TTS API (port 8004) |
| `/gateway/status` | — | Public configuration status |

The Worker strips the service prefix before forwarding. For example, `/vision/predict` is forwarded to the path `/predict` on the current `VISION_URL`.

## Deploy with Wrangler

Requirements: Node.js and a Cloudflare account with Workers access.

1. Open a terminal in this directory.
2. Log in:

   ```bash
   npx wrangler login
   ```

3. Create the KV namespace:

   ```bash
   npx wrangler kv namespace create UPSTREAMS
   ```

4. Copy the returned namespace ID into `wrangler.toml`, replacing `REPLACE_WITH_YOUR_KV_NAMESPACE_ID`.
5. Set the gateway key as a Worker Secret:

   ```bash
   npx wrangler secret put GATEWAY_API_KEY
   ```

   Enter a long, random value. Do not use the example value from old documentation.

6. Deploy:

   ```bash
   npx wrangler deploy
   ```

## Configure the Colab notebooks

Add these values in Colab's Secrets panel:

- `CF_API_TOKEN`: Cloudflare API token with permission to edit Workers KV values for the relevant account/namespace.
- `CF_ACCOUNT_ID`: your Cloudflare account ID.
- `CF_KV_NAMESPACE_ID`: the same namespace ID configured in `wrangler.toml`.
- `CF_WORKER_BASE_URL`: deployed Worker base URL, e.g. `https://smart-farming-gateway.<your-subdomain>.workers.dev` (no trailing slash).
- `GATEWAY_API_KEY`: exactly the same value configured as the Worker Secret.
- `HF_TOKEN`: only if the relevant model requires Hugging Face authentication.

The notebooks should update these KV keys when their tunnel starts:

- `VISION_URL`
- `TRANSLATION_URL`
- `ADVISORY_URL`

The API token is used by the notebook only to update KV. Never put `CF_API_TOKEN` in frontend or public repository code.

## Test

Check gateway configuration (no auth required):

```bash
curl https://<your-worker-host>/gateway/status
```

Test a service endpoint (replace the key with your secret):

```bash
curl -H "Authorization: Bearer <GATEWAY_API_KEY>"   https://<your-worker-host>/vision/health
```

Repeat with `/translation/health` and `/advisory/health` if those endpoints exist in your service apps. If an app uses a different health route, test its actual route instead.

A `503` means the relevant KV URL is missing. A `502` usually means the stored URL is invalid or the upstream tunnel/service cannot be reached. A `401` means the gateway key is missing or incorrect.

## Important limitations

- The Worker URL stays stable, but Colab is not a permanent server. If a Colab runtime disconnects, its model service becomes unavailable until restarted.
- The public `/gateway/status` endpoint reports whether URLs are configured; it does not prove that each upstream model is healthy.
- Keep `GATEWAY_API_KEY` private. A client-side app cannot safely keep a shared secret; if requests originate from a public mobile/web client, put authenticated calls behind your own backend rather than embedding the gateway key in the client.
