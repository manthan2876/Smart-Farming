import { useState, useEffect } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogIn, Sprout, CheckCircle2 } from "../components/icons";
import { motion } from "motion/react";
import { Button, Input } from "../components/ui";
import { getDefaultRouteForRole } from "../lib/routes";
import ThemeToggle from "../components/ThemeToggle";
import LanguageToggle from "../components/LanguageToggle";

export default function LoginPage() {
  const [searchParams] = useSearchParams();
  const resetSuccess = searchParams.get("reset") === "success";
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { user, isAuthenticated, signIn, t } = useAuth();

  // If already authenticated, redirect to role's designated landing route
  useEffect(() => {
    if (isAuthenticated && user) {
      navigate(getDefaultRouteForRole(user.role), { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const loggedUser = await signIn(identifier, password);
      const targetRoute = getDefaultRouteForRole(loggedUser.role);
      navigate(targetRoute, { replace: true });
    } catch (err: any) {
      setError(err.message || "Failed to login. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative grid min-h-screen bg-canvas lg:grid-cols-2">
      <div className="absolute right-4 top-4 z-20 flex items-center gap-2">
        <LanguageToggle />
        <ThemeToggle />
      </div>
      <div className="flex items-center justify-center px-5 py-12 sm:px-10 lg:px-16">
        <motion.div 
          className="w-full max-w-md"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <Sprout className="mb-7 text-farmer-700 dark:text-farmer-300" size={40} />
          <h2 className="font-display text-3xl text-ink sm:text-4xl">{t("greeting")}</h2>
          <p className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-muted">[{t("platformControl")}]</p>

          {resetSuccess && (
            <div className="mt-6 flex items-center gap-2 rounded-sm border border-farmer-200 bg-farmer-50 p-3 text-sm font-medium text-farmer-800 dark:border-farmer-900/50 dark:bg-farmer-950/40 dark:text-farmer-300">
              <CheckCircle2 size={18} className="shrink-0 text-farmer-600" />
              <span>{t("passwordResetSuccess")}</span>
            </div>
          )}

          {error && <div className="mt-6 rounded-sm border border-red-100 bg-red-50 p-3 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">{error}</div>}

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <Input 
              id="login-identifier" 
              label={t("emailOrPhone")}
              type="text" 
              value={identifier} 
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="farmer@example.com"
              required 
            />
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <label className="text-sm font-semibold text-ink" htmlFor="login-password">
                  {t("password")}
                </label>
                <Link
                  to="/auth/forgot-password"
                  className="text-xs font-semibold text-farmer-700 hover:underline dark:text-farmer-300"
                >
                  {t("forgotPassword")}
                </Link>
              </div>
              <Input
                id="login-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
            <Button type="submit" disabled={loading} className="mt-2 w-full">
              <LogIn size={17} />
              {loading ? t("signingIn") : t("signIn")}
            </Button>
          </form>

          <div className="mt-8 text-center text-sm text-muted">
            {t("dontHaveAccount")} <Link className="font-semibold text-farmer-700 dark:text-farmer-300 underline" to="/auth/register">{t("createAccount")}</Link>
            <div className="mt-5"><Link className="text-xs text-muted hover:text-ink transition-colors" to="/">{t("backToHome")}</Link></div>
          </div>
        </motion.div>
      </div>
      <div className="relative hidden min-h-[26rem] items-end overflow-hidden bg-farmer-950 bg-[url('https://images.unsplash.com/photo-1592982537447-6f29fbdb9e31?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center p-10 lg:flex lg:p-16 border-l border-line">
        <div className="absolute inset-0 bg-farmer-950/70" />
        <div className="relative z-10 text-white space-y-3">
          <h2 className="max-w-xl font-display text-3xl leading-tight">{t("loginBannerTitle")}</h2>
          <p className="text-xs font-semibold uppercase tracking-wider text-farmer-200">{t("loginBannerSubtitle")}</p>
        </div>
      </div>
    </div>
  );
}
