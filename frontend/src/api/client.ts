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
  // Keep signed object-storage URLs intact; replacing them with /data would bypass media authorization.
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

function shouldRefreshAfterUnauthorized(path: string): boolean {
  const unversionedPath = path.replace(/^\/api\/v\d+/, "");
  return unversionedPath !== "/auth/login" && unversionedPath !== "/auth/refresh";
}

async function getRefreshedToken(): Promise<string | null> {
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
  return refreshPromise;
}

function prepareHeaders(
  headersInit?: HeadersInit,
  currentToken?: string | null,
  body?: BodyInit | null,
): Headers {
  const headers = new Headers(headersInit);
  if (currentToken) {
    headers.set("Authorization", `Bearer ${currentToken}`);
  }
  const savedLang = localStorage.getItem("smart_farm_lang");
  if (savedLang && !headers.has("Accept-Language")) {
    headers.set("Accept-Language", savedLang);
  }
  if (body && !(body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return headers;
}

export function formatErrorMessage(errorBody: any, status: number): string {
  if (!errorBody) return `Request failed (${status})`;
  if (typeof errorBody === "string") return errorBody;
  if (typeof errorBody.detail === "string") return errorBody.detail;
  if (Array.isArray(errorBody.detail)) {
    return errorBody.detail
      .map((item: any) => {
        if (typeof item === "string") return item;
        const loc = Array.isArray(item.loc)
          ? item.loc.filter((part: any) => part !== "body").join(".")
          : "";
        const msg = item.msg || item.message || (typeof item === "object" ? JSON.stringify(item) : String(item));
        return loc ? `${loc}: ${msg}` : msg;
      })
      .join(", ");
  }
  if (errorBody.detail && typeof errorBody.detail === "object") {
    if (typeof errorBody.detail.message === "string") return errorBody.detail.message;
    try {
      return JSON.stringify(errorBody.detail);
    } catch {
      return `Request failed (${status})`;
    }
  }
  if (typeof errorBody.message === "string") return errorBody.message;
  return `Request failed (${status})`;
}

async function handleResponseError(response: Response): Promise<never> {
  const errorBody = await response.json().catch(() => null);
  const errMsg = formatErrorMessage(errorBody, response.status);
  const err: any = new Error(errMsg);
  err.status = response.status;
  err.detail = errorBody?.detail;
  err.body = errorBody;
  throw err;
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const execute = async (currentToken: string | null | undefined) => {
    const headers = prepareHeaders(options.headers, currentToken, options.body);
    return fetch(`${API_URL}${path}`, { credentials: 'include', ...options, headers });
  };

  let response = await execute(token);

  if (response.status === 401 && shouldRefreshAfterUnauthorized(path)) {
    try {
      const newAccessToken = await getRefreshedToken();
      if (newAccessToken) {
        localStorage.setItem("smart_farm_token", newAccessToken);
        window.dispatchEvent(new CustomEvent("tokenRefreshed", { detail: newAccessToken }));
        response = await execute(newAccessToken);
      }
    } catch {
      // Refresh failed, let the original 401 fall through
    }
  }

  if (!response.ok) {
    await handleResponseError(response);
  }
    
  return response.json() as Promise<T>;
}

export async function requestWithMeta<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<{ data: T; totalCount: number; offset: number; limit: number }> {
  const execute = async (currentToken: string | null | undefined) => {
    const headers = prepareHeaders(options.headers, currentToken, options.body);
    return fetch(`${API_URL}${path}`, { credentials: 'include', ...options, headers });
  };

  let response = await execute(token);

  if (response.status === 401 && shouldRefreshAfterUnauthorized(path)) {
    try {
      const newAccessToken = await getRefreshedToken();
      if (newAccessToken) {
        localStorage.setItem("smart_farm_token", newAccessToken);
        window.dispatchEvent(new CustomEvent("tokenRefreshed", { detail: newAccessToken }));
        response = await execute(newAccessToken);
      }
    } catch {
      // Refresh failed
    }
  }

  if (!response.ok) {
    await handleResponseError(response);
  }

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
  const execute = async (currentToken: string | null | undefined) => {
    const headers = prepareHeaders(options.headers, currentToken, options.body);
    return fetch(`${API_URL}${path}`, { credentials: "include", ...options, headers });
  };

  let response = await execute(token);

  if (response.status === 401 && shouldRefreshAfterUnauthorized(path)) {
    try {
      const newAccessToken = await getRefreshedToken();
      if (newAccessToken) {
        localStorage.setItem("smart_farm_token", newAccessToken);
        window.dispatchEvent(new CustomEvent("tokenRefreshed", { detail: newAccessToken }));
        response = await execute(newAccessToken);
      }
    } catch {
      // Refresh failed
    }
  }

  if (!response.ok) {
    await handleResponseError(response);
  }

  return response.blob();
}