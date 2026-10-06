import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { UserPlus, Sprout, Globe } from "../components/icons";
import { motion } from "motion/react";
import { Button, Input, Select } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { getDefaultRouteForRole } from "../lib/routes";
import ThemeToggle from "../components/ThemeToggle";
import LanguageToggle from "../components/LanguageToggle";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [language, setLanguage] = useState("English");
  const [location, setLocation] = useState("");
  
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signUp, t } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const newUser = await signUp({ name, email, phone, password, language, location });
      navigate(getDefaultRouteForRole(newUser.role), { replace: true });
    } catch (err: any) {
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

          {error && <div className="mt-6 rounded-sm border border-red-100 bg-red-50 p-3 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">{error}</div>}

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <Input id="register-name" label={t("fullName")} type="text" value={name} onChange={(e) => setName(e.target.value)} required />
            <div className="grid gap-5 sm:grid-cols-2">
              <Input id="register-email" label={t("emailAddress")} type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
              <Input id="register-phone" label={t("phoneNumber")} type="text" value={phone} onChange={(e) => setPhone(e.target.value)} required />
            </div>
            <Input id="register-password" label={t("password")} type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
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
              <Input id="register-location" label={t("location")} type="text" value={location} onChange={(e) => setLocation(e.target.value)} required />
            </div>

            <Button type="submit" disabled={loading} className="mt-2 w-full">
              <UserPlus size={17} />
              {loading ? t("creatingAccount") : t("registerAndContinue")}
            </Button>
          </form>

          <div className="mt-8 text-center text-sm text-muted">
            {t("alreadyHaveAccount")} <Link className="font-semibold text-farmer-700 dark:text-farmer-300 underline" to="/auth/login">{t("signIn")}</Link>
          </div>
        </motion.div>
      </div>
      <div className="relative hidden min-h-[26rem] items-end overflow-hidden bg-farmer-950 bg-[url('https://images.unsplash.com/photo-1595841696650-622839b207ee?q=80&w=2069&auto=format&fit=crop')] bg-cover bg-center p-10 lg:flex lg:p-16 border-l border-line">
        <div className="absolute inset-0 bg-farmer-950/70" />
        <div className="relative z-10 text-white space-y-3">
          <h2 className="max-w-xl font-display text-3xl leading-tight">{t("registerBannerTitle")}</h2>
          <p className="text-xs font-semibold uppercase tracking-wider text-farmer-200">{t("loginBannerSubtitle")}</p>
        </div>
      </div>
    </div>
  );
}
