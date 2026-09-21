const host = window.location.hostname || "localhost";
const configuredApiUrl = import.meta.env.VITE_API_URL ?? `http://${host}:8000`;
const API_URL = configuredApiUrl.replace(
  /^(https?:\/\/)(localhost|127\.0\.0\.1)(?=:)/,
  `$1${host}`,
);

export function getApiUrl() {
  return API_URL;
}

export function getAssetUrl(path: string) {
  return `${API_URL}${path.startsWith("/") ? path : `/${path}`}`;
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
      // Refresh failed, let the original 401 fall through
    }
  }

  if (!response.ok)
    throw new Error(
      (await response.json().catch(() => null))?.detail ??
        `Request failed (${response.status})`,
    );
    
  return response.json() as Promise<T>;
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