import { request } from "./client";
import type { Profile } from "./types";

type Tokens = {
  access_token: string;
  refresh_token: string;
  token_type?: string;
  expires_in?: number;
};
export type AuthResponse = { tokens: Tokens; user: Profile };

export async function login(
  identifier: string,
  password: string,
): Promise<AuthResponse> {
  return request<AuthResponse>("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ identifier, password }),
  });
}
export async function register(payload: {
  name: string;
  email: string;
  password: string;
  location: string;
  language: string;
  crop_history: string[];
}): Promise<AuthResponse> {
  return request<AuthResponse>("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
export async function profile(token: string) {
  return request<Profile>("/profile", {}, token);
}
export async function updateProfile(payload: Partial<Profile>, token: string) {
  return request<Profile>(
    "/profile",
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
    token,
  );
}

export async function logout(): Promise<{status: string}> {
  return request<{status: string}>("/auth/logout", {
    method: "POST",
  });
}

export async function changePassword(
  oldPassword: string,
  newPassword: string,
  token: string
): Promise<{ status: string; message: string }> {
  return request<{ status: string; message: string }>(
    "/auth/change-password",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    },
    token
  );
}

export async function forgotPassword(
  email: string
): Promise<{ status: string; message: string }> {
  return request<{ status: string; message: string }>("/auth/forgot-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
}

export async function resetPassword(
  token: string,
  newPassword: string
): Promise<{ status: string; message: string }> {
  return request<{ status: string; message: string }>("/auth/reset-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
  });
}

