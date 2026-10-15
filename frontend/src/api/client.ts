import { supabase } from "../lib/supabase";

const host = window.location.hostname || "localhost";
const configuredApiUrl = import.meta.env.VITE_API_URL ?? `http://${host}:8000`;
const API_URL = configuredApiUrl.replace(
  /^(https?:\/\/)(localhost|127\.0\.0\.1)(?=:)/,
  `$1${host}`,
);

export function getApiUrl() {
  return API_URL;
}

export function getAssetUrl(path: string | null | undefined): string {
  if (!path) return "";
  // If the path is a direct Supabase signed or public storage URL, route it through the backend proxy
  // (/data/{path}) to prevent third-party Cloudflare __cf_bm cookie rejection warnings in browsers.
  if (path.includes(".supabase.co/")) {
    const match = path.match(/\/(?:storage\/v1\/)?object\/(?:sign|authenticated|public)\/[^/]+\/(.+?)(?:\?|$)/);
    if (match && match[1]) {
      return `${API_URL}/data/${match[1]}`;
    }
  }
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  // Normalize Windows backslashes to forward slashes and trim leading slashes
  let clean = path.replace(/\\/g, "/").replace(/^\/+/, "");
  // Extract relative storage key if path contains data/ prefix
  const dataIdx = clean.indexOf("data/");
  if (dataIdx !== -1) {
    clean = clean.slice(dataIdx + 5);
  }
  clean = clean.replace(/^\/+/, "");
  return `${API_URL}/data/${clean}`;
}
export function getWebSocketUrl(path: string) {
  const url = new URL(API_URL);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = path.startsWith("/") ? path : `/${path}`;
  return url.toString();
}

// Ensure subsequent requests pick up the latest token if refreshed elsewhere
let refreshPromise: Promise<string | null> | null = null;

export async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const execute = async (currentToken: string | null | undefined) => {
    const headers = new Headers(options.headers);
    if (currentToken) {
      headers.set("Authorization", `Bearer ${currentToken}`);
    }
    const savedLang = localStorage.getItem("smart_farm_lang");
    if (savedLang && !headers.has("Accept-Language")) {
      headers.set("Accept-Language", savedLang);
    }
    if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    return fetch(`${API_URL}${path}`, { credentials: 'include', ...options, headers });
  };

  let response = await execute(token);

  if (response.status === 401 && path !== "/auth/login" && path !== "/auth/refresh") {
    try {
      // Attempt refresh with deduplication
      if (!refreshPromise) {
        refreshPromise = (async () => {
          try {
            const { data } = await supabase.auth.refreshSession();
            if (data?.session?.access_token) {
              return data.session.access_token;
            }
          } catch {}
          try {
            const res = await fetch(`${API_URL}/auth/refresh`, {
              method: "POST",
              credentials: "include",
            });
            if (res.ok) {
              const tokens = await res.json();
              return tokens.access_token;
            }
          } catch {}
          return null;
        })().finally(() => {
          refreshPromise = null;
        });
      }
      
      const newAccessToken = await refreshPromise;
      if (newAccessToken) {
        localStorage.setItem("smart_farm_token", newAccessToken);
        window.dispatchEvent(new CustomEvent("tokenRefreshed", { detail: newAccessToken }));
        response = await execute(newAccessToken);
      }
    } catch (e) {
      // Refresh failed, let the original 401 fall through
    }
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    let errMsg = `Request failed (${response.status})`;
    if (typeof errorBody?.detail === "string") {
      errMsg = errorBody.detail;
    } else if (errorBody?.detail?.message) {
      errMsg = errorBody.detail.message;
    } else if (errorBody?.message) {
      errMsg = errorBody.message;
    }
    const err: any = new Error(errMsg);
    err.status = response.status;
    err.detail = errorBody?.detail;
    err.body = errorBody;
    throw err;
  }
    
  return response.json() as Promise<T>;
}

export async function requestWithMeta<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<{ data: T; totalCount: number; offset: number; limit: number }> {
  const execute = async (currentToken: string | null | undefined) => {
    const headers = new Headers(options.headers);
    if (currentToken) {
      headers.set("Authorization", `Bearer ${currentToken}`);
    }
    const savedLang = localStorage.getItem("smart_farm_lang");
    if (savedLang && !headers.has("Accept-Language")) {
      headers.set("Accept-Language", savedLang);
    }
    if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    return fetch(`${API_URL}${path}`, { credentials: 'include', ...options, headers });
  };

  let response = await execute(token);

  if (response.status === 401 && path !== "/auth/login" && path !== "/auth/refresh") {
    try {
      if (!refreshPromise) {
        refreshPromise = fetch(`${API_URL}/auth/refresh`, {
          method: "POST",
          credentials: "include",
        }).then(async (res) => {
          if (res.ok) {
            const tokens = await res.json();
            return tokens.access_token;
          }
          return null;
        }).catch(() => null)
          .finally(() => {
            refreshPromise = null;
          });
      }
      
      const newAccessToken = await refreshPromise;
      if (newAccessToken) {
        localStorage.setItem("smart_farm_token", newAccessToken);
        window.dispatchEvent(new CustomEvent("tokenRefreshed", { detail: newAccessToken }));
        response = await execute(newAccessToken);
      }
    } catch (e) {
      // Refresh failed
    }
  }

  if (!response.ok)
    throw new Error(
      (await response.json().catch(() => null))?.detail ??
        `Request failed (${response.status})`,
    );

  const totalCount = parseInt(response.headers.get("x-total-count") || "0", 10);
  const offset = parseInt(response.headers.get("x-offset") || "0", 10);
  const limit = parseInt(response.headers.get("x-limit") || "0", 10);
  const data = (await response.json()) as T;
  return { data, totalCount, offset, limit };
}

export async function requestBlob(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<Blob> {
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_URL}${path}`, { credentials: "include", ...options, headers });
  if (!response.ok) {
    throw new Error((await response.json().catch(() => null))?.detail ?? `Request failed (${response.status})`);
  }
  return response.blob();
}