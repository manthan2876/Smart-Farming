import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogIn, Sprout, CheckCircle2, Phone, Mail, ArrowLeft, ArrowRight, Smartphone } from "../components/icons";
import { motion, AnimatePresence } from "motion/react";
import { Button, Input } from "../components/ui";
import { getDefaultRouteForRole } from "../lib/routes";
import { formatPhoneDisplay } from "../lib/phone";
import ThemeToggle from "../components/ThemeToggle";
import LanguageToggle from "../components/LanguageToggle";

type LoginTab = "phone" | "email";
type PhoneStep = "enter_phone" | "enter_otp";
type EmailStep = "credentials" | "phone_otp_challenge" | "create_password";

const RESEND_COOLDOWN_SECONDS = 60;

export default function LoginPage() {
  const [searchParams] = useSearchParams();
  const resetSuccess = searchParams.get("reset") === "success";
  const verifiedSuccess = searchParams.get("verified") === "true";
  const navigate = useNavigate();
  const { user, isAuthenticated, signIn, sendPhoneOtp, verifyPhoneOtp, setupFirstTimePassword, resendVerificationEmail, t } = useAuth();

  // Mode: "phone" (default for farmers) or "email" (for admins/agronomists)
  const [tab, setTab] = useState<LoginTab>("phone");

  // Phone OTP State
  const [phoneStep, setPhoneStep] = useState<PhoneStep>("enter_phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [countdown, setCountdown] = useState(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Email / Password State
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");

  // Email First-Time OTP & Password Setup State
  const [emailStep, setEmailStep] = useState<EmailStep>("credentials");
  const [challengeEmail, setChallengeEmail] = useState("");
  const [challengePhone, setChallengePhone] = useState("");
  const [challengeMaskedPhone, setChallengeMaskedPhone] = useState("");
  const [challengeOtp, setChallengeOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [unverifiedEmail, setUnverifiedEmail] = useState("");
  const [resendSuccess, setResendSuccess] = useState("");

  // Shared Form State
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      navigate(getDefaultRouteForRole(user.role), { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  // Countdown timer cleanup
  useEffect(() => {
    if (countdown > 0) {
      timerRef.current = setTimeout(() => {
        setCountdown((c) => c - 1);
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [countdown]);

  const startCooldown = () => {
    setCountdown(RESEND_COOLDOWN_SECONDS);
  };

  // 1. Phone Flow: Send OTP
  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const digits = phone.replace(/\D/g, "");
    if (digits.length < 10) {
      setError(t("invalidPhone"));
      return;
    }

    setLoading(true);
    try {
      await sendPhoneOtp(phone.trim(), true);
      setPhoneStep("enter_otp");
      startCooldown();
    } catch (err: any) {
      setError(err.message || t("loginPhoneCodeSendFailed"));
    } finally {
      setLoading(false);
    }
  };

  // 2. Phone Flow: Resend OTP
  const handleResendOtp = async () => {
    if (countdown > 0 || loading) return;
    setError("");
    setLoading(true);
    try {
      await sendPhoneOtp(phone.trim(), true);
      startCooldown();
    } catch (err: any) {
      setError(err.message || t("loginCodeResendFailed"));
    } finally {
      setLoading(false);
    }
  };

  // 3. Phone Flow: Verify OTP & Sign In
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (otp.trim().length < 6) {
      setError(t("invalidOtpLength"));
      return;
    }

    setLoading(true);
    try {
      const loggedUser = await verifyPhoneOtp(phone.trim(), otp.trim());
      const targetRoute = getDefaultRouteForRole(loggedUser.role);
      navigate(targetRoute, { replace: true });
    } catch (err: any) {
      setError(err.message || t("loginCodeInvalid"));
    } finally {
      setLoading(false);
    }
  };

  // 4. Email/Password Flow
  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setResendSuccess("");
    setLoading(true);
    try {
      const loggedUser = await signIn(identifier, password);
      const targetRoute = getDefaultRouteForRole(loggedUser.role);
      navigate(targetRoute, { replace: true });
    } catch (err: any) {
      // Check if backend challenged with phone OTP for first-time email login
      if (
        err?.status === 403 &&
        (err?.detail?.code === "FIRST_TIME_EMAIL_OTP_REQUIRED" || err?.message?.includes("FIRST_TIME_EMAIL_OTP_REQUIRED"))
      ) {
        const rawPhone = err?.detail?.phone || "";
        const masked = err?.detail?.masked_phone || rawPhone;
        const targetEmail = err?.detail?.email || identifier.trim();
        setChallengePhone(rawPhone);
        setChallengeMaskedPhone(masked);
        setChallengeEmail(targetEmail);
        setEmailStep("phone_otp_challenge");
        setError("");
        if (rawPhone) {
          try {
            await sendPhoneOtp(rawPhone, false);
            startCooldown();
          } catch (otpErr: any) {
            setError(otpErr.message || t("loginEmailCodeSendFailed"));
          }
        }
        return;
      }

      // Check if email is unverified
      if (err?.status === 403 && err?.message?.toLowerCase().includes("not verified")) {
        setUnverifiedEmail(identifier.trim());
        setError(err.message || t("loginEmailUnverified"));
        return;
      }

      setError(err.message || t("loginFailed"));
    } finally {
      setLoading(false);
    }
  };

  // 5. First-time Email Login: Verify Phone OTP
  const handleChallengeOtpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (challengeOtp.trim().length < 6) {
      setError(t("invalidOtpLength"));
      return;
    }
    setLoading(true);
    try {
      await verifyPhoneOtp(challengePhone, challengeOtp.trim());
      // OTP verified successfully! Advance to password creation
      setEmailStep("create_password");
    } catch (err: any) {
      setError(err.message || t("loginCodeInvalid"));
    } finally {
      setLoading(false);
    }
  };

  // 6. First-time Email Login: Resend Phone OTP
  const handleChallengeResendOtp = async () => {
    if (countdown > 0 || loading || !challengePhone) return;
    setError("");
    setLoading(true);
    try {
      await sendPhoneOtp(challengePhone, false);
      startCooldown();
    } catch (err: any) {
      setError(err.message || t("loginCodeResendFailed"));
    } finally {
      setLoading(false);
    }
  };

  // 7. First-time Email Login: Save New Password & Finalize
  const handleCreatePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (newPassword.length < 8) {
      setError(t("loginPasswordMinLength"));
      return;
    }
    if (newPassword !== confirmPassword) {
      setError(t("loginPasswordMismatch"));
      return;
    }
    setLoading(true);
    try {
      const loggedUser = await setupFirstTimePassword({
        email: challengeEmail,
        phone: challengePhone,
        new_password: newPassword,
      });
      const targetRoute = getDefaultRouteForRole(loggedUser.role);
      navigate(targetRoute, { replace: true });
    } catch (err: any) {
      setError(err.message || t("loginPasswordSetupFailed"));
    } finally {
      setLoading(false);
    }
  };

  // 8. Resend Unverified Email Link
  const handleResendUnverifiedEmail = async () => {
    if (!unverifiedEmail) return;
    setError("");
    setResendSuccess("");
    setLoading(true);
    try {
      const res = await resendVerificationEmail(unverifiedEmail);
      setResendSuccess(res.message || `${t("loginVerificationResentTo")} ${unverifiedEmail}.`);
    } catch (err: any) {
      setError(err.message || t("loginVerificationResendFailed"));
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
              <CheckCircle2 size={18} className="shrink-0 text-farmer-600 dark:text-farmer-400" />
              <span>{t("passwordResetSuccess")}</span>
            </div>
          )}

          {verifiedSuccess && (
            <div className="mt-6 flex items-center gap-2 rounded-sm border border-green-200 bg-green-50 p-3 text-sm font-medium text-green-800 dark:border-green-900/50 dark:bg-green-950/40 dark:text-green-300">
              <CheckCircle2 size={18} className="shrink-0 text-green-600 dark:text-green-400" />
              <span>{t("loginEmailVerifiedSuccess")}</span>
            </div>
          )}

          {resendSuccess && (
            <div className="mt-6 flex items-center gap-2 rounded-sm border border-green-200 bg-green-50 p-3 text-sm font-medium text-green-800 dark:border-green-900/50 dark:bg-green-950/40 dark:text-green-300">
              <CheckCircle2 size={18} className="shrink-0 text-green-600" />
              <span>{resendSuccess}</span>
            </div>
          )}

          {error && (
            <div className="mt-6 rounded-sm border border-red-100 bg-red-50 p-3 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
              <p>{error}</p>
              {unverifiedEmail && (
                <div className="mt-2.5 pt-2 border-t border-red-200 dark:border-red-900/50">
                  <button
                    type="button"
                    onClick={handleResendUnverifiedEmail}
                    disabled={loading}
                    className="text-xs font-semibold text-farmer-700 underline hover:text-farmer-800 dark:text-farmer-300"
                  >
                    {loading ? t("loginSending") : t("loginResendVerificationEmail")}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Auth Method Tabs */}
          <div className="mt-6 flex rounded-lg border border-line bg-canvas p-1 shadow-xs">
            <button
              type="button"
              onClick={() => {
                setTab("phone");
                setError("");
              }}
              className={`flex flex-1 items-center justify-center gap-2 rounded-md py-2 text-xs font-semibold transition-all ${
                tab === "phone"
                  ? "bg-farmer-700 text-white shadow-xs dark:bg-farmer-600"
                  : "text-muted hover:text-ink"
              }`}
            >
              <Smartphone size={15} />
              <span>{t("phoneLoginTab")}</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setTab("email");
                setError("");
              }}
              className={`flex flex-1 items-center justify-center gap-2 rounded-md py-2 text-xs font-semibold transition-all ${
                tab === "email"
                  ? "bg-farmer-700 text-white shadow-xs dark:bg-farmer-600"
                  : "text-muted hover:text-ink"
              }`}
            >
              <Mail size={15} />
              <span>{t("emailLoginTab")}</span>
            </button>
          </div>

          {/* Tab 1: Phone & OTP Authentication */}
          {tab === "phone" && (
            <div className="mt-6">
              <AnimatePresence mode="wait">
                {phoneStep === "enter_phone" ? (
                  <motion.form
                    key="step-phone"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    onSubmit={handleSendOtp}
                    className="space-y-5"
                  >
                    <div>
                      <label className="text-sm font-semibold text-ink" htmlFor="login-phone">
                        {t("phoneNumber")}
                      </label>
                      <div className="mt-1 flex rounded-md border border-line bg-canvas shadow-xs focus-within:border-farmer-600 focus-within:ring-1 focus-within:ring-farmer-600">
                        <span className="flex items-center px-3 text-sm font-semibold text-muted border-r border-line bg-surface select-none">
                          🇮🇳 +91
                        </span>
                        <input
                          id="login-phone"
                          type="tel"
                          inputMode="numeric"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          placeholder="99999 99999"
                          required
                          className="w-full bg-transparent px-3 py-2 text-sm text-ink placeholder:text-muted/60 focus:outline-hidden"
                        />
                      </div>
                      <p className="mt-1 text-xs text-muted">
                        {t("phoneOtpLoginSubtitle")}
                      </p>
                    </div>

                    <Button type="submit" disabled={loading} className="w-full">
                      <Phone size={16} />
                      {loading ? t("sendingOtp") : t("sendOtp")}
                      <ArrowRight size={15} className="ml-1" />
                    </Button>
                  </motion.form>
                ) : (
                  <motion.form
                    key="step-otp"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    onSubmit={handleVerifyOtp}
                    className="space-y-5"
                  >
                    <div className="rounded-lg border border-line bg-surface/50 p-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-xs text-muted">{t("enterOtpSubtitle")}</p>
                          <p className="text-sm font-bold text-ink">{formatPhoneDisplay(phone)}</p>
                        </div>
                        <button
                          type="button"
                          onClick={() => {
                            setPhoneStep("enter_phone");
                            setError("");
                          }}
                          className="flex items-center gap-1 text-xs font-semibold text-farmer-700 hover:underline dark:text-farmer-300"
                        >
                          <ArrowLeft size={13} />
                          {t("changePhoneNumber")}
                        </button>
                      </div>
                    </div>

                    <div>
                      <Input
                        id="login-otp"
                        label={t("enterOtp")}
                        type="text"
                        inputMode="numeric"
                        autoComplete="one-time-code"
                        maxLength={6}
                        value={otp}
                        onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                        placeholder="123456"
                        required
                        className="text-center font-mono text-xl tracking-widest"
                      />
                    </div>

                    <Button type="submit" disabled={loading || otp.length < 6} className="w-full">
                      <LogIn size={17} />
                      {loading ? t("verifying") : t("verifyAndSignIn")}
                    </Button>

                    <div className="flex items-center justify-between text-xs pt-1">
                      <span className="text-muted">
                        {countdown > 0 ? (
                          <>
                            {t("resendOtpIn")} <span className="font-bold text-ink">{countdown}{t("seconds")}</span>
                          </>
                        ) : (
                          t("loginDidNotReceiveSmsCode")
                        )}
                      </span>
                      <button
                        type="button"
                        onClick={handleResendOtp}
                        disabled={countdown > 0 || loading}
                        className={`font-semibold transition-colors ${
                          countdown > 0 || loading
                            ? "cursor-not-allowed text-muted/50"
                            : "text-farmer-700 hover:underline dark:text-farmer-300"
                        }`}
                      >
                        {t("resendOtp")}
                      </button>
                    </div>
                  </motion.form>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* Tab 2: Email Authentication (With first-time mobile OTP and password setup) */}
          {tab === "email" && (
            <AnimatePresence mode="wait">
              {emailStep === "credentials" && (
                <motion.form
                  key="step-credentials"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  onSubmit={handleEmailSubmit}
                  className="mt-6 space-y-5"
                >
                  <Input 
                    id="login-identifier" 
                    label={t("loginEmailOrPhone")}
                    type="text" 
                    value={identifier} 
                    onChange={(e) => setIdentifier(e.target.value)}
                    placeholder={t("loginEmailOrPhonePlaceholder")}
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
                </motion.form>
              )}

              {emailStep === "phone_otp_challenge" && (
                <motion.form
                  key="step-challenge"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  onSubmit={handleChallengeOtpSubmit}
                  className="mt-6 space-y-5"
                >
                  <div className="rounded-lg border border-farmer-200/80 bg-farmer-50/70 p-4 text-xs text-farmer-950 dark:border-farmer-900/40 dark:bg-farmer-950/30 dark:text-farmer-200">
                    <div className="font-semibold text-sm mb-1 text-farmer-800 dark:text-farmer-300 flex items-center gap-1.5">
                      <Smartphone size={16} />
                      <span>{t("loginFirstTimeEmailSignIn")}</span>
                    </div>
                    <div className="leading-relaxed">
                      {t("loginFirstTimeEmailPrefix")} <strong className="text-ink">{challengeEmail}</strong>.
                      {" "}{t("loginFirstTimeEmailCode")}{" "}
                      <span className="font-semibold underline">{challengeMaskedPhone}</span>.
                    </div>
                  </div>

                  <div>
                    <Input
                      id="challenge-otp"
                      label={t("enterOtp")}
                      type="text"
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      maxLength={6}
                      value={challengeOtp}
                      onChange={(e) => setChallengeOtp(e.target.value.replace(/\D/g, ""))}
                      placeholder="123456"
                      required
                      className="text-center font-mono text-xl tracking-widest"
                    />
                  </div>

                  <Button type="submit" disabled={loading || challengeOtp.length < 6} className="w-full">
                    <LogIn size={17} />
                    {loading ? t("verifying") : t("loginVerifyCodeContinue")}
                  </Button>

                  <div className="flex items-center justify-between text-xs pt-1">
                    <button
                      type="button"
                      onClick={() => {
                        setEmailStep("credentials");
                        setError("");
                      }}
                      className="flex items-center gap-1 font-semibold text-muted hover:text-ink transition-colors"
                    >
                      <ArrowLeft size={13} />
                      {t("loginBackToEmail")}
                    </button>

                    <button
                      type="button"
                      onClick={handleChallengeResendOtp}
                      disabled={countdown > 0 || loading}
                      className={`font-semibold transition-colors ${
                        countdown > 0 || loading
                          ? "cursor-not-allowed text-muted/50"
                          : "text-farmer-700 hover:underline dark:text-farmer-300"
                      }`}
                    >
                      {countdown > 0 ? `${t("resendOtpIn")} ${countdown}s` : t("resendOtp")}
                    </button>
                  </div>
                </motion.form>
              )}

              {emailStep === "create_password" && (
                <motion.form
                  key="step-create-password"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  onSubmit={handleCreatePasswordSubmit}
                  className="mt-6 space-y-5"
                >
                  <div className="rounded-lg border border-farmer-200/80 bg-farmer-50/70 p-4 text-xs text-farmer-950 dark:border-farmer-900/40 dark:bg-farmer-950/30 dark:text-farmer-200">
                    <div className="font-semibold text-sm mb-1 text-farmer-800 dark:text-farmer-300 flex items-center gap-1.5">
                      <CheckCircle2 size={16} />
                      <span>{t("loginMobileNumberVerified")}</span>
                    </div>
                    <div className="leading-relaxed">
                      {t("loginSetPasswordPrefix")} <strong className="text-ink">{challengeEmail}</strong>.{" "}
                      {t("loginSetPasswordSuffix")}
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Input
                      id="challenge-new-password"
                      label={t("loginCreatePassword")}
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder={t("loginPasswordLengthPlaceholder")}
                      required
                      minLength={8}
                    />

                    <Input
                      id="challenge-confirm-password"
                      label={t("loginConfirmPassword")}
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder={t("loginReenterPassword")}
                      required
                      minLength={8}
                    />
                  </div>

                  <Button type="submit" disabled={loading || newPassword.length < 8 || !confirmPassword} className="w-full">
                    <CheckCircle2 size={17} />
                    {loading ? t("loginSavingPassword") : t("loginSavePasswordSignIn")}
                  </Button>
                </motion.form>
              )}
            </AnimatePresence>
          )}

          <div className="mt-8 text-center text-sm text-muted">
            {t("dontHaveAccount")}{" "}
            <Link className="font-semibold text-farmer-700 dark:text-farmer-300 underline" to="/auth/register">
              {t("createAccount")}
            </Link>
            <div className="mt-5">
              <Link className="text-xs text-muted hover:text-ink transition-colors" to="/">
                {t("backToHome")}
              </Link>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="relative hidden min-h-[26rem] items-end overflow-hidden bg-farmer-950 bg-[url('https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center p-10 lg:flex lg:p-16 border-l border-line">
        <div className="absolute inset-0 bg-farmer-950/70" />
        <div className="relative z-10 text-white space-y-3">
          <h2 className="max-w-xl font-display text-3xl leading-tight">{t("loginBannerTitle")}</h2>
          <p className="text-xs font-semibold uppercase tracking-wider text-farmer-200">{t("loginBannerSubtitle")}</p>
        </div>
      </div>
    </div>
  );
}
