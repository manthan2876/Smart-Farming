/**
 * Smart Farming API Gateway
 *
 * Stable Cloudflare Worker gateway for Colab-hosted services.
 * KV namespace binding: UPSTREAMS
 * KV keys: VISION_URL, TRANSLATION_URL, ADVISORY_URL, TTS_URL
 * Secret: GATEWAY_API_KEY
 */

const ROUTES = [
  { prefix: "/vision", key: "VISION_URL" },
  { prefix: "/translation", key: "TRANSLATION_URL" },
  { prefix: "/advisory", key: "ADVISORY_URL" },
  { prefix: "/tts", key: "TTS_URL" },
];

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "86400",
  };
}

function jsonResponse(body, status = 200, extraHeaders = {}) {
  return Response.json(body, {
    status,
    headers: { ...corsHeaders(), ...extraHeaders },
  });
}

async function readUpstream(env, key) {
  if (!env.UPSTREAMS) {
    throw new Error("Worker KV binding 'UPSTREAMS' is missing.");
  }
  return (await env.UPSTREAMS.get(key))?.trim() || null;
}

function validateUpstream(rawUrl) {
  let url;
  try {
    url = new URL(rawUrl);
  } catch {
    throw new Error("Stored upstream URL is not a valid URL.");
  }
  if (url.protocol !== "https:" || !url.hostname) {
    throw new Error("Upstream URL must be a valid HTTPS URL.");
  }
  if (url.username || url.password) {
    throw new Error("Upstream URL must not contain embedded credentials.");
  }
  return url;
}

export default {
  async fetch(request, env) {
    const incoming = new URL(request.url);

    // CORS preflight requests do not need the gateway key.
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    // Public diagnostic endpoint: reports configuration, never reveals URLs or secrets.
    if (incoming.pathname === "/" || incoming.pathname === "/gateway/status") {
      const routes = {};
      for (const route of ROUTES) {
        try {
          routes[route.key.replace("_URL", "").toLowerCase()] =
            (await readUpstream(env, route.key)) ? "configured" : "missing";
        } catch {
          routes[route.key.replace("_URL", "").toLowerCase()] = "kv_binding_missing";
        }
      }

      return jsonResponse({
        service: "smart-farming-gateway",
        status: "active",
        routes,
        has_auth_key: Boolean(env.GATEWAY_API_KEY),
        timestamp: new Date().toISOString(),
      });
    }

    // Protect the Colab services from unauthorized use.
    const authHeader = request.headers.get("Authorization");
    if (!env.GATEWAY_API_KEY || authHeader !== `Bearer ${env.GATEWAY_API_KEY}`) {
      return jsonResponse({
        error: "Unauthorized",
        message: "Provide a valid Bearer token in the Authorization header.",
      }, 401);
    }

    const route = ROUTES.find(
      (item) =>
        incoming.pathname === item.prefix ||
        incoming.pathname.startsWith(item.prefix + "/")
    );

    if (!route) {
      return jsonResponse({
        error: "Unknown service route",
        path: incoming.pathname,
        available_routes: ["/vision/*", "/translation/*", "/advisory/*"],
      }, 404);
    }

    let rawUpstream;
    try {
      rawUpstream = await readUpstream(env, route.key);
    } catch (error) {
      return jsonResponse({
        error: "Gateway configuration error",
        message: String(error),
      }, 500);
    }

    if (!rawUpstream) {
      return jsonResponse({
        error: "Service URL not configured",
        message: `No KV value is set for ${route.key}. Start the corresponding Colab notebook and verify its KV URL sync.`,
      }, 503);
    }

    try {
      const target = validateUpstream(rawUpstream);
      const suffix = incoming.pathname.slice(route.prefix.length);
      const basePath = target.pathname.replace(/\/+$/, "");
      target.pathname = `${basePath}${suffix || "/"}`;
      target.search = incoming.search;

      // Do not forward the gateway credential to the upstream service.
      const forwardedHeaders = new Headers(request.headers);
      forwardedHeaders.delete("Authorization");

      const upstreamRequest = new Request(target.toString(), {
        method: request.method,
        headers: forwardedHeaders,
        body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
        redirect: "follow",
      });

      const upstreamResponse = await fetch(upstreamRequest);
      const responseHeaders = new Headers(upstreamResponse.headers);
      for (const [key, value] of Object.entries(corsHeaders())) {
        responseHeaders.set(key, value);
      }

      return new Response(upstreamResponse.body, {
        status: upstreamResponse.status,
        statusText: upstreamResponse.statusText,
        headers: responseHeaders,
      });
    } catch (error) {
      return jsonResponse({
        error: "Upstream service unavailable",
        message: "Check that the relevant Colab runtime is running and its current tunnel URL has been synced to KV.",
        detail: String(error),
      }, 502);
    }
  },
};
