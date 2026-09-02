import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { login, profile, register, AuthResponse } from "../api/auth";
import { Profile } from "../api/types";

interface AuthContextType {
  user: Profile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signIn: (identifier: string, pass: string) => Promise<void>;
  signUp: (payload: { name: string; email?: string; phone?: string; password: string; location: string; language: string; crop_history?: string[] }) => Promise<void>;
  signOut: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Profile | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("smart_farm_token"));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchUserProfile = async (authToken: string) => {
    try {
      const userData = await profile(authToken);
      setUser(userData);
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

  const signIn = async (identifier: string, pass: string) => {
    const res: AuthResponse = await login(identifier, pass);
    const accessToken = res.tokens.access_token;
    localStorage.setItem("smart_farm_token", accessToken);
    setToken(accessToken);
    setUser(res.user);
  };

  const signUp = async (payload: { name: string; email?: string; phone?: string; password: string; location: string; language: string; crop_history?: string[] }) => {
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
  };

  const signOut = () => {
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