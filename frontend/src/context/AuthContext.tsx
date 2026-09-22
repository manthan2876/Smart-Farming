import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { login, profile, register, logout, updateProfile, AuthResponse } from "../api/auth";
import { Profile } from "../api/types";
import { Language, Units, t, TranslationKey } from "../i18n";

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
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
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
      const userData = await profile(authToken);
      setUser(userData);
      if (userData.language && (userData.language === "Gujarati" || userData.language === "Hindi" || userData.language === "English")) {
        setLanguageState(userData.language as Language);
        localStorage.setItem(PREF_LANG_KEY, userData.language);
      }
    } catch {
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

    const handleTokenRefresh = (e: Event) => {
      const customEvent = e as CustomEvent<string>;
      setToken(customEvent.detail);
    };

    window.addEventListener("tokenRefreshed", handleTokenRefresh);
    return () => window.removeEventListener("tokenRefreshed", handleTokenRefresh);
  }, [token]);

  const setLanguage = async (newLang: Language) => {
    setLanguageState(newLang);
    localStorage.setItem(PREF_LANG_KEY, newLang);
    if (token && user) {
      try {
        const updated = await updateProfile({ language: newLang }, token);
        setUser(updated);
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
      password: payload.password,
      location: payload.location,
      language: payload.language,
      crop_history: payload.crop_history || [],
    });
    const accessToken = res.tokens.access_token;
    localStorage.setItem("smart_farm_token", accessToken);
    setToken(accessToken);
    setUser(res.user);
    if (payload.language && (payload.language === "Gujarati" || payload.language === "Hindi" || payload.language === "English")) {
      setLanguageState(payload.language as Language);
      localStorage.setItem(PREF_LANG_KEY, payload.language);
    }
    return res.user;
  };

  const signOut = async () => {
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
        signOut,
        refreshProfile,
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