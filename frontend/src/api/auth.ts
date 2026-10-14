import { request } from "./client";
import type { Profile } from "./types";
import { supabase } from "../lib/supabase";
import { normalizePhoneNumber, isValidPhoneNumber } from "../lib/phone";

type Tokens = {
  access_token: string;
  refresh_token: string;
  token_type?: string;
  expires_in?: number;
};
export type AuthResponse = { tokens: Tokens; user: Profile };

export function profileFromSupabaseUser(user: any): Profile {
  const meta = user?.user_metadata || {};
  return {
    id: user?.id || "",
    name: meta.name || user?.email?.split("@")[0] || "User",
    email: user?.email || "",
    phone: meta.phone || user?.phone || "",
    language: meta.language || "English",
    role: meta.role || "farmer",
    location: meta.location || "Gujarat, India",
    farm_name: meta.farm_name || `${meta.name || "My"} Farm`,
    crop_history: meta.crop_history || [],
    plots: [],
  };
}

export async function login(
  identifier: string,
  password: string,
): Promise<AuthResponse> {
  const cleanId = identifier.trim();
  const isEmail = cleanId.includes("@");
  const credentials = isEmail
    ? { email: cleanId, password }
    : { phone: cleanId, password };

  // 1. Authenticate via backend: validates credentials, automatically synchronizes
  // user password with Supabase Auth via Admin API (preventing 400 invalid_credentials
  // network console errors for existing users), and returns genuine Supabase session tokens.
  try {
    const backendRes = await request<AuthResponse>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier: cleanId, password }),
    });

    if (backendRes?.tokens?.access_token) {
      localStorage.setItem("smart_farm_token", backendRes.tokens.access_token);
      // Hydrate Supabase client session if Supabase tokens were provided
      if (backendRes.tokens.refresh_token) {
        try {
          await supabase.auth.setSession({
            access_token: backendRes.tokens.access_token,
            refresh_token: backendRes.tokens.refresh_token,
          });
        } catch (sessErr) {
          console.warn("Could not set Supabase session from backend tokens:", sessErr);
        }
      }
      return backendRes;
    }
  } catch (backendErr: any) {
    // If backend explicitly returned 401 (invalid credentials), propagate it directly
    if (backendErr?.status === 401 || backendErr?.message?.toLowerCase().includes("invalid credentials")) {
      throw new Error("Invalid credentials. Please check your email and password.");
    }
    // If backend is offline or unreachable, fall back to direct Supabase Auth
    console.warn("Backend /auth/login unavailable, falling back to direct Supabase Auth:", backendErr);
  }

  // 2. Direct Supabase Auth attempt (fallback if backend is offline or unreachable)
  try {
    const { data, error } = await supabase.auth.signInWithPassword(credentials);
    if (!error && data?.session?.access_token) {
      const accessToken = data.session.access_token;
      localStorage.setItem("smart_farm_token", accessToken);
      let userProfile: Profile = profileFromSupabaseUser(data.user);
      try {
        const backendProfile = await profile(accessToken);
        if (backendProfile) {
          userProfile = { ...userProfile, ...backendProfile };
        }
      } catch (profErr) {
        console.warn("Backend /profile fetch skipped or offline, using Supabase session profile:", profErr);
      }
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
    if (error) {
      throw error;
    }
  } catch (supaErr: any) {
    throw new Error(supaErr?.message || "Invalid credentials. Please check your email and password.");
  }

  throw new Error("Invalid credentials. Please check your email and password.");
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
      let userProfile: Profile = profileFromSupabaseUser(data.user);
      try {
        const backendProfile = await profile(accessToken);
        if (backendProfile) {
          userProfile = { ...userProfile, ...backendProfile };
        }
      } catch (profErr) {
        console.warn("Backend /profile fetch skipped or offline, using Supabase session profile:", profErr);
      }
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

export async function sendPhoneOtp(
  phone: string,
  isSignUp: boolean,
  metadata?: {
    name?: string;
    language?: string;
    location?: string;
    crop_history?: string[];
  }
): Promise<{ success: boolean; message: string }> {
  const cleanPhone = normalizePhoneNumber(phone);
  if (!isValidPhoneNumber(cleanPhone)) {
    throw new Error("Please enter a valid 10-digit mobile number.");
  }

  const { error } = await supabase.auth.signInWithOtp({
    phone: cleanPhone,
    options: {
      shouldCreateUser: isSignUp,
      data: isSignUp
        ? {
            name: metadata?.name || "Farmer",
            language: metadata?.language || "English",
            location: metadata?.location || "Gujarat, India",
            crop_history: metadata?.crop_history || [],
            role: "farmer",
          }
        : undefined,
    },
  });

  if (error) {
    const msg = error.message.toLowerCase();
    if (msg.includes("signups not allowed") || msg.includes("user not found")) {
      throw new Error("This phone number is not registered yet. Please create an account first.");
    }
    if (msg.includes("rate limit") || error.status === 429) {
      throw new Error("Too many OTP requests. Please wait a minute before requesting another code.");
    }
    throw new Error(error.message || "Failed to send verification code. Please check your phone number.");
  }

  return { success: true, message: "Verification code sent successfully." };
}

export async function verifyPhoneOtp(
  phone: string,
  token: string,
  registrationData?: {
    name?: string;
    language?: string;
    location?: string;
    crop_history?: string[];
  }
): Promise<AuthResponse> {
  const cleanPhone = normalizePhoneNumber(phone);
  if (!isValidPhoneNumber(cleanPhone)) {
    throw new Error("Invalid phone number format.");
  }
  if (!token || token.trim().length < 6) {
    throw new Error("Please enter the complete 6-digit verification code.");
  }

  const { data, error } = await supabase.auth.verifyOtp({
    phone: cleanPhone,
    token: token.trim(),
    type: "sms",
  });

  if (error) {
    const msg = error.message.toLowerCase();
    if (msg.includes("token has expired") || msg.includes("expired")) {
      throw new Error("Verification code has expired. Please request a new code.");
    }
    if (msg.includes("invalid") || msg.includes("incorrect")) {
      throw new Error("Invalid verification code. Please check and try again.");
    }
    throw new Error(error.message || "Verification failed. Please check the OTP code.");
  }

  if (!data?.session?.access_token || !data?.user) {
    throw new Error("Verification succeeded but no active session was returned.");
  }

  const accessToken = data.session.access_token;
  localStorage.setItem("smart_farm_token", accessToken);

  // Initialize base profile from Supabase user metadata
  let userProfile: Profile = profileFromSupabaseUser(data.user);
  if (registrationData?.name) userProfile.name = registrationData.name;
  if (registrationData?.language) userProfile.language = registrationData.language;
  if (registrationData?.location) userProfile.location = registrationData.location;

  // Synchronize session with backend database
  try {
    const backendRes = await syncSession(accessToken, {
      name: registrationData?.name || userProfile.name,
      phone: cleanPhone,
      language: registrationData?.language || userProfile.language,
      location: registrationData?.location || userProfile.location,
      crop_history: registrationData?.crop_history || userProfile.crop_history,
    });
    if (backendRes?.user) {
      userProfile = { ...userProfile, ...backendRes.user };
    }
  } catch (syncErr) {
    console.warn("Backend /auth/sync-session skipped or offline, using Supabase session profile:", syncErr);
  }

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

export async function syncSession(
  token: string,
  payload?: {
    name?: string;
    phone?: string;
    language?: string;
    location?: string;
    farm_name?: string;
    crop_history?: string[];
  }
): Promise<AuthResponse> {
  return request<AuthResponse>(
    "/auth/sync-session",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload || {}),
    },
    token
  );
}
