import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { resetPassword } from "../api/auth";
import { Sprout, Lock, KeyRound, AlertTriangle, CheckCircle2 } from "lucide-react";
import { motion } from "motion/react";
import { Button, Input } from "../components/ui";
import ThemeToggle from "../components/ThemeToggle";

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const navigate = useNavigate();
  const { t } = useAuth();

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!token) {
      setError(t("missingResetToken"));
      return;
    }

    if (newPassword.length < 8) {
      setError(t("passwordTooShort"));
      return;
    }

    if (newPassword !== confirmPassword) {
      setError(t("passwordsDoNotMatch"));
      return;
    }

    setLoading(true);
    try {
      await resetPassword(token, newPassword);
      setSuccess(true);
      setTimeout(() => {
        navigate("/auth/login?reset=success", { replace: true });
      }, 2000);
    } catch (err: any) {
      setError(err.message || "Failed to reset password. The link may have expired.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative grid min-h-screen bg-canvas lg:grid-cols-2">
      <div className="absolute right-4 top-4 z-20">
        <ThemeToggle />
      </div>

      <div className="flex items-center justify-center px-5 py-12 sm:px-10 lg:px-16">
        <motion.div
          className="w-full max-w-md"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <Sprout className="mb-7 text-farmer-700 dark:text-farmer-300" size={40} />

          {!token ? (
            <div className="rounded-md border border-line bg-surface p-6 shadow-soft">
              <div className="flex items-center gap-3 text-danger">
                <AlertTriangle size={24} />
                <h3 className="font-display text-xl text-ink">Invalid Reset Link</h3>
              </div>
              <p className="mt-3 text-sm text-muted">
                {t("missingResetToken")}
              </p>
              <div className="mt-6">
                <Link to="/auth/forgot-password">
                  <Button className="w-full">
                    Request New Reset Link
                  </Button>
                </Link>
              </div>
            </div>
          ) : success ? (
            <div className="rounded-md border border-line bg-surface p-6 text-center shadow-soft">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-farmer-100 text-farmer-700 dark:bg-farmer-950 dark:text-farmer-300">
                <CheckCircle2 size={32} />
              </div>
              <h2 className="mt-5 font-display text-2xl text-ink">
                {t("passwordResetSuccess")}
              </h2>
              <p className="mt-3 text-sm text-muted">
                Redirecting you to the sign in page...
              </p>
              <div className="mt-6">
                <Link to="/auth/login">
                  <Button className="w-full">
                    {t("backToLogin")}
                  </Button>
                </Link>
              </div>
            </div>
          ) : (
            <>
              <h2 className="font-display text-3xl text-ink sm:text-4xl">
                {t("resetPasswordTitle")}
              </h2>
              <p className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-muted">
                [UPDATE CREDENTIALS]
              </p>
              <p className="mt-3 text-sm text-muted">
                {t("resetPasswordSubtitle")}
              </p>

              {error && (
                <div className="mt-6 rounded-sm border border-red-100 bg-red-50 p-3 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="mt-8 space-y-5">
                <Input
                  id="reset-new-password"
                  label={t("newPassword")}
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="••••••••"
                  leadingIcon={<KeyRound size={16} />}
                  required
                />
                <Input
                  id="reset-confirm-password"
                  label={t("confirmNewPassword")}
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  leadingIcon={<Lock size={16} />}
                  required
                />

                <Button type="submit" disabled={loading} className="mt-2 w-full">
                  {loading ? t("resettingPassword") : t("resetPassword")}
                </Button>
              </form>

              <div className="mt-8 text-center text-sm text-muted">
                <Link className="font-bold text-farmer-700 underline dark:text-farmer-300" to="/auth/login">
                  {t("backToLogin")}
                </Link>
                <div className="mt-5">
                  <Link className="text-muted hover:text-ink" to="/">
                    ← Back to Home
                  </Link>
                </div>
              </div>
            </>
          )}
        </motion.div>
      </div>

      <div className="relative hidden min-h-[26rem] items-end overflow-hidden border-l border-line bg-farmer-950 bg-[url('https://images.unsplash.com/photo-1592982537447-6f29fbdb9e31?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center p-10 lg:flex lg:p-16">
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/45 to-black/20" />
        <div className="relative z-10 text-white">
          <h2 className="max-w-xl font-display text-4xl leading-tight">
            "Your secure farm management platform. Strong passwords protect your agricultural data."
          </h2>
          <p className="mt-5 text-xs font-bold uppercase tracking-[0.14em] text-farmer-300">
            [SMART FARMING INTELLIGENCE]
          </p>
        </div>
      </div>
    </div>
  );
}
