import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  datasetSummary as getDatasetSummary,
  exportDataset,
  purgeBlobs,
  purgeDatabase,
  readAdminConfig,
  updateAdminConfig,
} from "../api/admin";
import { changePassword } from "../api/auth";
import { 
  AlertTriangle, 
  Trash2, 
  DownloadCloud, 
  Settings as SettingsIcon,
  Globe,
  Sliders,
  CheckCircle2,
  Database,
  Cloud,
  Sprout,
  FolderArchive,
  Sun,
  KeyRound,
  ShieldCheck,
  User,
  Phone,
  Mail
} from "../components/icons";
import { motion } from "motion/react";
import { Button, Card, Input, Select } from "../components/ui";
import ThemeToggle from "../components/ThemeToggle";
import { normalizePhoneNumber, isValidPhoneNumber } from "../lib/phone";

export default function SettingsPage() {
  const {
    user,
    token,
    language,
    units,
    setLanguage,
    setUnits,
    updateUserProfile,
    requestEmailUpdate,
    resendVerificationEmail,
    requestPhoneUpdate,
    verifyPhoneUpdate,
    sendPhoneOtp,
    t,
  } = useAuth();
  const queryClient = useQueryClient();
  const isAdmin = user?.role === "admin";
  
  // Account Profile (Full Name)
  const [profileName, setProfileName] = useState(user?.name || "");
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState("");
  const [profileSuccess, setProfileSuccess] = useState(false);

  // Mobile Phone Linking / Verification
  const [profilePhone, setProfilePhone] = useState(user?.phone || "");
  const [phoneStep, setPhoneStep] = useState<"idle" | "otp">("idle");
  const [phoneOtp, setPhoneOtp] = useState("");
  const [phoneCountdown, setPhoneCountdown] = useState(0);
  const [phoneLoading, setPhoneLoading] = useState(false);
  const [phoneError, setPhoneError] = useState("");
  const [phoneSuccess, setPhoneSuccess] = useState("");

  // Email Linking / Update
  const [profileEmail, setProfileEmail] = useState(user?.email || user?.pending_email || "");
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailError, setEmailError] = useState("");
  const [emailSuccess, setEmailSuccess] = useState("");

  useEffect(() => {
    if (user) {
      setProfileName(user.name || "");
      setProfilePhone(user.phone || "");
      setProfileEmail(user.pending_email || user.email || "");
    }
  }, [user]);

  // Phone Resend Countdown Timer
  useEffect(() => {
    if (phoneCountdown > 0) {
      const timer = setTimeout(() => setPhoneCountdown((c) => c - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [phoneCountdown]);

  const handleUpdateName = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileError("");
    setProfileSuccess(false);

    const trimmedName = profileName.trim();
    if (!trimmedName || trimmedName.length < 2 || trimmedName.length > 100) {
      setProfileError(t("settingsNameInvalid"));
      return;
    }

    setProfileLoading(true);
    try {
      await updateUserProfile({
        name: trimmedName,
      });
      setProfileSuccess(true);
      setTimeout(() => setProfileSuccess(false), 4000);
    } catch (err: any) {
      setProfileError(err?.message || t("settingsNameUpdateFailed"));
    } finally {
      setProfileLoading(false);
    }
  };

  const handleSendPhoneOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setPhoneError("");
    setPhoneSuccess("");

    const trimmed = profilePhone.trim();
    if (!trimmed) {
      setPhoneError(t("settingsPhoneRequired"));
      return;
    }
    if (!isValidPhoneNumber(trimmed)) {
      setPhoneError(t("phoneInvalid"));
      return;
    }

    const normalized = normalizePhoneNumber(trimmed);
    if (user?.phone && normalizePhoneNumber(user.phone) === normalized) {
      setPhoneError(t("settingsPhoneAlreadyLinked"));
      return;
    }

    setPhoneLoading(true);
    try {
      // 1. Verify phone is available and not already used by another account
      await requestPhoneUpdate(normalized);

      // 2. Dispatch SMS verification OTP
      await sendPhoneOtp(normalized, false);

      setPhoneStep("otp");
      setPhoneCountdown(60);
      setPhoneSuccess(`${t("settingsPhoneCodeSent")} ${normalized}.`);
    } catch (err: any) {
      setPhoneError(err?.message || t("settingsPhoneCodeFailed"));
    } finally {
      setPhoneLoading(false);
    }
  };

  const handleVerifyPhoneOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setPhoneError("");
    setPhoneSuccess("");

    const cleanCode = phoneOtp.trim();
    if (cleanCode.length !== 6 || !/^\d{6}$/.test(cleanCode)) {
      setPhoneError(t("settingsPhoneCodeIncomplete"));
      return;
    }

    const normalized = normalizePhoneNumber(profilePhone.trim());
    setPhoneLoading(true);
    try {
      await verifyPhoneUpdate(normalized, cleanCode);
      setPhoneStep("idle");
      setPhoneOtp("");
      setPhoneSuccess(t("phoneLinkedSuccess"));
      setTimeout(() => setPhoneSuccess(""), 10000);
    } catch (err: any) {
      setPhoneError(err?.message || t("settingsPhoneCodeInvalid"));
    } finally {
      setPhoneLoading(false);
    }
  };

  const handleCancelPhoneOtp = () => {
    setPhoneStep("idle");
    setPhoneOtp("");
    setPhoneError("");
    setProfilePhone(user?.phone || "");
  };

  const handleResendPhoneOtp = async () => {
    if (phoneCountdown > 0 || phoneLoading) return;
    setPhoneError("");
    setPhoneSuccess("");
    const normalized = normalizePhoneNumber(profilePhone.trim());
    setPhoneLoading(true);
    try {
      await sendPhoneOtp(normalized, false);
      setPhoneCountdown(60);
      setPhoneSuccess(`${t("settingsPhoneCodeResent")} ${normalized}.`);
    } catch (err: any) {
      setPhoneError(err?.message || t("settingsPhoneResendFailed"));
    } finally {
      setPhoneLoading(false);
    }
  };

  const handleUpdateEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailError("");
    setEmailSuccess("");

    const trimmed = profileEmail.trim();
    if (!trimmed || !trimmed.includes("@") || !trimmed.includes(".")) {
      setEmailError(t("settingsEmailInvalid"));
      return;
    }

    if (user?.email && user.email.toLowerCase() === trimmed.toLowerCase() && user.is_email_verified) {
      setEmailError(t("settingsEmailAlreadyVerified"));
      return;
    }

    setEmailLoading(true);
    try {
      const res = await requestEmailUpdate(trimmed);
      setEmailSuccess(res.message || `${t("settingsEmailLinkSent")} ${trimmed}.`);
      setTimeout(() => setEmailSuccess(""), 10000);
    } catch (err: any) {
      setEmailError(err.message || t("settingsEmailLinkFailed"));
    } finally {
      setEmailLoading(false);
    }
  };

  const handleResendVerification = async () => {
    const target = user?.pending_email || profileEmail.trim();
    if (!target) return;
    setEmailError("");
    setEmailSuccess("");
    setEmailLoading(true);
    try {
      const res = await resendVerificationEmail(target);
      setEmailSuccess(res.message || `${t("settingsEmailLinkResent")} ${target}.`);
      setTimeout(() => setEmailSuccess(""), 8000);
    } catch (err: any) {
      setEmailError(err.message || t("settingsEmailResendFailed"));
    } finally {
      setEmailLoading(false);
    }
  };

  // General
  const [lang, setLang] = useState(language);
  const [unitPref, setUnitPref] = useState(units);
  const [prefSaved, setPrefSaved] = useState(false);

  // Security / Password
  const [currentPwd, setCurrentPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [pwdLoading, setPwdLoading] = useState(false);
  const [pwdError, setPwdError] = useState("");
  const [pwdSuccess, setPwdSuccess] = useState(false);

  // Danger Zone
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  // MLOps
  const [exportFilters, setExportFilters] = useState({ expert: true, farmer: true });
  const [exportCrop, setExportCrop] = useState("All Crops (Tomato, Cotton, Potato)");
  const [exportFormat, setExportFormat] = useState("PyTorch Folder");
  const [exportImage, setExportImage] = useState("preprocessed");
  const [splitTrain, setSplitTrain] = useState(70);
  const [splitVal, setSplitVal] = useState(15);
  const [isExporting, setIsExporting] = useState(false);

  // Config
  const [routingThresh, setRoutingThresh] = useState(75);
  const [expertThresh, setExpertThresh] = useState(70);
  const [configSaved, setConfigSaved] = useState(false);

  // Data Fetching
  const { data: configData } = useQuery({
    queryKey: ["adminConfig"],
    queryFn: () => readAdminConfig(token!),
    enabled: isAdmin,
  });

  const { data: datasetSummary } = useQuery({
    queryKey: ["datasetSummary"],
    queryFn: () => getDatasetSummary(token!),
    enabled: isAdmin,
  });

  useEffect(() => {
    if (configData) {
      setRoutingThresh(Math.round(configData.crop_routing_threshold * 100));
      setExpertThresh(Math.round(configData.expert_escalation_cutoff * 100));
    }
  }, [configData]);

  const updateConfig = useMutation({
    mutationFn: async () => updateAdminConfig(token!, {
        crop_routing_threshold: routingThresh / 100,
        expert_escalation_cutoff: expertThresh / 100,
    }),
    onSuccess: () => {
      setConfigSaved(true);
      setTimeout(() => setConfigSaved(false), 3000);
      queryClient.invalidateQueries({ queryKey: ["adminConfig"] });
    }
  });

  const handleDeleteData = async () => {
    if (deleteConfirmText !== "DELETE") return;
    setIsDeleting(true);
    try {
      await purgeDatabase(token!);
      alert(t("databaseWiped"));
      setShowDeleteModal(false);
      window.location.reload();
    } catch (err: any) {
      alert(`${t("operationFailed")}: ${err.message}`);
    } finally {
      setIsDeleting(false);
    }
  };

  const handlePurgeBlobs = async () => {
    if (!confirm(t("confirmDeleteOrphanedBlobs"))) return;
    try {
      const res = await purgeBlobs(token!);
      const localCount = res.local_deleted ?? 0;
      const cloudCount = res.supabase_deleted ?? res.cloud_deleted ?? res.s3_deleted ?? 0;
      alert(
        t("orphanedBlobsDeleted")
          .replace("{deleted}", String(res.deleted_files ?? (localCount + cloudCount)))
          .replace("{local}", String(localCount))
          .replace("{cloud}", String(cloudCount)),
      );
    } catch (err: any) {
      alert(`${t("operationFailed")}: ${err.message}`);
    }
  };

  const handleExportMLOps = async () => {
    setIsExporting(true);
    try {
      const payload = {
        filters: exportFilters,
        split: { train: splitTrain, val: splitVal, test: 100 - splitTrain - splitVal },
        format: exportFormat,
        imageTarget: exportImage
      };
      const blob = await exportDataset(token!, {
        filters: { expert: exportFilters.expert, farmer: exportFilters.farmer, crop: exportCrop },
        split: payload.split,
        format: exportFormat === "JSON Manifest" ? "JSON Manifest" : "PyTorch Folder",
        imageTarget: exportImage as "raw" | "preprocessed",
      });

      // If backend uploaded to Supabase/S3, it returns a JSON payload with signed download_url
      if (blob.type.includes("json")) {
        const text = await blob.text();
        try {
          const json = JSON.parse(text);
          if (json.download_url) {
            const a = document.createElement("a");
            a.href = json.download_url;
            a.target = "_blank";
            a.rel = "noopener noreferrer";
            a.download = `dataset_export_${json.export_id || "bundle"}.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            return;
          }
        } catch {
          // Fall through to regular blob handling
        }
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "dataset_export.zip";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error(err);
      alert(err?.message || t("exportError"));
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="flex items-center gap-3 font-display text-3xl text-ink sm:text-4xl"><SettingsIcon size={28} className="text-farmer-700 dark:text-farmer-300" /> {t("settings")}</h1>
        <p className="mt-3 max-w-3xl leading-7 text-muted">{t("settingsSubtitle")}</p>
      </div>

      {/* Account Information / Mobile Number */}
      <Card>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="flex items-center gap-2 font-display text-xl text-ink">
              <User size={20} className="text-farmer-700 dark:text-farmer-300" />
              <span>{t("accountInformation")}</span>
            </h3>
            <p className="mt-1 text-sm text-muted">
              {t("accountInformationDesc")}
            </p>
          </div>
          <div>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-canvas px-3 py-1 text-xs font-semibold uppercase tracking-wider text-ink">
              <ShieldCheck size={14} className="text-farmer-600 dark:text-farmer-400" />
              <span>
                {user?.role === "admin"
                  ? t("roleAdmin")
                  : user?.role === "expert"
                  ? t("roleExpert")
                  : t("roleFarmer")}
              </span>
            </span>
          </div>
        </div>

        {profileError && (
          <div className="mt-4 rounded-sm border border-red-200 bg-red-50 p-3 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
            {profileError}
          </div>
        )}

        <form onSubmit={handleUpdateName} className="mt-6 space-y-4">
          <div className="max-w-md">
            <Input
              label={t("fullName")}
              value={profileName}
              onChange={(e) => setProfileName(e.target.value)}
              placeholder={t("enterFullName")}
              leadingIcon={<User size={16} />}
            />
          </div>

          <div className="flex flex-wrap items-center gap-3 pt-1">
            <Button type="submit" disabled={profileLoading} className="flex items-center gap-2">
              <User size={15} />
              <span>{profileLoading ? t("updating") : t("saveProfileChanges")}</span>
            </Button>
            {profileSuccess && (
              <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-farmer-700 dark:text-farmer-300 animate-fadeIn">
                <CheckCircle2 size={16} />
                <span>{t("profileUpdatedSuccess")}</span>
              </span>
            )}
          </div>
        </form>

        {/* Mobile Phone & Authentication Section */}
        <div className="my-6 border-t border-line" />

        <div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h4 className="flex items-center gap-2 font-display text-lg text-ink">
                <Phone size={18} className="text-farmer-700 dark:text-farmer-300" />
                <span>{t("mobilePhoneAuth")}</span>
              </h4>
              <p className="mt-1 text-sm text-muted">
                {t("mobilePhoneAuthDesc")}
              </p>
            </div>

            <div>
              {user?.phone ? (
                <span className="inline-flex items-center gap-1.5 rounded-full border border-green-200 bg-green-50 px-3 py-1 text-xs font-semibold text-green-700 dark:border-green-800 dark:bg-green-950/40 dark:text-green-300">
                  <CheckCircle2 size={14} />
                  <span>{t("phoneLinked")}: {user.phone}</span>
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-canvas px-3 py-1 text-xs font-medium text-muted">
                  <span>{t("noPhoneLinked")}</span>
                </span>
              )}
            </div>
          </div>

          {phoneError && (
            <div className="mt-4 rounded-sm border border-red-200 bg-red-50 p-3 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
              {phoneError}
            </div>
          )}

          {phoneSuccess && (
            <div className="mt-4 rounded-sm border border-green-200 bg-green-50 p-3 text-sm text-farmer-800 dark:border-green-900/50 dark:bg-green-950/40 dark:text-green-300 flex items-center gap-2">
              <CheckCircle2 size={16} className="text-farmer-700 dark:text-green-400 shrink-0" />
              <span>{phoneSuccess}</span>
            </div>
          )}

          {phoneStep === "idle" ? (
            <form onSubmit={handleSendPhoneOtp} className="mt-5 space-y-4">
              <div className="max-w-md">
                <Input
                  label={t("mobilePhone")}
                  type="tel"
                  value={profilePhone}
                  onChange={(e) => setProfilePhone(e.target.value)}
                  placeholder={t("phoneExamplePlaceholder")}
                  leadingIcon={<Phone size={16} />}
                />
                <span className="mt-1 block text-xs text-muted">
                  {t("phoneHelp")}
                </span>
              </div>

              <div className="flex items-center gap-3 pt-1">
                <Button type="submit" disabled={phoneLoading} className="flex items-center gap-2">
                  <Phone size={15} />
                  <span>
                    {phoneLoading
                      ? t("sendingCode")
                      : user?.phone
                      ? t("changeMobilePhone")
                      : t("verifyAndLinkPhone")}
                  </span>
                </Button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleVerifyPhoneOtp} className="mt-5 space-y-4">
              <div className="rounded-lg border border-farmer-200/80 bg-farmer-50/50 p-4 text-xs text-farmer-900 dark:border-farmer-900/40 dark:bg-farmer-950/30 dark:text-farmer-200">
                {t("verificationCodeSent")} <strong>{profilePhone}</strong>. {t("phoneVerifyHelp")}
              </div>

              <div className="max-w-xs">
                <Input
                  label={t("otpCodeInputLabel")}
                  type="text"
                  maxLength={6}
                  value={phoneOtp}
                  onChange={(e) => setPhoneOtp(e.target.value.replace(/\D/g, ""))}
                  placeholder="123456"
                  autoFocus
                />
              </div>

              <div className="flex flex-wrap items-center gap-3 pt-1">
                <Button
                  type="submit"
                  disabled={phoneLoading || phoneOtp.trim().length !== 6}
                  className="flex items-center gap-2"
                >
                  <CheckCircle2 size={15} />
                  <span>{phoneLoading ? t("verifying") : t("confirmAndLinkPhone")}</span>
                </Button>

                <Button
                  type="button"
                  variant="secondary"
                  disabled={phoneLoading || phoneCountdown > 0}
                  onClick={handleResendPhoneOtp}
                >
                  {phoneCountdown > 0 ? `${t("resendCodeIn")} ${phoneCountdown}s` : t("resendCode")}
                </Button>

                <Button
                  type="button"
                  variant="ghost"
                  disabled={phoneLoading}
                  onClick={handleCancelPhoneOtp}
                >
                  {t("cancel")}
                </Button>
              </div>
            </form>
          )}
        </div>

        {/* Email Address Section */}
        <div className="my-6 border-t border-line" />

        <div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h4 className="flex items-center gap-2 font-display text-lg text-ink">
                <Mail size={18} className="text-farmer-700 dark:text-farmer-300" />
                <span>{t("emailAuthentication")}</span>
              </h4>
              <p className="mt-1 text-sm text-muted">
                {t("emailAuthenticationDesc")}
              </p>
            </div>

            <div>
              {user?.is_email_verified && user?.email ? (
                <span className="inline-flex items-center gap-1.5 rounded-full border border-green-200 bg-green-50 px-3 py-1 text-xs font-semibold text-green-700 dark:border-green-800 dark:bg-green-950/40 dark:text-green-300">
                  <CheckCircle2 size={14} />
                  <span>{t("verified")}</span>
                </span>
              ) : user?.pending_email ? (
                <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-300">
                  <AlertTriangle size={14} />
                  <span>{t("emailVerificationPending")}</span>
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-canvas px-3 py-1 text-xs font-medium text-muted">
                  <span>{t("noEmailLinked")}</span>
                </span>
              )}
            </div>
          </div>

          {emailError && (
            <div className="mt-4 rounded-sm border border-red-200 bg-red-50 p-3 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
              {emailError}
            </div>
          )}

          {emailSuccess && (
            <div className="mt-4 rounded-sm border border-green-200 bg-green-50 p-3 text-sm text-farmer-800 dark:border-green-900/50 dark:bg-green-950/40 dark:text-green-300 flex items-center gap-2">
              <CheckCircle2 size={16} className="text-farmer-700 dark:text-green-400 shrink-0" />
              <span>{emailSuccess}</span>
            </div>
          )}

          {user?.pending_email && (
            <div className="mt-4 rounded-lg border border-amber-200/80 bg-amber-50/70 p-4 text-xs text-amber-900 dark:border-amber-900/40 dark:bg-amber-950/30 dark:text-amber-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <strong>{t("pendingVerification")}:</strong> {t("pendingVerificationLinkSent")}{" "}
                <span className="underline font-semibold">{user.pending_email}</span>. {t("completeEmailVerification")}
              </div>
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={handleResendVerification}
                disabled={emailLoading}
                className="shrink-0"
              >
                {emailLoading ? t("sending") : t("resendLink")}
              </Button>
            </div>
          )}

          <form onSubmit={handleUpdateEmail} className="mt-5 space-y-4">
            <div className="max-w-md">
              <Input
                label={t("emailAddress")}
                type="email"
                value={profileEmail}
                onChange={(e) => setProfileEmail(e.target.value)}
                placeholder={t("emailExamplePlaceholder")}
                leadingIcon={<Mail size={16} />}
              />
            </div>

            <div className="flex items-center gap-3 pt-1">
              <Button type="submit" disabled={emailLoading} className="flex items-center gap-2">
                <Mail size={15} />
                <span>
                  {emailLoading
                    ? t("sending")
                    : user?.email
                    ? t("updateEmailAddress")
                    : t("sendVerificationLink")}
                </span>
              </Button>
            </div>
          </form>
        </div>
      </Card>

      <Card>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="flex items-center gap-2 font-display text-xl text-ink">
              <Sun size={20} className="text-farmer-700 dark:text-farmer-300" />
              <span>{t("appearanceTheme")}</span>
            </h3>
            <p className="mt-2 text-sm text-muted">
              {t("appearanceThemeDesc")}
            </p>
          </div>
          <ThemeToggle variant="segmented" />
        </div>
      </Card>

      <Card>
        <h3 className="flex items-center gap-2 font-display text-xl text-ink"><Globe size={20} className="text-farmer-700 dark:text-farmer-300" /> {t("languagePreferences")}</h3>
        <p className="mt-2 text-sm text-muted">{t("languageSubtitle")}</p>
        
        <div className="mt-6 grid gap-5 sm:grid-cols-2">
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-ink" htmlFor="settings-language">
              <Globe size={15} className="text-farmer-700 dark:text-farmer-300" />
              <span>{t("interfaceLanguage")}</span>
            </label>
            <Select 
              id="settings-language"
              value={lang} 
              onChange={(val) => setLang(val as any)}
              options={[
                { value: "English", label: "English" },
                { value: "Gujarati", label: "ગુજરાતી (Gujarati)" },
                { value: "Hindi", label: "हिन्दी (Hindi)" },
              ]}
            />
          </div>
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-ink" htmlFor="settings-units">
              <Sliders size={15} className="text-farmer-700 dark:text-farmer-300" />
              <span>{t("units")}</span>
            </label>
            <Select 
              id="settings-units"
              value={unitPref} 
              onChange={(val) => setUnitPref(val as any)}
              options={[
                { value: "Metric", label: "Metric (ha, °C, km/h)" },
                { value: "Imperial", label: "Imperial (acres, °F, mph)" },
              ]}
            />
          </div>
        </div>

        <div className="mt-6 flex items-center gap-3">
          <Button 
            onClick={async () => {
              await setLanguage(lang as any);
              setUnits(unitPref as any);
              setPrefSaved(true);
              setTimeout(() => setPrefSaved(false), 3000);
            }}
          >
            {t("save")}
          </Button>
          {prefSaved && <span className="inline-flex items-center gap-1 text-sm font-semibold text-farmer-700 dark:text-farmer-300"><CheckCircle2 size={16} /> {t("savedSuccess")}</span>}
        </div>
      </Card>

      {/* Security & Password */}
      <Card>
        <h3 className="flex items-center gap-2 font-display text-xl text-ink">
          <ShieldCheck size={20} className="text-farmer-700 dark:text-farmer-300" /> {t("securitySettings")}
        </h3>
        <p className="mt-2 text-sm text-muted">{t("securitySubtitle")}</p>

        {pwdError && (
          <div className="mt-4 rounded-sm border border-red-100 bg-red-50 p-3 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
            {pwdError}
          </div>
        )}

        <form 
          onSubmit={async (e) => {
            e.preventDefault();
            setPwdError("");
            setPwdSuccess(false);

            if (newPwd.length < 8) {
              setPwdError(t("passwordTooShort"));
              return;
            }
            if (newPwd !== confirmPwd) {
              setPwdError(t("passwordsDoNotMatch"));
              return;
            }

            setPwdLoading(true);
            try {
              await changePassword(currentPwd, newPwd, token!);
              setPwdSuccess(true);
              setCurrentPwd("");
              setNewPwd("");
              setConfirmPwd("");
              setTimeout(() => setPwdSuccess(false), 4000);
            } catch (err: any) {
              setPwdError(err.message || t("settingsPasswordChangeFailed"));
            } finally {
              setPwdLoading(false);
            }
          }} 
          className="mt-6 space-y-4"
        >
          <div className="grid gap-4 sm:grid-cols-3">
            <Input
              id="settings-current-pwd"
              label={t("currentPassword")}
              type="password"
              value={currentPwd}
              onChange={(e) => setCurrentPwd(e.target.value)}
              placeholder={t("passwordPlaceholder")}
              required
            />
            <Input
              id="settings-new-pwd"
              label={t("newPassword")}
              type="password"
              value={newPwd}
              onChange={(e) => setNewPwd(e.target.value)}
              placeholder={t("passwordPlaceholder")}
              required
            />
            <Input
              id="settings-confirm-pwd"
              label={t("confirmNewPassword")}
              type="password"
              value={confirmPwd}
              onChange={(e) => setConfirmPwd(e.target.value)}
              placeholder={t("passwordPlaceholder")}
              required
            />
          </div>

          <div className="mt-4 flex items-center gap-3">
            <Button type="submit" disabled={pwdLoading}>
              <KeyRound size={16} />
              {pwdLoading ? t("updatingPassword") : t("changePassword")}
            </Button>
            {pwdSuccess && (
              <span className="inline-flex items-center gap-1 text-sm font-semibold text-farmer-700 dark:text-farmer-300">
                <CheckCircle2 size={16} /> {t("passwordChangedSuccess")}
              </span>
            )}
          </div>
        </form>
      </Card>

      {isAdmin && (
        <>
          <div className="rounded-sm border border-line bg-surface p-5 sm:p-6">
            <h3 className="flex items-center gap-2 font-display text-lg text-ink"><Database size={18} className="text-farmer-700 dark:text-farmer-300" /> {t("mlopsEngine")}</h3>
            <p className="mt-2 text-sm text-muted">{t("mlopsSubtitle")}</p>
            
            <div className="mt-6 rounded-sm bg-canvas p-4">
              <strong className="text-sm text-ink">{t("groundTruthInclusion")}</strong>
              <div className="mt-3 flex flex-col gap-3 text-sm text-muted sm:flex-row sm:gap-6">
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked={exportFilters.expert} onChange={e => setExportFilters(p => ({...p, expert: e.target.checked}))} />
                  {t("expertOverriddenCases")} ({datasetSummary?.expert_overridden || 0})
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked={exportFilters.farmer} onChange={e => setExportFilters(p => ({...p, farmer: e.target.checked}))} />
                  {t("confirmedFarmerFeedback")} ({datasetSummary?.farmer_confirmed || 0})
                </label>
              </div>
            </div>

            <div className="mt-6 grid gap-5 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-semibold text-ink" htmlFor="export-crop">
                  <Sprout size={15} className="text-expert-700 dark:text-cyan-400" />
                  <span>{t("targetCrop")}</span>
                </label>
                <Select 
                  id="export-crop"
                  value={exportCrop} 
                  onChange={(val) => setExportCrop(val)}
                  theme="expert"
                  options={[
                    { value: "All Crops (Tomato, Cotton, Potato)", label: "All Crops (Tomato, Cotton, Potato)" },
                    { value: "Cotton", label: "Cotton", icon: <Sprout size={14} className="text-expert-600 dark:text-cyan-400 shrink-0" /> },
                    { value: "Tomato", label: "Tomato", icon: <Sprout size={14} className="text-expert-600 dark:text-cyan-400 shrink-0" /> },
                  ]}
                />
              </div>
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-semibold text-ink" htmlFor="export-format">
                  <FolderArchive size={15} className="text-expert-700 dark:text-cyan-400" />
                  <span>{t("archiveFormat")}</span>
                </label>
                <Select 
                  id="export-format"
                  value={exportFormat} 
                  onChange={(val) => setExportFormat(val)}
                  theme="expert"
                  options={[
                    { value: "PyTorch Folder", label: "PyTorch Folder", sublabel: "Class-based folder structure" },
                    { value: "COCO Bounding Boxes", label: "COCO Bounding Boxes", sublabel: "instances.json format" },
                    { value: "JSON Manifest", label: "JSON Manifest", sublabel: "Full telemetry & predictions" },
                  ]}
                />
              </div>
            </div>

            <div className="mt-6">
              <label className="text-sm font-semibold text-ink">{t("imageTarget")}</label>
              <div className="mt-3 flex flex-col gap-3 text-sm text-muted sm:flex-row sm:gap-6">
                <label className="flex items-center gap-2">
                  <input type="radio" name="imgTarget" checked={exportImage === "preprocessed"} onChange={() => setExportImage("preprocessed")} />
                  {t("preprocessedImg")}
                </label>
                <label className="flex items-center gap-2">
                  <input type="radio" name="imgTarget" checked={exportImage === "raw"} onChange={() => setExportImage("raw")} />
                  {t("rawImg")}
                </label>
              </div>
            </div>

            <div className="mt-6">
              <label className="text-sm font-semibold text-ink">{t("datasetSplit")}: {t("train")} {splitTrain}% / {t("val")} {splitVal}% / {t("test")} {100 - splitTrain - splitVal}%</label>
              <input className="mt-4 w-full accent-farmer-700 dark:accent-farmer-400" type="range" min="50" max="90" value={splitTrain} onChange={e => setSplitTrain(Number(e.target.value))} />
            </div>

            <div className="mt-7 flex flex-wrap gap-3">
              <Button className="bg-expert-700 hover:bg-expert-500 dark:bg-cyan-700 dark:hover:bg-cyan-600 dark:text-white" onClick={handleExportMLOps} disabled={isExporting}>
                <DownloadCloud size={18} /> {isExporting ? t("packaging") : t("exportArchive")}
              </Button>
              <Button variant="secondary" className="border-expert-500 text-expert-700 dark:border-cyan-600 dark:text-cyan-300 dark:hover:bg-cyan-950/40" disabled={isExporting}>
                <Cloud size={18} /> {t("syncS3")}
              </Button>
            </div>
          </div>

          <div className="rounded-sm border border-line bg-surface p-5 sm:p-6">
            <h3 className="flex items-center gap-2 font-display text-lg text-ink"><Sliders size={18} className="text-farmer-700 dark:text-farmer-300" /> {t("decisionThresholds")}</h3>
            <p className="mt-2 text-sm text-muted">{t("thresholdsSubtitle")}</p>
            
            <div className="mt-6">
              <label className="text-sm font-semibold text-ink">{t("cropRoutingConfMin")}: {routingThresh}%</label>
              <input className="mt-3 w-full accent-farmer-700 dark:accent-farmer-400" type="range" min="50" max="95" value={routingThresh} onChange={e => setRoutingThresh(Number(e.target.value))} />
            </div>
            
            <div className="mt-6">
              <label className="text-sm font-semibold text-ink">{t("expertEscalationCutoff")}: {expertThresh}%</label>
              <input className="mt-3 w-full accent-farmer-700 dark:accent-farmer-400" type="range" min="50" max="95" value={expertThresh} onChange={e => setExpertThresh(Number(e.target.value))} />
            </div>

            <Button className="mt-7" onClick={() => updateConfig.mutate()} disabled={updateConfig.isPending}>
              {updateConfig.isPending ? t("saving") : t("saveConfigParams")}
            </Button>
            {configSaved && <span className="ml-4 inline-flex items-center gap-1 text-sm font-semibold text-farmer-700 dark:text-farmer-300"><CheckCircle2 size={16} /> {t("saved")}</span>}
          </div>

          <div className="rounded-sm border border-red-300 bg-red-50 dark:border-red-900/60 dark:bg-red-950/30 p-5 sm:p-6">
            <h3 className="flex items-center gap-2 font-display text-lg text-danger dark:text-red-400"><AlertTriangle size={18} /> {t("dangerZone")}</h3>
            
            <div className="mt-6 flex flex-wrap gap-3">
              <Button type="button" variant="danger" onClick={() => setShowDeleteModal(true)}>
                <Trash2 size={16} /> {t("clearPredictions")}
              </Button>
              <Button type="button" variant="secondary" className="border-danger text-danger dark:border-red-500 dark:text-red-400" onClick={handlePurgeBlobs}>
                <Trash2 size={16} /> {t("purgeBlobs")}
              </Button>
            </div>
          </div>
        </>
      )}

      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/60 p-4">
          <div className="w-full max-w-md rounded-sm border border-line bg-surface p-6">
            <h3 className="font-display text-xl text-danger">{t("confirmPurge")}</h3>
            <p className="mt-2 text-sm text-muted">{t("typeDeleteBelow")}</p>
            <Input id="delete-confirmation" className="mt-4" value={deleteConfirmText} onChange={(e) => setDeleteConfirmText(e.target.value)} placeholder={t("deleteConfirmationPlaceholder")} />
            <div className="mt-6 flex justify-end gap-3">
              <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>{t("cancel")}</Button>
              <Button variant="danger" disabled={deleteConfirmText !== "DELETE" || isDeleting} onClick={handleDeleteData}>
                {t("confirmDelete")}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
