import { useState, useEffect } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { CheckCircle2, AlertTriangle, Sprout, ArrowRight, Mail, RefreshCw } from "../components/icons";
import { motion } from "motion/react";
import { Button, Card, Input } from "../components/ui";
import { verifyEmail, resendVerificationEmail, verifyEmailOtp } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import { supabase } from "../lib/supabase";
import ThemeToggle from "../components/ThemeToggle";
import LanguageToggle from "../components/LanguageToggle";

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const queryToken = searchParams.get("token");
  const code = searchParams.get("code");
  const navigate = useNavigate();
  const { isAuthenticated, refreshProfile, user } = useAuth();

  const [loading, setLoading] = useState<boolean>(true);
  const [success, setSuccess] = useState<boolean>(false);
  const [message, setMessage] = useState<string>("");
  const [error, setError] = useState<string>("");

  // Interactive recovery state
  const [emailInput, setEmailInput] = useState<string>(() => {
    return user?.email || localStorage.getItem("pending_verify_email") || "";
  });
  const [otpInput, setOtpInput] = useState<string>("");
  const [resending, setResending] = useState<boolean>(false);
  const [resendStatus, setResendStatus] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [verifyingOtp, setVerifyingOtp] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;

    const runVerification = async () => {
      // 1. Check for error parameters in hash or query
      const hash = window.location.hash;
      const hashParams = new URLSearchParams(hash.startsWith("#") ? hash.substring(1) : hash);
      const errorDesc = searchParams.get("error_description") || hashParams.get("error_description");
      if (errorDesc) {
        if (isMounted) {
          setError(decodeURIComponent(errorDesc.replace(/\+/g, " ")));
          setLoading(false);
        }
        return;
      }

      // 2. If code (PKCE) is present, exchange it
      let activeSession = null;
      if (code) {
        try {
          const { data } = await supabase.auth.exchangeCodeForSession(code);
          activeSession = data.session;
        } catch {}
      }

      // 3. Check for hash tokens or active Supabase session
      if (!activeSession) {
        try {
          const { data } = await supabase.auth.getSession();
          activeSession = data.session;
        } catch {}
      }

      const activeToken = queryToken || activeSession?.access_token || "";

      if (!activeToken && !activeSession && !hash.includes("access_token")) {
        if (isMounted) {
          setLoading(false);
          setError("No verification token was provided in the link.");
        }
        return;
      }

      try {
        const res = await verifyEmail(activeToken);
        if (isMounted) {
          setSuccess(true);
          setMessage(res.message || "Your email address has been verified successfully!");
          await refreshProfile().catch(() => {});
        }
      } catch (err: any) {
        // If Supabase session has confirmed email, treat as successful
        if (activeSession?.user?.email_confirmed_at || activeSession?.user?.email) {
          if (isMounted) {
            setSuccess(true);
            setMessage("Your email address has been verified successfully!");
            await refreshProfile().catch(() => {});
          }
        } else {
          if (isMounted) {
            setError(
              err.message ||
                "Verification link is invalid or has expired. Please request a new verification link."
            );
          }
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    runVerification();
    return () => {
      isMounted = false;
    };
  }, [queryToken, code]);

  const handleResend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!emailInput.trim()) {
      setResendStatus({ type: "error", text: "Please enter your email address." });
      return;
    }
    setResending(true);
    setResendStatus(null);
    try {
      const res = await resendVerificationEmail(emailInput.trim());
      setResendStatus({
        type: "success",
        text: res.message || "A fresh verification email has been sent. Please check your inbox.",
      });
    } catch (err: any) {
      setResendStatus({
        type: "error",
        text: err.message || "Failed to resend email. Please verify the address and try again.",
      });
    } finally {
      setResending(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!emailInput.trim() || !otpInput.trim()) {
      setResendStatus({ type: "error", text: "Please enter both email and 6-digit confirmation code." });
      return;
    }
    setVerifyingOtp(true);
    setResendStatus(null);
    try {
      const res = await verifyEmailOtp(emailInput.trim(), otpInput.trim());
      setSuccess(true);
      setError("");
      setMessage(res.message || "Email verified successfully!");
      await refreshProfile().catch(() => {});
    } catch (err: any) {
      setResendStatus({
        type: "error",
        text: err.message || "Invalid or expired confirmation code. Please request a fresh one.",
      });
    } finally {
      setVerifyingOtp(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-canvas px-4 py-12">
      <div className="absolute right-4 top-4 z-20 flex items-center gap-2">
        <LanguageToggle />
        <ThemeToggle />
      </div>

      <motion.div
        className="w-full max-w-md"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="mb-6 text-center">
          <Link to="/" className="inline-flex items-center gap-2 font-display text-2xl font-bold text-ink">
            <Sprout size={32} className="text-farmer-700 dark:text-farmer-300" />
            <span>Smart Farming</span>
          </Link>
        </div>

        <Card className="p-8 text-center shadow-lg">
          {loading && (
            <div className="py-8 space-y-4">
              <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-farmer-200 border-t-farmer-600 dark:border-farmer-900 dark:border-t-farmer-400" />
              <h2 className="font-display text-xl text-ink">Verifying Email...</h2>
              <p className="text-sm text-muted">
                Please wait while we confirm your email address.
              </p>
            </div>
          )}

          {!loading && success && (
            <div className="py-4 space-y-5 animate-fadeIn">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-farmer-100 text-farmer-700 dark:bg-farmer-950 dark:text-farmer-300">
                <CheckCircle2 size={36} />
              </div>
              <div>
                <h2 className="font-display text-2xl text-ink">Email Verified!</h2>
                <p className="mt-2 text-sm text-muted">
                  {message}
                </p>
              </div>

              <div className="pt-4">
                {isAuthenticated ? (
                  <Button
                    onClick={() => navigate("/settings")}
                    className="w-full flex items-center justify-center gap-2"
                  >
                    <span>Return to Settings</span>
                    <ArrowRight size={16} />
                  </Button>
                ) : (
                  <Button
                    onClick={() => navigate("/auth/login?verified=true")}
                    className="w-full flex items-center justify-center gap-2"
                  >
                    <span>Proceed to Login</span>
                    <ArrowRight size={16} />
                  </Button>
                )}
              </div>
            </div>
          )}

          {!loading && error && (
            <div className="py-2 space-y-5 text-left animate-fadeIn">
              <div className="text-center">
                <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-red-100 text-danger dark:bg-red-950 dark:text-red-400">
                  <AlertTriangle size={32} />
                </div>
                <h2 className="font-display text-2xl font-bold text-ink">Link Invalid or Expired</h2>
                <p className="mt-2 text-sm text-danger dark:text-red-300 font-medium">
                  {error}
                </p>
              </div>

              <div className="rounded-lg bg-surface border border-slate-200 dark:border-slate-800 p-3.5 text-xs text-muted leading-relaxed">
                💡 <strong>Why this happens:</strong> Supabase invalidates earlier verification links whenever a newer email is requested, or after the token expiry window.
              </div>

              {resendStatus && (
                <div
                  className={`rounded-lg p-3 text-xs font-medium ${
                    resendStatus.type === "success"
                      ? "bg-green-50 text-farmer-800 border border-green-200 dark:bg-green-950/40 dark:text-green-300 dark:border-green-800"
                      : "bg-red-50 text-red-700 border border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800"
                  }`}
                >
                  {resendStatus.text}
                </div>
              )}

              {/* Option 1: 6-Digit OTP */}
              <form onSubmit={handleVerifyOtp} className="space-y-3 pt-1 border-t border-slate-100 dark:border-slate-800">
                <p className="text-xs font-semibold text-ink uppercase tracking-wider">
                  Option 1: Enter 6-Digit Code from Email
                </p>
                <Input
                  type="email"
                  placeholder="your-email@example.com"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  leadingIcon={<Mail size={16} />}
                  required
                />
                <div className="flex gap-2">
                  <Input
                    type="text"
                    maxLength={6}
                    placeholder="e.g. 529183"
                    value={otpInput}
                    onChange={(e) => setOtpInput(e.target.value)}
                    className="text-center font-mono tracking-widest text-lg"
                    required
                  />
                  <Button
                    type="submit"
                    disabled={verifyingOtp || !otpInput.trim()}
                    className="whitespace-nowrap px-4"
                  >
                    {verifyingOtp ? "Verifying..." : "Verify"}
                  </Button>
                </div>
              </form>

              {/* Option 2: Resend Fresh Link */}
              <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                <p className="text-xs font-semibold text-ink uppercase tracking-wider">
                  Option 2: Send a Fresh Verification Link
                </p>
                <Button
                  onClick={handleResend}
                  disabled={resending || !emailInput.trim()}
                  variant="secondary"
                  className="w-full flex items-center justify-center gap-2"
                >
                  <RefreshCw size={14} className={resending ? "animate-spin" : ""} />
                  <span>{resending ? "Sending New Link..." : "Resend Verification Link"}</span>
                </Button>
              </div>

              <div className="pt-2 text-center">
                <Button
                  onClick={() => navigate("/auth/login")}
                  variant="ghost"
                  className="text-xs text-muted hover:text-ink"
                >
                  Return to Login
                </Button>
              </div>
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  );
}
