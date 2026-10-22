import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { login, profile, register, logout, updateProfile, profileFromSupabaseUser, AuthResponse, sendPhoneOtp, verifyPhoneOtp, requestEmailUpdate as apiRequestEmailUpdate, resendVerificationEmail as apiResendVerificationEmail, setupFirstTimePassword as apiSetupFirstTimePassword, requestPhoneUpdate as apiRequestPhoneUpdate, verifyPhoneUpdate as apiVerifyPhoneUpdate } from "../api/auth";
import { Profile } from "../api/types";
import { Language, Units, t, TranslationKey } from "../i18n";
import { supabase } from "../lib/supabase";
import { normalizePhoneNumber } from "../lib/phone";
import { analytics } from "../lib/analytics";

interface AuthContextType {
  user: Profile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  language: Language;
  units: Units;
  t: (key: TranslationKey) => string;
  setLanguage: (lang: Language) => Promise<void>;
  setUnits: (units: Units) => void;
  signIn: (identifier: string, pass: string) => Promise<Profile>;
  signUp: (payload: { name: string; email?: string; phone?: string; password: string; location: string; language: string; crop_history?: string[] }) => Promise<Profile>;
  sendPhoneOtp: (phone: string, isSignUp: boolean, metadata?: { name?: string; language?: string; location?: string; crop_history?: string[] }) => Promise<{ success: boolean; message: string }>;
  verifyPhoneOtp: (phone: string, token: string, registrationData?: { name?: string; language?: string; location?: string; crop_history?: string[] }) => Promise<Profile>;
  requestEmailUpdate: (email: string) => Promise<{ status: string; message: string }>;
  resendVerificationEmail: (email: string) => Promise<{ status: string; message: string }>;
  requestPhoneUpdate: (phone: string) => Promise<{ status: string; message: string }>;
  verifyPhoneUpdate: (phone: string, otpCode: string) => Promise<Profile>;
  setupFirstTimePassword: (payload: { email: string; phone: string; new_password: string }) => Promise<Profile>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  updateUserProfile: (payload: Partial<Profile>) => Promise<Profile>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const PREF_LANG_KEY = "smart_farm_lang";
const PREF_UNITS_KEY = "smart_farm_units";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Profile | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("smart_farm_token"));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem(PREF_LANG_KEY);
    if (saved === "Gujarati" || saved === "Hindi" || saved === "English") return saved;
    return "English";
  });

  const [units, setUnitsState] = useState<Units>(() => {
    const saved = localStorage.getItem(PREF_UNITS_KEY);
    if (saved === "Imperial" || saved === "Metric") return saved;
    return "Metric";
  });

  const fetchUserProfile = async (authToken: string) => {
    try {
      const savedLang = localStorage.getItem(PREF_LANG_KEY);
      const effectiveLang = (savedLang === "Gujarati" || savedLang === "Hindi" || savedLang === "English") ? (savedLang as Language) : undefined;
      const userData = await profile(authToken, effectiveLang);
      if (userData) {
        setUser(userData);
        if (effectiveLang) {
          setLanguageState(effectiveLang);
        } else if (userData.language && (userData.language === "Gujarati" || userData.language === "Hindi" || userData.language === "English")) {
          setLanguageState(userData.language as Language);
          localStorage.setItem(PREF_LANG_KEY, userData.language);
        }
      }
    } catch {
      // Backend /profile unavailable: fallback to Supabase session metadata without signing out
      try {
        const { data } = await supabase.auth.getUser();
        if (data?.user) {
          const fallbackProfile = profileFromSupabaseUser(data.user);
          setUser((prev) => (prev ? { ...fallbackProfile, ...prev } : fallbackProfile));
          return;
        }
      } catch {}
      signOut();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchUserProfile(token);
    } else {
      setIsLoading(false);
    }

    // 1. Listen for Supabase session changes & automatic background token refreshes
    const { data: authSubscription } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.access_token) {
        if (session.access_token !== token) {
          localStorage.setItem("smart_farm_token", session.access_token);
          setToken(session.access_token);
        }
        if (session.user) {
          const quickProfile = profileFromSupabaseUser(session.user);
          setUser((prev) => (prev ? { ...quickProfile, ...prev } : quickProfile));
        }
        fetchUserProfile(session.access_token);
      } else if (event === "SIGNED_OUT") {
        localStorage.removeItem("smart_farm_token");
        setToken(null);
        setUser(null);
        setIsLoading(false);
      }
    });

    const handleTokenRefresh = (e: Event) => {
      const customEvent = e as CustomEvent<string>;
      setToken(customEvent.detail);
    };

    window.addEventListener("tokenRefreshed", handleTokenRefresh);
    return () => {
      authSubscription?.subscription?.unsubscribe();
      window.removeEventListener("tokenRefreshed", handleTokenRefresh);
    };
  }, [token]);

  const setLanguage = async (newLang: Language) => {
    setLanguageState(newLang);
    localStorage.setItem(PREF_LANG_KEY, newLang);
    analytics.languageChanged(newLang);
    if (token) {
      try {
        await updateProfile({ language: newLang }, token);
        const refreshed = await profile(token, newLang);
        setUser(refreshed);
      } catch (err) {
        console.warn("Failed to persist language to backend profile:", err);
      }
    }
  };

  const setUnits = (newUnits: Units) => {
    setUnitsState(newUnits);
    localStorage.setItem(PREF_UNITS_KEY, newUnits);
  };

  const translate = (key: TranslationKey): string => {
    return t(key, language);
  };

  const signIn = async (identifier: string, pass: string): Promise<Profile> => {
    const res: AuthResponse = await login(identifier, pass);
    const accessToken = res.tokens.access_token;
    localStorage.setItem("smart_farm_token", accessToken);
    setToken(accessToken);
    setUser(res.user);
    analytics.authAction("login");
    if (res.user.language && (res.user.language === "Gujarati" || res.user.language === "Hindi" || res.user.language === "English")) {
      setLanguageState(res.user.language as Language);
      localStorage.setItem(PREF_LANG_KEY, res.user.language);
    }
    return res.user;
  };

  const signUp = async (payload: { name: string; email?: string; phone?: string; password: string; location: string; language: string; crop_history?: string[] }): Promise<Profile> => {
    const res: AuthResponse = await register({
      name: payload.name,
      email: payload.email || "",
      phone: payload.phone ? normalizePhoneNumber(payload.phone) : undefined,
      password: payload.password,
      location: payload.location,
      language: payload.language,
      crop_history: payload.crop_history || [],
    });
    const accessToken = res.tokens.access_token;
    if (accessToken) {
      localStorage.setItem("smart_farm_token", accessToken);
      setToken(accessToken);
      setUser(res.user);
      analytics.authAction("register");
    }
    if (payload.language && (payload.language === "Gujarati" || payload.language === "Hindi" || payload.language === "English")) {
      setLanguageState(payload.language as Language);
      localStorage.setItem(PREF_LANG_KEY, payload.language);
    }
    return res.user;
  };

  const sendPhoneOtpHandler = async (
    phone: string,
    isSignUp: boolean,
    metadata?: { name?: string; language?: string; location?: string; crop_history?: string[] }
  ): Promise<{ success: boolean; message: string }> => {
    return sendPhoneOtp(phone, isSignUp, metadata);
  };

  const verifyPhoneOtpHandler = async (
    phone: string,
    otpCode: string,
    registrationData?: { name?: string; language?: string; location?: string; crop_history?: string[] }
  ): Promise<Profile> => {
    const res: AuthResponse = await verifyPhoneOtp(phone, otpCode, registrationData);
    const accessToken = res.tokens.access_token;
    localStorage.setItem("smart_farm_token", accessToken);
    setToken(accessToken);
    setUser(res.user);
    analytics.authAction(registrationData ? "register" : "login");
    if (res.user.language && (res.user.language === "Gujarati" || res.user.language === "Hindi" || res.user.language === "English")) {
      setLanguageState(res.user.language as Language);
      localStorage.setItem(PREF_LANG_KEY, res.user.language);
    }
    return res.user;
  };

  const signOut = async () => {
    analytics.authAction("logout");
    try {
      await logout();
    } catch (e) {
      console.error("Logout API failed", e);
    }
    localStorage.removeItem("smart_farm_token");
    setToken(null);
    setUser(null);
  };

  const refreshProfile = async () => {
    if (token) {
      await fetchUserProfile(token);
    }
  };

  const updateUserProfile = async (payload: Partial<Profile>): Promise<Profile> => {
    if (!token) throw new Error("Not authenticated");
    const updated = await updateProfile(payload, token);
    setUser(updated);
    return updated;
  };

  const requestEmailUpdateHandler = async (email: string) => {
    if (!token) throw new Error("Not authenticated");
    const res = await apiRequestEmailUpdate(email, token);
    await refreshProfile();
    return res;
  };

  const resendVerificationEmailHandler = async (email: string) => {
    return apiResendVerificationEmail(email);
  };

  const requestPhoneUpdateHandler = async (phone: string) => {
    if (!token) throw new Error("Not authenticated");
    return apiRequestPhoneUpdate(phone, token);
  };

  const verifyPhoneUpdateHandler = async (phone: string, otpCode: string): Promise<Profile> => {
    if (!token) throw new Error("Not authenticated");
    const updated = await apiVerifyPhoneUpdate(phone, otpCode, token);
    setUser(updated);
    await refreshProfile();
    return updated;
  };

  const setupFirstTimePasswordHandler = async (payload: { email: string; phone: string; new_password: string }): Promise<Profile> => {
    const res = await apiSetupFirstTimePassword(payload);
    const accessToken = res.tokens.access_token as string;
    localStorage.setItem("smart_farm_token", accessToken);
    setToken(accessToken);
    setUser(res.user);
    return res.user;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        language,
        units,
        t: translate,
        setLanguage,
        setUnits,
        signIn,
        signUp,
        sendPhoneOtp: sendPhoneOtpHandler,
        verifyPhoneOtp: verifyPhoneOtpHandler,
        requestEmailUpdate: requestEmailUpdateHandler,
        resendVerificationEmail: resendVerificationEmailHandler,
        requestPhoneUpdate: requestPhoneUpdateHandler,
        verifyPhoneUpdate: verifyPhoneUpdateHandler,
        setupFirstTimePassword: setupFirstTimePasswordHandler,
        signOut,
        refreshProfile,
        updateUserProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}