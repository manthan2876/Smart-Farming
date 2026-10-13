import { request } from "./client";
import type { Profile } from "./types";
import { supabase } from "../lib/supabase";

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
  // 1. Attempt Supabase Auth login
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: identifier,
      password,
    });
    if (!error && data?.session?.access_token) {
      const accessToken = data.session.access_token;
      localStorage.setItem("smart_farm_token", accessToken);
      const userProfile = await profile(accessToken);
      return {
        tokens: {
          access_token: accessToken,
          refresh_token: data.session.refresh_token,
          token_type: "bearer",
          expires_in: data.session.expires_in,
        },
        user: userProfile,
      };
    }
  } catch (supaErr) {
    console.warn("Supabase Auth login attempt failed, trying backend fallback:", supaErr);
  }

  // 2. Fallback to backend authentication route
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
  // 1. Attempt Supabase Auth registration
  try {
    const { data, error } = await supabase.auth.signUp({
      email: payload.email,
      password: payload.password,
      options: {
        data: {
          name: payload.name,
          location: payload.location,
          language: payload.language,
          crop_history: payload.crop_history || [],
          role: "farmer",
        },
      },
    });

    if (error) {
      throw error;
    }

    if (data?.session?.access_token) {
      const accessToken = data.session.access_token;
      localStorage.setItem("smart_farm_token", accessToken);
      const userProfile = await profile(accessToken);
      return {
        tokens: {
          access_token: accessToken,
          refresh_token: data.session.refresh_token,
          token_type: "bearer",
          expires_in: data.session.expires_in,
        },
        user: userProfile,
      };
    } else if (data?.user && !data.session) {
      // Email confirmation required by Supabase
      throw new Error("Registration successful! Please check your email inbox to confirm your account.");
    }
  } catch (supaErr: any) {
    if (supaErr?.message && supaErr.message.includes("check your email")) {
      throw supaErr;
    }
    console.warn("Supabase Auth signup failed, trying backend fallback:", supaErr);
  }

  // 2. Fallback to backend registration route
  return request<AuthResponse>("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function profile(token: string, lang?: string) {
  const query = lang ? `?lang=${encodeURIComponent(lang)}` : "";
  return request<Profile>(`/profile${query}`, {}, token);
}

export async function updateProfile(payload: Partial<Profile>, token: string) {
  // Update Supabase user metadata in background if active session exists
  try {
    await supabase.auth.updateUser({ data: payload });
  } catch {}

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

export async function logout(): Promise<{ status: string }> {
  try {
    await supabase.auth.signOut();
  } catch (e) {
    console.error("Supabase signOut error", e);
  }
  try {
    await request<{ status: string }>("/auth/logout", {
      method: "POST",
    });
  } catch {}
  localStorage.removeItem("smart_farm_token");
  return { status: "success" };
}

export async function changePassword(
  oldPassword: string,
  newPassword: string,
  token: string
): Promise<{ status: string; message: string }> {
  try {
    const { error } = await supabase.auth.updateUser({ password: newPassword });
    if (!error) {
      return { status: "success", message: "Password changed successfully." };
    }
  } catch {}

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
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    });
    if (!error) {
      return { status: "success", message: "Password reset link sent to your email." };
    }
  } catch {}

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
  try {
    const { error } = await supabase.auth.updateUser({ password: newPassword });
    if (!error) {
      return {
        status: "success",
        message: "Password has been reset successfully. You can now log in.",
      };
    }
  } catch {}

  return request<{ status: string; message: string }>("/auth/reset-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
  });
}
