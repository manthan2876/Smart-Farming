import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { login, profile, register } from "../api/auth";
import type { Profile } from "../api/types";

type AuthValue = {
  token: string | null;
  user: Profile | null;
  ready: boolean;
  language: string;
  setLanguage: (language: string) => void;
  signIn: (identifier: string, password: string) => Promise<void>;
  signUp: (payload: {
    name: string;
    email: string;
    password: string;
    location: string;
    language: string;
    crop_history: string[];
  }) => Promise<void>;
  signOut: () => void;
};
const AuthContext = createContext<AuthValue | null>(null);
const tokenKey = "fieldnote_access_token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(() => localStorage.getItem(tokenKey));
  const [user, setUser] = useState<Profile | null>(null);
  const [language, setLanguageState] = useState(
    () => localStorage.getItem("fieldnote_language") ?? "English",
  );
  const [ready, setReady] = useState(() => !localStorage.getItem(tokenKey));
  useEffect(() => {
    if (!token) {
      setReady(true);
      return;
    }
    profile(token)
      .then((data) => {
        setUser(data);
        setLanguageState(data.language);
      })
      .catch(() => {
        localStorage.removeItem(tokenKey);
        setToken(null);
      })
      .finally(() => setReady(true));
  }, [token]);
  async function signIn(identifier: string, password: string) {
    const response = await login(identifier, password);
    localStorage.setItem(tokenKey, response.tokens.access_token);
    localStorage.setItem(
      "fieldnote_refresh_token",
      response.tokens.refresh_token,
    );
    setToken(response.tokens.access_token);
    setUser(response.user);
  }
  async function signUp(payload: {
    name: string;
    email: string;
    password: string;
    location: string;
    language: string;
    crop_history: string[];
  }) {
    const response = await register(payload);
    localStorage.setItem(tokenKey, response.tokens.access_token);
    localStorage.setItem(
      "fieldnote_refresh_token",
      response.tokens.refresh_token,
    );
    setToken(response.tokens.access_token);
    setUser(response.user);
  }
  function signOut() {
    localStorage.removeItem(tokenKey);
    localStorage.removeItem("fieldnote_refresh_token");
    setToken(null);
    setUser(null);
  }
  function setLanguage(language: string) {
    localStorage.setItem("fieldnote_language", language);
    setLanguageState(language);
    setUser((current) => (current ? { ...current, language } : current));
  }
  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        ready,
        language,
        setLanguage,
        signIn,
        signUp,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used within AuthProvider");
  return value;
}
export { profile };
