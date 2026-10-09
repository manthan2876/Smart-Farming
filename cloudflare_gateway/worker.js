/**
 * Smart Farming API Gateway - Cloudflare Worker
 * 
 * Provides a stable endpoint for the Smart Farming backend while Google Colab
 * runs the heavy AI models (Vision, IndicTrans2 Translation, and Qwen Advisory)
 * behind ephemeral Cloudflare Quick Tunnels.
 */

export default {
  async fetch(request, env) {
    const incoming = new URL(request.url);

    // 1. Handle CORS Preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization, ngrok-skip-browser-warning",
          "Access-Control-Max-Age": "86400",
        },
      });
    }

    // 2. Built-in Gateway Diagnostic Status Route (Unprotected for health monitoring)
    if (incoming.pathname === "/gateway/status" || incoming.pathname === "/") {
      return Response.json(
        {
          service: "smart-farming-gateway",
          status: "active",
          routes: {
            vision: env.VISION_URL ? "configured" : "missing",
            translation: env.TRANSLATION_URL ? "configured" : "missing",
            advisory: env.ADVISORY_URL ? "configured" : "missing",
          },
          has_auth_key: Boolean(env.GATEWAY_API_KEY),
          timestamp: new Date().toISOString(),
        },
        {
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
          },
        }
      );
    }

    // 3. Authenticate Gateway Key (Protects upstream Colab compute resources)
    const authHeader = request.headers.get("Authorization");
    if (!env.GATEWAY_API_KEY || authHeader !== `Bearer ${env.GATEWAY_API_KEY}`) {
      return Response.json(
        {
          error: "Unauthorized",
          message: "Invalid or missing Bearer token in Authorization header.",
        },
        {
          status: 401,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
          },
        }
      );
    }

    // 4. Match Route Prefix to Target Upstream Service
    const routes = [
      { prefix: "/vision", origin: env.VISION_URL },
      { prefix: "/translation", origin: env.TRANSLATION_URL },
      { prefix: "/advisory", origin: env.ADVISORY_URL },
    ];

    const route = routes.find(
      (item) =>
        incoming.pathname === item.prefix ||
        incoming.pathname.startsWith(item.prefix + "/")
    );

    if (!route) {
      return Response.json(
        {
          error: "Unknown service route",
          path: incoming.pathname,
          available_routes: ["/vision/*", "/translation/*", "/advisory/*"],
        },
        {
          status: 404,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
          },
        }
      );
    }

    if (!route.origin) {
      return Response.json(
        {
          error: "Service URL not configured",
          message: `The upstream tunnel URL for '${route.prefix}' is not configured in Worker environment variables.`,
        },
        {
          status: 503,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
          },
        }
      );
    }

    // 5. Construct Upstream Target URL preserving suffix and query params
    try {
      const target = new URL(route.origin);
      const suffix = incoming.pathname.slice(route.prefix.length);
      target.pathname = target.pathname.replace(/\/+$/, "") + (suffix || "/");
      target.search = incoming.search;

      // 6. Forward Request to Colab Quick Tunnel
      // Upstream request forwards headers, body stream (including multipart image data), and HTTP method
      const upstreamRequest = new Request(target.toString(), request);
      const upstreamResponse = await fetch(upstreamRequest);

      // 7. Inject CORS Headers into Upstream Response
      const headers = new Headers(upstreamResponse.headers);
      headers.set("Access-Control-Allow-Origin", "*");

      return new Response(upstreamResponse.body, {
        status: upstreamResponse.status,
        statusText: upstreamResponse.statusText,
        headers,
      });
    } catch (err) {
      return Response.json(
        {
          error: "Upstream service unavailable",
          message: "Check that Google Colab is running and its Cloudflare Quick Tunnel URL is current.",
          detail: String(err),
        },
        {
          status: 502,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
          },
        }
      );
    }
  },
};

