import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { UserPlus, Sprout, Globe, Phone, Mail, ArrowLeft, ArrowRight, Smartphone, CheckCircle2 } from "../components/icons";
import { motion, AnimatePresence } from "motion/react";
import { Button, Input, Select } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { getDefaultRouteForRole } from "../lib/routes";
import { formatPhoneDisplay } from "../lib/phone";
import ThemeToggle from "../components/ThemeToggle";
import LanguageToggle from "../components/LanguageToggle";

type RegisterMode = "phone" | "email";
type RegisterStep = "details" | "verify_otp";

const RESEND_COOLDOWN_SECONDS = 60;

export default function RegisterPage() {
  const [mode, setMode] = useState<RegisterMode>("phone");
  const [step, setStep] = useState<RegisterStep>("details");

  // Form Fields
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [language, setLanguage] = useState("English");
  const [location, setLocation] = useState("Gujarat, India");
  const [otp, setOtp] = useState("");

  // Email Mode Fields
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Cooldown timer state
  const [countdown, setCountdown] = useState(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [emailVerificationSent, setEmailVerificationSent] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState("");
  const [resendSuccess, setResendSuccess] = useState("");
  const navigate = useNavigate();
  const { signUp, sendPhoneOtp, verifyPhoneOtp, resendVerificationEmail, isAuthenticated, user, t } = useAuth();

  useEffect(() => {
    if (isAuthenticated && user) {
      navigate(getDefaultRouteForRole(user.role), { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

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

  // Step 1: Send OTP for Phone Registration
  const handleSendRegistrationOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!name.trim()) {
      setError("Please enter your full name.");
      return;
    }

    const digits = phone.replace(/\D/g, "");
    if (digits.length < 10) {
      setError(t("invalidPhone"));
      return;
    }

    setLoading(true);
    try {
      await sendPhoneOtp(phone.trim(), true, {
        name: name.trim(),
        language,
        location: location.trim(),
      });
      setStep("verify_otp");
      startCooldown();
    } catch (err: any) {
      setError(err.message || "Failed to send verification code. Please check your number.");
    } finally {
      setLoading(false);
    }
  };

  // Resend OTP in Registration Flow
  const handleResendRegistrationOtp = async () => {
    if (countdown > 0 || loading) return;
    setError("");
    setLoading(true);
    try {
      await sendPhoneOtp(phone.trim(), true, {
        name: name.trim(),
        language,
        location: location.trim(),
      });
      startCooldown();
    } catch (err: any) {
      setError(err.message || "Failed to resend code.");
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Verify OTP and finalize onboarding
  const handleVerifyRegistrationOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (otp.trim().length < 6) {
      setError(t("invalidOtpLength"));
      return;
    }

    setLoading(true);
    try {
      const newUser = await verifyPhoneOtp(phone.trim(), otp.trim(), {
        name: name.trim(),
        language,
        location: location.trim(),
      });
      navigate(getDefaultRouteForRole(newUser.role), { replace: true });
    } catch (err: any) {
      setError(err.message || "Verification failed. Please check the code.");
    } finally {
      setLoading(false);
    }
  };

  // Traditional Email Registration
  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setResendSuccess("");
    setLoading(true);
    try {
      const newUser = await signUp({
        name: name.trim(),
        email: email.trim(),
        password,
        language,
        location: location.trim(),
      });

      // If user requires email verification (tokens empty / unverified)
      if (newUser && newUser.is_email_verified === false) {
        setRegisteredEmail(email.trim());
        setEmailVerificationSent(true);
        return;
      }

      navigate(getDefaultRouteForRole(newUser.role), { replace: true });
    } catch (err: any) {
      if (err.message && err.message.toLowerCase().includes("check your email")) {
        setRegisteredEmail(email.trim());
        setEmailVerificationSent(true);
        return;
      }
      setError(err.message || "Failed to create account.");
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

      <div className="flex items-center justify-center px-5 py-10 sm:px-10 lg:px-16">
        <motion.div 
          className="w-full max-w-2xl"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <Sprout className="mb-6 text-farmer-700 dark:text-farmer-300" size={40} />
          <h2 className="font-display text-3xl text-ink sm:text-4xl">{t("registerTitle")}</h2>
          <p className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-muted">[{t("platformControl")}]</p>

          {error && (
            <div className="mt-6 rounded-sm border border-red-100 bg-red-50 p-3 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
              {error}
            </div>
          )}

          {emailVerificationSent ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-6 rounded-xl border border-line bg-canvas p-8 text-center shadow-xs space-y-6"
            >
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-farmer-100 text-farmer-700 dark:bg-farmer-950 dark:text-farmer-300">
                <Mail size={36} />
              </div>

              <div>
                <h3 className="font-display text-2xl text-ink">{t("checkYourEmail")}</h3>
                <p className="mt-2 text-sm text-muted max-w-md mx-auto leading-relaxed">
                  {t("accountActivationEmailSent")} <strong className="text-ink">{registeredEmail}</strong>.
                  {" "}{t("openInboxToActivate")}
                </p>
              </div>

              {resendSuccess && (
                <div className="flex items-center justify-center gap-2 text-xs font-semibold text-green-700 dark:text-green-300">
                  <CheckCircle2 size={15} />
                  <span>{resendSuccess}</span>
                </div>
              )}

              <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
                <Button
                  onClick={() => navigate("/auth/login")}
                  className="w-full sm:w-auto"
                >
                  {t("proceedToLogin")}
                </Button>
                <Button
                  variant="secondary"
                  disabled={loading}
                  onClick={async () => {
                    setLoading(true);
                    try {
                      const res = await resendVerificationEmail(registeredEmail);
                      setResendSuccess(res.message || t("verificationEmailResent"));
                      setTimeout(() => setResendSuccess(""), 6000);
                    } catch (err: any) {
                      setError(err.message || "Failed to resend.");
                    } finally {
                      setLoading(false);
                    }
                  }}
                  className="w-full sm:w-auto"
                >
                  {loading ? t("loginSending") : t("resendVerificationLink")}
                </Button>
              </div>
            </motion.div>
          ) : (
            <>
              {/* Registration Mode Selector */}
              <div className="mt-6 flex rounded-lg border border-line bg-canvas p-1 shadow-xs">
                <button
                  type="button"
                  onClick={() => {
                    setMode("phone");
                    setStep("details");
                    setError("");
                  }}
                  className={`flex flex-1 items-center justify-center gap-2 rounded-md py-2 text-xs font-semibold transition-all ${
                    mode === "phone"
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
                    setMode("email");
                    setError("");
                  }}
                  className={`flex flex-1 items-center justify-center gap-2 rounded-md py-2 text-xs font-semibold transition-all ${
                    mode === "email"
                      ? "bg-farmer-700 text-white shadow-xs dark:bg-farmer-600"
                      : "text-muted hover:text-ink"
                  }`}
                >
                  <Mail size={15} />
                  <span>{t("emailLoginTab")}</span>
                </button>
              </div>

              {/* Mode 1: Phone Registration Flow */}
              {mode === "phone" && (
            <div className="mt-6">
              <AnimatePresence mode="wait">
                {step === "details" ? (
                  <motion.form
                    key="reg-details"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    onSubmit={handleSendRegistrationOtp}
                    className="space-y-5"
                  >
                    <Input
                      id="register-name"
                      label={t("fullName")}
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Ramesh Patel"
                      required
                    />

                    <div>
                      <label className="text-sm font-semibold text-ink" htmlFor="register-phone">
                        {t("phoneNumber")}
                      </label>
                      <div className="mt-1 flex rounded-md border border-line bg-canvas shadow-xs focus-within:border-farmer-600 focus-within:ring-1 focus-within:ring-farmer-600">
                        <span className="flex items-center px-3 text-sm font-semibold text-muted border-r border-line bg-surface select-none">
                          🇮🇳 +91
                        </span>
                        <input
                          id="register-phone"
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
                        {t("smsOwnershipVerification")}
                      </p>
                    </div>

                    <div className="grid gap-5 sm:grid-cols-2">
                      <div className="space-y-2">
                        <label className="flex items-center gap-2 text-sm font-semibold text-ink" htmlFor="register-language">
                          <Globe size={15} className="text-farmer-700 dark:text-farmer-300" />
                          <span>{t("language")}</span>
                        </label>
                        <Select
                          id="register-language"
                          value={language}
                          onChange={(val) => setLanguage(val)}
                          options={[
                            { value: "English", label: "English" },
                            { value: "Hindi", label: "हिन्दी (Hindi)" },
                            { value: "Gujarati", label: "ગુજરાતી (Gujarati)" },
                          ]}
                        />
                      </div>
                      <Input
                        id="register-location"
                        label={t("location")}
                        type="text"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        placeholder="Anand, Gujarat"
                        required
                      />
                    </div>

                    <Button type="submit" disabled={loading} className="mt-2 w-full">
                      <Phone size={17} />
                      {loading ? t("sendingOtp") : t("sendOtp")}
                      <ArrowRight size={15} className="ml-1" />
                    </Button>
                  </motion.form>
                ) : (
                  <motion.form
                    key="reg-otp"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    onSubmit={handleVerifyRegistrationOtp}
                    className="space-y-5"
                  >
                    <div className="rounded-lg border border-farmer-200 bg-farmer-50/60 p-4 dark:border-farmer-900/50 dark:bg-farmer-950/40">
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <CheckCircle2 size={16} className="text-farmer-600 dark:text-farmer-400" />
                            <p className="text-xs font-semibold text-farmer-800 dark:text-farmer-300">
                              {t("phoneVerification")}
                            </p>
                          </div>
                          <p className="text-sm font-bold text-ink">{formatPhoneDisplay(phone)}</p>
                        </div>
                        <button
                          type="button"
                          onClick={() => {
                            setStep("details");
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
                        id="register-otp"
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
                      <UserPlus size={17} />
                      {loading ? t("verifying") : t("completeRegistration")}
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
                        onClick={handleResendRegistrationOtp}
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

          {/* Mode 2: Traditional Email Registration */}
          {mode === "email" && (
            <form onSubmit={handleEmailSubmit} className="mt-6 space-y-5">
              <Input
                id="register-name"
                label={t("fullName")}
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ramesh Patel"
                required
              />
              <Input
                id="register-email"
                label={t("emailAddress")}
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="farmer@example.com"
                required
              />
              <Input
                id="register-password"
                label={t("password")}
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
              <div className="grid gap-5 sm:grid-cols-2">
                <div className="space-y-2">
                  <label className="flex items-center gap-2 text-sm font-semibold text-ink" htmlFor="register-language-email">
                    <Globe size={15} className="text-farmer-700 dark:text-farmer-300" />
                    <span>{t("language")}</span>
                  </label>
                  <Select
                    id="register-language-email"
                    value={language}
                    onChange={(val) => setLanguage(val)}
                    options={[
                      { value: "English", label: "English" },
                      { value: "Hindi", label: "हिन्दी (Hindi)" },
                      { value: "Gujarati", label: "ગુજરાતી (Gujarati)" },
                    ]}
                  />
                </div>
                <Input
                  id="register-location-email"
                  label={t("location")}
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Anand, Gujarat"
                  required
                />
              </div>

              <Button type="submit" disabled={loading} className="mt-2 w-full">
                <UserPlus size={17} />
                {loading ? t("creatingAccount") : t("registerAndContinue")}
              </Button>
            </form>
          )}
          </>
          )}

          <div className="mt-8 text-center text-sm text-muted">
            {t("alreadyHaveAccount")}{" "}
            <Link className="font-semibold text-farmer-700 dark:text-farmer-300 underline" to="/auth/login">
              {t("signIn")}
            </Link>
          </div>
        </motion.div>
      </div>

      <div className="relative hidden min-h-[26rem] items-end overflow-hidden bg-farmer-950 bg-[url('https://images.unsplash.com/photo-1500937386664-56d1dfef3854?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center p-10 lg:flex lg:p-16 border-l border-line">
        <div className="absolute inset-0 bg-farmer-950/70" />
        <div className="relative z-10 text-white space-y-3">
          <h2 className="max-w-xl font-display text-3xl leading-tight">{t("registerBannerTitle")}</h2>
          <p className="text-xs font-semibold uppercase tracking-wider text-farmer-200">{t("loginBannerSubtitle")}</p>
        </div>
      </div>
    </div>
  );
}
