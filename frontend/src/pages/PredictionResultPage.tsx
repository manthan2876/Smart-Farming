import { getAssetUrl, request } from "../api/client";
import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "motion/react";
import imageCompression from "browser-image-compression";
import { AlertCircle, CheckCircle2, Loader2, Pause, ShieldAlert, Volume2, Printer, Activity, Sprout } from "../components/icons";
import { useAuth } from "../context/AuthContext";
import { getPrediction, requestExpertReview } from "../api/predictions";
import { Badge, Button, Card, Input } from "../components/ui";
import { translateCrop, translateDisease, translatePest, translateSeverityBucket, translateWeather } from "../i18n/domain";

export default function PredictionResultPage() {
  const { id } = useParams<{ id: string }>();
  const { token, language, t } = useAuth();
  const targetLang = language === "Hindi" ? "hi" : language === "Gujarati" ? "gu" : "en";
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoadingAudio, setIsLoadingAudio] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [farmerNote, setFarmerNote] = useState("");
  const [localTranslations, setLocalTranslations] = useState<Record<string, any>>({});
  const inFlightLangRef = useRef<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    // Whenever a prediction is viewed, refresh alerts cache so unread notifications update
    if (id && token) {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    }
  }, [id, token, queryClient]);

  const { data: prediction, isLoading, isError, refetch } = useQuery({
    queryKey: ["prediction", id],
    queryFn: () => getPrediction(id as string, token!),
    refetchInterval: (query) => {
      const current = query.state.data;
      if (!current) return false;
      const latest = current.follow_up || current;
      return (latest.status as any)?.pipeline === "processing" || (latest.status as any)?.preprocessing === "processing" ? 2000 : false;
    },
  });

  useEffect(() => {
    if (targetLang !== "en" && prediction && id && token) {
      const primary = prediction.follow_up || prediction;
      const alreadyHasTranslation = primary.translations?.[targetLang] || localTranslations[targetLang];
      if (!alreadyHasTranslation && inFlightLangRef.current !== targetLang) {
        inFlightLangRef.current = targetLang;
        setIsTranslating(true);
        request<any>(`/predictions/${id}/translate?target_language=${targetLang}`, { method: "POST" }, token)
          .then((res) => {
            if (res?.recommendation) {
              setLocalTranslations((prev) => ({ ...prev, [targetLang]: res.recommendation }));
            }
            return refetch();
          })
          .catch((e) => console.error("Auto translation error:", e))
          .finally(() => {
            inFlightLangRef.current = null;
            setIsTranslating(false);
          });
      }
    }
  }, [targetLang, prediction, id, token, localTranslations, refetch]);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0];
    if (!selected) return;
    try {
      setIsUploading(true);
      setSelectedFile(await imageCompression(selected, { maxSizeMB: 1, maxWidthOrHeight: 1440, useWebWorker: true }));
    } catch (error) {
      console.error("Compression error:", error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRescanSubmit = async () => {
    if (!selectedFile || !token || !id) return;
    setIsUploading(true);
    try {
      const { rescan } = await import("../api/predictions");
      await rescan(id, selectedFile, token);
      await refetch();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
      console.error(error);
      alert("Failed to upload new photo.");
    } finally {
      setIsUploading(false);
      setSelectedFile(null);
    }
  };

  const toggleAudio = async (text: string) => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        await audioRef.current.play();
        setIsPlaying(true);
      }
      return;
    }
    try {
      setIsLoadingAudio(true);
      const response: any = await request("/tts", { method: "POST", body: JSON.stringify({ text, language: targetLang }) }, token!);
      if (response?.audioContent) {
        const format = response.format || (response.audioContent.startsWith("UklGR") ? "wav" : "mpeg");
        const mimeType = format === "wav" ? "audio/wav" : "audio/mpeg";
        const audio = new Audio(`data:${mimeType};base64,${response.audioContent}`);
        audioRef.current = audio;
        audio.onended = () => setIsPlaying(false);
        audio.onpause = () => setIsPlaying(false);
        audio.onplay = () => setIsPlaying(true);
        await audio.play();
        setIsPlaying(true);
      }
    } catch (error) {
      console.error(error);
      setIsPlaying(false);
    } finally {
      setIsLoadingAudio(false);
    }
  };

  const handleRequestExpert = async () => {
    try {
      await requestExpertReview(id!, token!);
      alert("Expert review requested successfully!");
      refetch();
    } catch (error) {
      console.error(error);
      alert("Failed to request expert review.");
    }
  };

  const submitFeedback = async (correct: boolean) => {
    try {
      await request("/feedback", { method: "POST", body: JSON.stringify({ prediction_id: Number(id), is_correct: correct, farmer_note: farmerNote }) }, token!);
      setFeedbackSubmitted(true);
    } catch (error) {
      console.error("Feedback submission failed", error);
    }
  };

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><Loader2 className="animate-spin text-farmer-700" size={36} /></div>;
  if (isError || !prediction) return <Card className="text-danger">Failed to load prediction details.</Card>;

  const primary = prediction.follow_up || prediction;
  const original = prediction.follow_up ? prediction : null;
  const status = primary.status as any;
  const isPendingReview = status?.expert_review === "pending";
  const isProcessing = status?.pipeline === "processing" || status?.preprocessing === "processing";
  const isFailed = status?.pipeline === "failed";

  const AudioButton = ({ text }: { text: string }) => <Button variant="secondary" size="sm" className="no-print" onClick={() => toggleAudio(text)} disabled={isLoadingAudio}>
    {isLoadingAudio ? <Loader2 size={16} className="animate-spin" /> : isPlaying ? <Pause size={16} /> : <Volume2 size={16} />}
    {isLoadingAudio ? t("loading") : isPlaying ? t("pauseAudio") : t("listenAdvisory")}
  </Button>;

  const TreatmentProgressCard = ({ progress }: { progress: any }) => {
    if (!progress) return null;
    const status = progress.status;
    const statusBadgeTone = status === "improving" || status === "resolved" ? "success" : status === "worsening" ? "danger" : "info";
    const statusText = status === "improving" 
      ? t("treatmentImproving") 
      : status === "worsening" 
      ? t("treatmentWorsening") 
      : status === "resolved"
      ? t("treatmentResolved")
      : t("treatmentStable");
    const delta = progress.severity_delta;
    const deltaFormatted = delta > 0 ? `+${delta.toFixed(1)}%` : `${delta?.toFixed(1)}%`;

    return (
      <Card className="border-farmer-300 dark:border-farmer-700">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Activity className="text-farmer-600 dark:text-farmer-400" size={22} />
            <h3 className="font-display text-xl text-ink">{t("treatmentProgress")}</h3>
          </div>
          <Badge tone={statusBadgeTone} className="text-xs font-semibold px-2.5 py-1 uppercase">
            {statusText}
          </Badge>
        </div>

        <p className="mt-3 text-sm text-ink leading-6">{progress.message}</p>

        <div className="mt-5 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
          <div className="rounded-sm border border-line bg-canvas p-4">
            <div className="text-xs uppercase tracking-wider text-muted">{t("previousScan")}</div>
            <div className="mt-1.5 font-display text-2xl font-bold text-ink">
              {progress.parent_severity_pct != null ? `${progress.parent_severity_pct.toFixed(1)}%` : "N/A"}
            </div>
            <div className="mt-1 text-xs text-muted">
              {translateSeverityBucket(progress.parent_severity_bucket, language)}
              {progress.parent_date && ` • ${new Date(progress.parent_date).toLocaleDateString()}`}
            </div>
          </div>

          <div className="rounded-sm border border-line bg-canvas p-4">
            <div className="text-xs uppercase tracking-wider text-muted">{t("currentScan")}</div>
            <div className="mt-1.5 font-display text-2xl font-bold text-ink">
              {progress.current_severity_pct != null ? `${progress.current_severity_pct.toFixed(1)}%` : "N/A"}
            </div>
            <div className="mt-1 text-xs text-muted">
              {translateSeverityBucket(progress.current_severity_bucket, language)}
            </div>
          </div>

          <div className={`rounded-sm border p-4 ${status === "improving" || status === "resolved" ? "border-emerald-200 bg-emerald-50 dark:border-emerald-800/60 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-200" : status === "worsening" ? "border-rose-200 bg-rose-50 dark:border-rose-900/60 dark:bg-rose-950/40 text-rose-800 dark:text-rose-200" : "border-line bg-canvas text-ink"}`}>
            <div className="text-xs uppercase tracking-wider opacity-80">{t("severityDelta")}</div>
            <div className="mt-1.5 font-display text-2xl font-bold">
              {deltaFormatted}
            </div>
            <div className="mt-1 text-xs opacity-80">
              {statusText}
            </div>
          </div>
        </div>
      </Card>
    );
  };

  const Advisory = ({ predictionData }: { predictionData: any }) => {
    const rawRec = predictionData.recommendation || {};
    const translatedRec = targetLang !== "en" ? (predictionData.translations?.[targetLang] || localTranslations[targetLang]) : null;
    const recommendation = translatedRec || rawRec;
    const expertGuidance = predictionData.expert_review_data?.farmer_guidance;
    const isFallback = rawRec.is_fallback === true;
    const masked = (predictionData.status as any)?.mask_advisory === true || ((predictionData.status as any)?.expert_review === "pending" && !recommendation.immediate_action);
    if (masked) return <Card className="mt-6 border-dashed text-center text-muted"><ShieldAlert className="mx-auto mb-3 opacity-50" size={32} /><h4 className="font-semibold text-ink">{t("advisoryMasked")}</h4><p className="mx-auto mt-2 max-w-xl text-sm leading-6">{t("advisoryMaskedDesc")}</p></Card>;
    if (expertGuidance) return <Card className="mt-6 border-expert-100 bg-expert-50 text-expert-700 dark:border-cyan-800 dark:bg-cyan-950/40 dark:text-cyan-100"><div className="flex flex-wrap items-center justify-between gap-3"><h3 className="flex items-center gap-2 font-display text-xl text-ink dark:text-cyan-200"><CheckCircle2 size={22} className="text-cyan-400" /> {t("specialistVerifiedPlan")}</h3><AudioButton text={expertGuidance} /></div><div className="mt-5 rounded-sm border border-farmer-200 bg-farmer-50 p-5 dark:border-emerald-800/60 dark:bg-emerald-950/40"><h4 className="font-semibold text-farmer-800 dark:text-emerald-300">{t("agronomistGuidance")}</h4><p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-farmer-800 dark:text-emerald-100">{expertGuidance}</p></div><p className="mt-4 border-l-4 border-danger bg-red-50 p-3 text-xs leading-5 text-danger dark:border-red-800 dark:bg-red-950/40 dark:text-red-200"><strong>Important:</strong> Always follow local agricultural guidelines and chemical label instructions.</p></Card>;
    if (!Object.keys(recommendation).length) return null;
    const advisoryText = [recommendation.immediate_action, recommendation.action, recommendation.fertilizer, recommendation.treatment, recommendation.pesticide, recommendation.prevention, recommendation.prevention_tips, recommendation.monitoring, recommendation.irrigation].filter(Boolean).join(". ");
    const sections = [
      [t("immediateAction"), recommendation.immediate_action || recommendation.action || recommendation.fertilizer, "border-red-200 bg-red-50 text-danger dark:border-rose-900/60 dark:bg-rose-950/40 dark:text-rose-200"],
      [t("treatmentGuidance"), recommendation.treatment || recommendation.pesticide, "border-farmer-200 bg-farmer-50 text-farmer-800 dark:border-emerald-800/60 dark:bg-emerald-950/40 dark:text-emerald-200"],
      [t("preventionStrategy"), recommendation.prevention || recommendation.prevention_tips, "border-expert-100 bg-expert-50 text-expert-700 dark:border-cyan-800/60 dark:bg-cyan-950/40 dark:text-cyan-200"],
      [t("monitoringPlan"), recommendation.monitoring || recommendation.irrigation, "border-line bg-canvas text-muted dark:border-line dark:bg-surface/60 dark:text-farmer-100/90"],
    ];
    return <Card className="mt-6 border border-farmer-800 bg-farmer-900 text-farmer-100 shadow-card" padding="lg">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h3 className="font-display text-2xl text-farmer-200">{isFallback ? t("standardAdvisory") : t("aiAdvisoryPlan")}</h3>
          {isFallback && <Badge tone="warning">{t("standardRulesFallback")}</Badge>}
          {isTranslating && <span className="inline-flex items-center gap-1.5 text-xs text-farmer-300"><Loader2 size={12} className="animate-spin" /> {t("translating")}</span>}
        </div>
        <AudioButton text={advisoryText} />
      </div>
      {(predictionData.plot || recommendation.plot_name || recommendation.farm_aware) && (
        <div className="mt-3 inline-flex items-center gap-2 rounded bg-farmer-800/80 px-3 py-1.5 text-xs text-farmer-200 border border-farmer-700">
          <Sprout size={14} className="text-emerald-400" />
          <span>
            <strong>{t("calibratedForPlot")}:</strong> {predictionData.plot?.name || recommendation.plot_name || "Plot"}
            {(predictionData.plot?.area_acres || recommendation.plot_area_acres) && ` (${predictionData.plot?.area_acres || recommendation.plot_area_acres} acres)`}
            {` — ${t("plotScaleAdvice")}`}
          </span>
        </div>
      )}
      {isFallback && <div className="mt-4 rounded-sm border border-amber-400/40 bg-amber-500/10 p-3 text-xs text-amber-200 leading-5">{t("standardRulesNote")}</div>}
      <div className="mt-6 grid gap-4 sm:grid-cols-2">{sections.map(([title, value, classes]) => value ? <div className={`rounded-sm border p-4 ${classes}`} key={title}><h4 className="font-semibold">{title}</h4><p className="mt-2 text-sm leading-6">{value}</p></div> : null)}</div>
      <p className="mt-5 border-l-4 border-danger bg-red-50 dark:bg-red-950/40 p-3 text-xs leading-5 text-danger dark:text-red-300"><strong>{t("important")}:</strong> {recommendation.safety_disclaimer || "Always follow local agricultural guidelines and chemical label instructions."}</p>
    </Card>;
  };

  const PredictionBlock = ({ predictionData }: { predictionData: any }) => {
    if (predictionData.error || (predictionData.status as any)?.pipeline === "failed") return <div className="rounded-md border border-red-200 bg-red-50 p-6 text-danger"><h3 className="flex items-center gap-2 font-display text-xl"><AlertCircle size={22} /> {t("pipelineError")}</h3><p className="mt-3">{predictionData.error || t("analysisNotCompleted")}</p><p className="mt-3 text-sm">{t("captureBetterLighting")}</p></div>;
    const rawImage = predictionData.image?.raw_url || predictionData.raw_url || (predictionData.image?.raw_path ? getAssetUrl(predictionData.image.raw_path) : (predictionData.raw_path ? getAssetUrl(predictionData.raw_path) : null));
    const processedImage = predictionData.image?.processed_url || predictionData.processed_url || (predictionData.image?.processed_path ? getAssetUrl(predictionData.image.processed_path) : (predictionData.processed_path ? getAssetUrl(predictionData.processed_path) : null));
    const diseaseConfidence = (predictionData.disease?.confidence || 0) * 100;
    const isLowConfidence = predictionData.disease?.is_uncertain === true || diseaseConfidence < 60;
    const confRating = predictionData.disease?.confidence_rating || (diseaseConfidence >= 85 ? "high" : diseaseConfidence >= 60 ? "moderate" : "low");
    const severityPercent = predictionData.severity?.percent || 0;
    const pestStatus = predictionData.pest_classification?.status || (predictionData.status as any)?.pest_detection;
    const pestOffline = predictionData.pest_classification?.available === false || pestStatus === "unavailable" || pestStatus === "skipped";
    const weatherDegraded = predictionData.weather?.is_degraded || predictionData.weather?.status === "failed" || !predictionData.weather?.temperature_celsius;
    const isUnsupportedCrop =
      predictionData.crop?.status === "unsupported_crop" ||
      (predictionData.status as any)?.decision_routing === "unsupported_crop" ||
      predictionData.disease?.label?.toLowerCase().includes("unsupported crop");

    return <div className="space-y-6">
      {predictionData.treatment_progress && (
        <TreatmentProgressCard progress={predictionData.treatment_progress} />
      )}
      {isUnsupportedCrop && (
        <Card className="border-amber-300 bg-amber-50/90 dark:border-amber-700/60 dark:bg-amber-950/40">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 text-amber-700 dark:text-amber-400 shrink-0" size={20} />
            <div>
              <h3 className="font-display text-lg font-semibold text-amber-900 dark:text-amber-200">
                {t("unsupportedCropTitle")}
              </h3>
              <p className="mt-1 text-sm text-amber-800 dark:text-amber-300">
                {t("unsupportedCropDesc")}
              </p>
              <div className="mt-2.5 flex flex-wrap gap-1.5 items-center text-xs text-amber-900 dark:text-amber-200">
                <span className="font-semibold">{t("supportedCropsLabel")}:</span>
                {["Cotton", "Groundnut", "Pepper Bell", "Potato", "Tomato"].map((c) => (
                  <span key={c} className="rounded bg-amber-200/70 dark:bg-amber-900/60 px-2 py-0.5 font-medium">
                    {translateCrop(c, language)}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </Card>
      )}
      <Card><h3 className="font-display text-xl text-ink">{t("visualAnalysis")}</h3><div className="mt-5 grid gap-4 sm:grid-cols-2">{[[t("originalUpload"), rawImage, ""], [t("gradcamHeatmap"), processedImage, "bg-ink text-farmer-200"]].map(([label, image, labelClass]) => <div key={label || "analysis"}><span className={`mb-2 block rounded-sm px-2 py-1 text-center text-xs font-semibold uppercase tracking-wide text-muted ${labelClass || ""}`}>{label || "Analysis"}</span>{image ? <img className="aspect-square w-full rounded-sm border border-line object-cover" src={image} alt={label || "Analysis image"} /> : <div className="flex aspect-square items-center justify-center rounded-sm bg-canvas text-sm text-muted">{t("imageUnavailable")}</div>}</div>)}</div></Card>
      <Card>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="font-display text-xl text-ink">{t("diagnosticTelemetry")}</h3>
          <Badge tone={confRating === "high" ? "success" : confRating === "moderate" ? "info" : "warning"}>{confRating.toUpperCase()} {t("confidence").toUpperCase()}</Badge>
        </div>
        <div className="mt-5 space-y-4">
          <div className="rounded-sm bg-canvas p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="font-display text-2xl text-ink">
                {(predictionData.status as any)?.expert_review === "pending"
                  ? t("pendingVerification")
                  : translateDisease(predictionData.disease?.label, language)}
              </h2>
              {((predictionData.status as any)?.expert_review === "verified" || (predictionData.status as any)?.pipeline === "verified") && (
                <Badge tone="success" className="inline-flex items-center gap-1">
                  <CheckCircle2 size={13} /> {t("specialistVerified")}
                </Badge>
              )}
            </div>
            {predictionData.expert_review_data?.corrected_disease && (
              <p className="mt-1 text-xs font-semibold text-emerald-700 dark:text-emerald-400">
                {t("correctedBySpecialist")}: {translateDisease(predictionData.expert_review_data.corrected_disease, language)}
              </p>
            )}
            <p className="mt-1 text-sm text-muted">{t("modelConfidence")}: {diseaseConfidence.toFixed(1)}% (Threshold: 60%)</p>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-line">
              <div className={`h-full ${isLowConfidence ? "bg-amber-500" : "bg-farmer-700"}`} style={{ width: `${diseaseConfidence}%` }} />
            </div>
            {isLowConfidence && <div className="mt-3 rounded border border-amber-200 bg-amber-50 p-2.5 text-xs text-amber-800">{t("tentativeDiagnosisDesc")}</div>}
            {predictionData.disease?.could_also_be && (
              <div className="mt-3 rounded border border-amber-300 bg-amber-50/80 p-3 text-xs text-amber-900 dark:border-amber-700/60 dark:bg-amber-950/40 dark:text-amber-200">
                <div className="flex items-center gap-1.5 font-semibold text-amber-800 dark:text-amber-300">
                  <AlertCircle size={15} />
                  <span>
                    {t("couldAlsoBe")}: {translateDisease(predictionData.disease.could_also_be.label || predictionData.disease.could_also_be, language)} ({((predictionData.disease.could_also_be.confidence || 0) * 100).toFixed(1)}%)
                  </span>
                </div>
                <p className="mt-1 text-[11px] leading-4 text-amber-700 dark:text-amber-400">
                  {t("nearTieExplanation")}
                </p>
              </div>
            )}
          </div>
          <div className="rounded-sm bg-canvas p-4">
            <h2 className="font-display text-xl text-ink">{t("severity")}: {translateSeverityBucket(predictionData.severity?.bucket, language)}</h2>
            <p className="mt-1 text-sm text-muted">{t("affectedArea")}: {severityPercent}%</p>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-line"><div className="h-full bg-admin-500" style={{ width: `${severityPercent}%` }} /></div>
          </div>
          <div className="text-xs uppercase tracking-wide text-muted space-y-1.5">
            <p><strong>{t("crop")}:</strong> {translateCrop(predictionData.crop?.label, language)} {predictionData.crop?.confidence && `(${(predictionData.crop.confidence * 100).toFixed(1)}%)`}</p>
            <p><strong>{t("pests")}:</strong> {pestOffline ? <span className="inline-flex items-center gap-1 rounded bg-amber-100/80 px-2 py-0.5 text-[11px] font-medium text-amber-800 dark:bg-amber-950/50 dark:text-amber-300"><AlertCircle size={11} /> {t("pestDetectorUnavailable")}</span> : predictionData.pests?.length ? predictionData.pests.map((p: any) => `${translatePest(p.label, language)}${p.confidence ? ` (${(p.confidence * 100).toFixed(0)}%)` : ""}`).join(", ") : <span className="inline-flex items-center gap-1 text-emerald-700 dark:text-emerald-400 font-medium"><CheckCircle2 size={12} /> {t("noPestsDetected")}</span>}</p>
            <p><strong>{t("weather")} {t("context")}:</strong> {weatherDegraded ? <span className="italic text-amber-600">{t("unavailableDuringScan")}</span> : `${predictionData.weather?.temperature_celsius}°C, ${predictionData.weather?.humidity_percent}% ${t("humidity").toLowerCase()} (${translateWeather(predictionData.weather?.condition, language)})`}</p>
          </div>
          <div className="flex flex-wrap items-center justify-between border-t border-line pt-3 text-[11px] text-muted">
            <span>Model: {predictionData.provenance?.models?.disease?.name || predictionData.disease?.model_used || "EfficientNet-B2"}</span>
            {predictionData.total_duration_ms && <span>Processing Latency: {predictionData.total_duration_ms} ms</span>}
            <span>Schema: v{predictionData.schema_version || "2.0"}</span>
          </div>
        </div>
      </Card>
      <Advisory predictionData={predictionData} />
    </div>;
  };

  const historicalImages = primary.historical_images || [];
  return (
    <>
      {isUploading && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-surface/95 p-4 no-print">
          <Loader2 size={52} className="animate-spin text-farmer-700" />
          <h2 className="mt-6 font-display text-2xl text-ink">{t("rerunningPipeline")}</h2>
          <p className="mt-2 text-muted">{t("analyzingFollowUpPhoto")}</p>
        </div>
      )}
      <motion.div className="space-y-6 pb-12" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        {/* Printable Official Header */}
        <div className="hidden print-only mb-6 border-b border-gray-300 pb-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{t("diagnosticReportTitle")}</h1>
              <p className="text-xs text-gray-600 mt-1">
                {t("scanReference")}: #{primary.prediction_id || id} | Generated: {new Date().toLocaleString()}
              </p>
            </div>
            <div className="text-right">
              <span className="text-sm font-bold text-emerald-800">Smart Farming Platform</span>
              <p className="text-xs text-gray-500">Agri-tech Field Intelligence</p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <Link to="/history" className="no-print text-xs font-bold uppercase tracking-wide text-muted hover:text-farmer-700">
              &larr; {t("backToHistory")}
            </Link>
            <h1 className="mt-2 font-display text-3xl text-ink sm:text-4xl">
              {t("scanDiagnosis")} #{primary.prediction_id || id} {original && <Badge className="ml-2 align-middle" tone="info">Follow-up</Badge>}
            </h1>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => window.print()}
            className="no-print flex items-center gap-2"
          >
            <Printer size={16} />
            <span>{t("printExportPdf")}</span>
          </Button>
        </div>

        {isPendingReview && (
          <Card className="border-admin-100 bg-admin-50">
            <h3 className="font-display text-xl text-admin-700">{t("additionalReviewRequired")}</h3>
            <p className="mt-2 text-sm leading-6 text-admin-700">
              {t("additionalReviewDesc")}
            </p>
          </Card>
        )}

        <Card className="flex flex-col gap-4 bg-canvas sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="font-display text-xl text-ink">{t("diagnosticStatus")}</h3>
            <div className="mt-3 flex flex-wrap gap-2">
              <Badge tone={status?.pipeline === "completed" || status?.pipeline === "verified" ? "success" : "warning"}>
                Pipeline: {status?.pipeline || "Unknown"}
              </Badge>
              {status?.expert_review === "verified" || status?.pipeline === "verified" ? (
                <Badge tone="success" className="inline-flex items-center gap-1">
                  <CheckCircle2 size={13} /> {t("specialistVerified")}
                </Badge>
              ) : (
                <Badge tone={status?.expert_review === "pending" ? "warning" : "neutral"}>
                  Expert Review: {status?.expert_review || "Not Requested"}
                </Badge>
              )}
            </div>
          </div>
          {status?.expert_review === "not_requested" && !isFailed && (
            <Button variant="secondary" className="no-print" onClick={handleRequestExpert}>
              {t("requestExpert")}
            </Button>
          )}
        </Card>

        {historicalImages.length > 0 && (
          <Card>
            <h3 className="font-display text-xl text-ink">{t("diseaseTimeline")}</h3>
            <div className="mt-5 flex gap-3 overflow-x-auto pb-2">
              {historicalImages.map((item: any, index: number) => (
                <div className="min-w-40 rounded-sm border border-line bg-canvas p-4" key={index}>
                  <div className="text-xs text-muted">{new Date(item.created_at).toLocaleDateString()}</div>
                  <div className="mt-2 font-semibold text-ink">{translateDisease(item.disease, language)}</div>
                  <div className={`mt-1 text-xs font-semibold ${item.severity_pct > 60 ? "text-danger" : "text-farmer-700"}`}>
                    {t("severity")}: {item.severity_pct}%
                  </div>
                </div>
              ))}
              <div className="min-w-40 rounded-sm border-2 border-expert-500 bg-expert-50 p-4">
                <div className="text-xs font-bold text-expert-700">{t("latestScan")}</div>
                <div className="mt-2 font-semibold text-ink">{translateDisease(primary.disease?.label, language)}</div>
                <div className="mt-1 text-xs font-semibold text-farmer-700">
                  {t("severity")}: {primary.severity?.percent || 0}%
                </div>
              </div>
            </div>
          </Card>
        )}

        {isProcessing ? (
          <Card className="flex flex-col items-center text-center" padding="lg">
            <Loader2 size={48} className="animate-spin text-farmer-700" />
            <h2 className="mt-5 font-display text-2xl text-ink">{t("runningPipeline")}</h2>
            <p className="mt-2 text-muted">{t("analyzingBackground")}</p>
          </Card>
        ) : (
          <PredictionBlock predictionData={primary} />
        )}

        {original && (
          <Card>
            <details>
              <summary className="cursor-pointer font-display text-xl text-ink">{t("viewOriginalDetails")}</summary>
              <div className="mt-6">
                <PredictionBlock predictionData={original} />
              </div>
            </details>
          </Card>
        )}

        {!isPendingReview && !isFailed && (
          <Card className="no-print">
            <h3 className="font-display text-xl text-ink">{t("farmerFeedbackTitle")}</h3>
            {feedbackSubmitted ? (
              <div className="mt-4 rounded-sm bg-farmer-700 p-4 text-sm font-semibold text-white">
                {t("feedbackThanks")}
              </div>
            ) : (
              <>
                <p className="mt-2 text-sm leading-6 text-muted">
                  {t("farmerFeedbackSubtitle")}
                </p>
                <textarea
                  className="mt-4 min-h-24 w-full rounded-sm border border-line bg-surface p-3 text-sm text-ink focus:border-farmer-500 focus:outline-none focus:ring-4 focus:ring-farmer-100"
                  placeholder={t("optionalNotes")}
                  value={farmerNote}
                  onChange={(event) => setFarmerNote(event.target.value)}
                />
                <div className="mt-4 flex flex-col gap-3 sm:flex-row">
                  <Button className="flex-1" onClick={() => submitFeedback(true)}>
                    {t("accurate")}
                  </Button>
                  <Button variant="secondary" className="flex-1 border-danger text-danger" onClick={() => submitFeedback(false)}>
                    {t("incorrect")}
                  </Button>
                </div>
              </>
            )}
          </Card>
        )}
      </motion.div>
    </>
  );
}
