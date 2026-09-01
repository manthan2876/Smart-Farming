const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export function getApiUrl() {
  return API_URL;
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options.headers);
  
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  // Automatically attach Content-Type if a body is being sent
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  
  if (!response.ok)
    throw new Error(
      (await response.json().catch(() => null))?.detail ??
        `Request failed (${response.status})`,
    );
    
  return response.json() as Promise<T>;
}