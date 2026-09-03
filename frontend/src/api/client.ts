const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export function getApiUrl() {
  return API_URL;
}

// Ensure subsequent requests pick up the latest token if refreshed elsewhere
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
      // Attempt refresh
      const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        credentials: "include", // Send HttpOnly cookie
      });
      
      if (refreshRes.ok) {
        const tokens = await refreshRes.json();
        const newAccessToken = tokens.access_token;
        localStorage.setItem("smart_farm_token", newAccessToken);
        window.dispatchEvent(new CustomEvent("tokenRefreshed", { detail: newAccessToken }));
        
        // Retry original request
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