import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { forgotPassword } from "../api/auth";
import { Sprout, Mail, ArrowLeft, CheckCircle2 } from "lucide-react";
import { motion } from "motion/react";
import { Button, Input } from "../components/ui";
import ThemeToggle from "../components/ThemeToggle";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const { t } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await forgotPassword(email.trim());
      setSubmitted(true);
    } catch (err: any) {
      setError(err.message || "Failed to process request. Please try again.");
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

          {submitted ? (
            <div className="rounded-md border border-line bg-surface p-6 text-center shadow-soft">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-farmer-100 text-farmer-700 dark:bg-farmer-950 dark:text-farmer-300">
                <CheckCircle2 size={32} />
              </div>
              <h2 className="mt-5 font-display text-2xl text-ink">
                {t("resetLinkSentTitle")}
              </h2>
              <p className="mt-3 text-sm text-muted">
                {t("resetLinkSentDesc")}
              </p>
              <div className="mt-7">
                <Link to="/auth/login">
                  <Button className="w-full">
                    <ArrowLeft size={16} />
                    {t("backToLogin")}
                  </Button>
                </Link>
              </div>
            </div>
          ) : (
            <>
              <h2 className="font-display text-3xl text-ink sm:text-4xl">
                {t("forgotPasswordTitle")}
              </h2>
              <p className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-muted">
                [PASSWORD RECOVERY]
              </p>
              <p className="mt-3 text-sm text-muted">
                {t("forgotPasswordSubtitle")}
              </p>

              {error && (
                <div className="mt-6 rounded-sm border border-red-100 bg-red-50 p-3 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="mt-8 space-y-5">
                <Input
                  id="forgot-email"
                  label="Registered Email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="farmer@example.com"
                  leadingIcon={<Mail size={16} />}
                  required
                />
                <Button type="submit" disabled={loading} className="mt-2 w-full">
                  {loading ? t("sendingResetLink") : t("sendResetLink")}
                </Button>
              </form>

              <div className="mt-8 text-center text-sm text-muted">
                <Link
                  className="inline-flex items-center gap-1 font-bold text-farmer-700 underline dark:text-farmer-300"
                  to="/auth/login"
                >
                  <ArrowLeft size={14} />
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
            "Your crops and account are always secure. Instant recovery whenever you need it."
          </h2>
          <p className="mt-5 text-xs font-bold uppercase tracking-[0.14em] text-farmer-300">
            [SMART FARMING SECURITY]
          </p>
        </div>
      </div>
    </div>
  );
}
