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
    // If backend returned 403 (e.g. FIRST_TIME_EMAIL_OTP_REQUIRED or email not verified), re-throw immediately
    if (
      backendErr?.status === 403 ||
      backendErr?.detail?.code === "FIRST_TIME_EMAIL_OTP_REQUIRED" ||
      backendErr?.message?.includes("FIRST_TIME_EMAIL_OTP_REQUIRED") ||
      backendErr?.message?.toLowerCase().includes("not verified")
    ) {
      throw backendErr;
    }
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
  phone?: string;
  password: string;
  location: string;
  language: string;
  crop_history: string[];
}): Promise<AuthResponse> {
  // 1. Primary: Register via backend to ensure verification email is issued
  try {
    const backendRes = await request<AuthResponse>("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (backendRes) {
      if (backendRes.tokens?.access_token) {
        localStorage.setItem("smart_farm_token", backendRes.tokens.access_token);
      }
      return backendRes;
    }
  } catch (backendErr: any) {
    if (backendErr?.status === 409 || backendErr?.message?.toLowerCase().includes("already registered")) {
      throw new Error(backendErr.message || "Phone or email is already registered.");
    }
    console.warn("Backend registration failed, attempting Supabase Auth fallback:", backendErr);
  }

  // 2. Fallback to Supabase Auth registration
  try {
    const { data, error } = await supabase.auth.signUp({
      email: payload.email,
      password: payload.password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/verify-email`,
        data: {
          name: payload.name,
          phone: payload.phone || "",
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
    throw new Error(supaErr?.message || "Registration failed. Please try again.");
  }

  throw new Error("Registration failed. Please try again.");
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
  let supaSuccess = false;
  try {
    const { error } = await supabase.auth.updateUser({ password: newPassword });
    if (!error) {
      supaSuccess = true;
    }
  } catch {}

  if (token && token !== "supabase_recovery") {
    try {
      return await request<{ status: string; message: string }>("/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: newPassword }),
      });
    } catch (backendErr) {
      if (supaSuccess) {
        return {
          status: "success",
          message: "Password has been reset successfully. You can now log in.",
        };
      }
      throw backendErr;
    }
  }

  if (supaSuccess) {
    return {
      status: "success",
      message: "Password has been reset successfully. You can now log in.",
    };
  }

  throw new Error("Failed to reset password. The link may have expired or is invalid.");
}

export async function requestEmailUpdate(
  email: string,
  token?: string
): Promise<{ status: string; message: string }> {
  let activeToken = token;
  if (!activeToken) {
    activeToken = localStorage.getItem("smart_farm_token") || "";
    if (!activeToken) {
      try {
        const { data } = await supabase.auth.getSession();
        activeToken = data.session?.access_token || "";
      } catch {}
    }
  }

  // Also trigger Supabase Auth email change so Supabase dispatches the "Change Email Address" email
  try {
    await supabase.auth.updateUser(
      { email },
      { emailRedirectTo: `${window.location.origin}/auth/verify-email` }
    );
  } catch (err) {
    console.warn("Supabase updateUser email change note:", err);
  }

  return request<{ status: string; message: string }>(
    "/auth/request-email-update",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    },
    activeToken
  );
}

export async function requestPhoneUpdate(
  phone: string,
  token?: string
): Promise<{ status: string; message: string }> {
  let activeToken = token;
  if (!activeToken) {
    activeToken = localStorage.getItem("smart_farm_token") || "";
    if (!activeToken) {
      try {
        const { data } = await supabase.auth.getSession();
        activeToken = data.session?.access_token || "";
      } catch {}
    }
  }

  return request<{ status: string; message: string }>(
    "/auth/request-phone-update",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone }),
    },
    activeToken
  );
}

export async function verifyPhoneUpdate(
  phone: string,
  otpCode: string,
  token?: string
): Promise<Profile> {
  let activeToken = token;
  if (!activeToken) {
    activeToken = localStorage.getItem("smart_farm_token") || "";
    if (!activeToken) {
      try {
        const { data } = await supabase.auth.getSession();
        activeToken = data.session?.access_token || "";
      } catch {}
    }
  }

  // 1. Verify OTP with Supabase Auth in the browser using the browser's PKCE verifier
  const digitsOnly = phone.replace(/\D/g, "");
  const e164Phone = normalizePhoneNumber(phone);
  let storedPhone: string | null = null;
  try {
    storedPhone = sessionStorage.getItem("smart_farm_otp_phone");
  } catch {}

  const candidates: string[] = [];
  if (storedPhone && !candidates.includes(storedPhone)) {
    candidates.push(storedPhone);
  }
  if (!candidates.includes(e164Phone)) {
    candidates.push(e164Phone);
  }
  if (digitsOnly.length === 10 && !candidates.includes(digitsOnly)) {
    candidates.push(digitsOnly);
  }

  let verifyResult: any = null;
  let lastError: any = null;
  let successfulPhone = candidates[0];

  for (const candidate of candidates) {
    try {
      const { data, error } = await supabase.auth.verifyOtp({
        phone: candidate,
        token: otpCode.trim(),
        type: "sms",
      });

      if (!error && (data?.session || data?.user)) {
        verifyResult = data;
        successfulPhone = candidate;
        break;
      }
      lastError = error;
    } catch (err) {
      lastError = err;
    }
  }

  if (!verifyResult) {
    if (lastError) {
      const msg = (lastError.message || "").toLowerCase();
      if (msg.includes("expired")) {
        throw new Error("Verification code has expired. Please request a new code.");
      }
      if (msg.includes("invalid") || msg.includes("incorrect")) {
        throw new Error("Invalid verification code. Please check and try again.");
      }
      throw new Error(lastError.message || "Invalid or expired verification code.");
    }
    throw new Error("Invalid verification code. Please check and try again.");
  }

  const verifiedPhoneToken = verifyResult.session?.access_token || "";

  // 2. Call backend to link phone to user account and sync to Supabase Auth
  try {
    const updatedProfile = await request<Profile>(
      "/auth/verify-phone-update",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: successfulPhone,
          token: otpCode.trim(),
          verified_phone_token: verifiedPhoneToken,
        }),
      },
      activeToken
    );

    // 3. Keep active user session intact on their primary account
    if (activeToken) {
      localStorage.setItem("smart_farm_token", activeToken);
    }
    try {
      sessionStorage.removeItem("smart_farm_otp_phone");
    } catch {}

    return updatedProfile;
  } catch (backendErr) {
    if (activeToken) {
      localStorage.setItem("smart_farm_token", activeToken);
    }
    throw backendErr;
  }
}

export async function verifyEmail(
  tokenStr: string
): Promise<{ status: string; message: string }> {
  return request<{ status: string; message: string }>("/auth/verify-email", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: tokenStr }),
  });
}

export async function resendVerificationEmail(
  email: string
): Promise<{ status: string; message: string }> {
  try {
    return await request<{ status: string; message: string }>("/auth/resend-verification-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
  } catch (err: any) {
    // Fallback directly to Supabase Auth resend
    const { error } = await supabase.auth.resend({
      type: "signup",
      email,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/verify-email`,
      },
    });
    if (error) {
      // Also try email_change type if signup doesn't apply
      const secondTry = await supabase.auth.resend({
        type: "email_change",
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/verify-email`,
        },
      });
      if (secondTry.error) throw new Error(secondTry.error.message || error.message);
    }
    return {
      status: "success",
      message: "A new confirmation email has been dispatched. Please check your inbox.",
    };
  }
}

export async function verifyEmailOtp(
  email: string,
  token: string
): Promise<{ status: string; message: string }> {
  const cleanEmail = email.trim().toLowerCase();
  const cleanToken = token.trim();

  // 1. Try signup OTP
  let res = await supabase.auth.verifyOtp({
    email: cleanEmail,
    token: cleanToken,
    type: "signup",
  });

  if (res.error) {
    // 2. Try email / email_change OTP
    res = await supabase.auth.verifyOtp({
      email: cleanEmail,
      token: cleanToken,
      type: "email",
    });
  }

  if (res.error) {
    throw new Error(res.error.message || "Invalid or expired OTP code.");
  }

  return {
    status: "success",
    message: "Email verified successfully! You are now logged in.",
  };
}

export async function setupFirstTimePassword(payload: {
  email: string;
  phone: string;
  new_password: string;
}): Promise<AuthResponse> {
  const backendRes = await request<AuthResponse>("/auth/setup-first-time-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (backendRes?.tokens?.access_token) {
    localStorage.setItem("smart_farm_token", backendRes.tokens.access_token);
    if (backendRes.tokens.refresh_token) {
      try {
        await supabase.auth.setSession({
          access_token: backendRes.tokens.access_token,
          refresh_token: backendRes.tokens.refresh_token as string,
        });
      } catch (sessErr) {
        console.warn("Could not set Supabase session from backend tokens:", sessErr);
      }
    }
  }
  return backendRes;
}

export async function sendPhoneOtp(
  phone: string,
  _isSignUp: boolean = true,
  metadata?: {
    name?: string;
    language?: string;
    location?: string;
    crop_history?: string[];
  }
): Promise<{ success: boolean; message: string; phoneUsed: string }> {
  const digitsOnly = phone.replace(/\D/g, "");
  const e164Phone = normalizePhoneNumber(phone);

  // Build candidate phone formats.
  // If the user configured "9999999999" in Supabase test numbers without country code,
  // we must test "9999999999" as well as "+919999999999" to guarantee matching.
  const candidates: string[] = [];
  if (digitsOnly === "9999999999") {
    candidates.push("9999999999", "+919999999999");
  } else if (phone.trim().startsWith("+")) {
    candidates.push(phone.trim().replace(/[\s\-]/g, ""));
  } else {
    candidates.push(e164Phone);
    if (digitsOnly.length === 10) {
      candidates.push(digitsOnly);
    }
  }

  let lastError: any = null;

  for (const candidate of candidates) {
    try {
      const { error } = await supabase.auth.signInWithOtp({
        phone: candidate,
        options: {
          // Always set shouldCreateUser to true so Supabase does not throw 422 for test or new numbers
          shouldCreateUser: true,
          data: {
            name: metadata?.name || "Farmer",
            language: metadata?.language || "English",
            location: metadata?.location || "Gujarat, India",
            crop_history: metadata?.crop_history || [],
            role: "farmer",
          },
        },
      });

      if (!error) {
        try {
          sessionStorage.setItem("smart_farm_otp_phone", candidate);
        } catch {}
        return { success: true, message: "Verification code sent successfully.", phoneUsed: candidate };
      }
      lastError = error;
    } catch (err) {
      lastError = err;
    }
  }

  if (lastError) {
    const msg = (lastError.message || "").toLowerCase();
    if (msg.includes("rate limit") || lastError.status === 429) {
      throw new Error("Too many OTP requests. Please wait a minute before requesting another code.");
    }
    throw new Error(lastError.message || "Failed to send verification code. Please check your phone number.");
  }

  return { success: true, message: "Verification code sent successfully.", phoneUsed: candidates[0] };
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
  const digitsOnly = phone.replace(/\D/g, "");
  const e164Phone = normalizePhoneNumber(phone);
  let storedPhone: string | null = null;
  try {
    storedPhone = sessionStorage.getItem("smart_farm_otp_phone");
  } catch {}

  const candidates: string[] = [];
  if (storedPhone && !candidates.includes(storedPhone)) {
    candidates.push(storedPhone);
  }
  if (digitsOnly === "9999999999") {
    if (!candidates.includes("9999999999")) candidates.push("9999999999");
    if (!candidates.includes("+919999999999")) candidates.push("+919999999999");
  } else {
    if (!candidates.includes(e164Phone)) candidates.push(e164Phone);
    if (digitsOnly.length === 10 && !candidates.includes(digitsOnly)) candidates.push(digitsOnly);
  }

  if (!token || token.trim().length < 6) {
    throw new Error("Please enter the complete 6-digit verification code.");
  }

  let verifyResult: any = null;
  let lastError: any = null;
  let successfulPhone = candidates[0];

  for (const candidate of candidates) {
    try {
      const { data, error } = await supabase.auth.verifyOtp({
        phone: candidate,
        token: token.trim(),
        type: "sms",
      });

      if (!error && data?.session?.access_token) {
        verifyResult = data;
        successfulPhone = candidate;
        break;
      }
      lastError = error;
    } catch (err) {
      lastError = err;
    }
  }

  if (!verifyResult?.session?.access_token || !verifyResult?.user) {
    if (lastError) {
      const msg = (lastError.message || "").toLowerCase();
      if (msg.includes("token has expired") || msg.includes("expired")) {
        throw new Error("Verification code has expired. Please request a new code.");
      }
      if (msg.includes("invalid") || msg.includes("incorrect")) {
        throw new Error("Invalid verification code. Please check and try again.");
      }
      throw new Error(lastError.message || "Verification failed. Please check the OTP code.");
    }
    throw new Error("Verification failed. Please check the OTP code.");
  }

  const accessToken = verifyResult.session.access_token;
  localStorage.setItem("smart_farm_token", accessToken);
  try {
    sessionStorage.removeItem("smart_farm_otp_phone");
  } catch {}

  // Initialize base profile from Supabase user metadata
  let userProfile: Profile = profileFromSupabaseUser(verifyResult.user);
  if (registrationData?.name) userProfile.name = registrationData.name;
  if (registrationData?.language) userProfile.language = registrationData.language;
  if (registrationData?.location) userProfile.location = registrationData.location;

  // Synchronize session with backend database
  try {
    const backendRes = await syncSession(accessToken, {
      name: registrationData?.name || userProfile.name,
      phone: successfulPhone,
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
      refresh_token: verifyResult.session.refresh_token,
      token_type: "bearer",
      expires_in: verifyResult.session.expires_in,
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
