import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, CloudSun, History, MapPin, ShieldAlert } from "../components/icons";
import { useAuth } from "../context/AuthContext";
import { getExpertReview, submitExpertReview } from "../api/expert";
import { getAssetUrl } from "../api/client";
import { Badge, Button, Card, Input, Select } from "../components/ui";

const actions = ["Approve", "Override / Correct Findings", "Request Rescan"] as const;
type ReviewAction = (typeof actions)[number];

export default function ExpertReviewPage() {
  const { id } = useParams();
  const { token, t, language } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [action, setAction] = useState<ReviewAction>("Approve");
  const [correctedDisease, setCorrectedDisease] = useState("");
  const [correctedSeverity, setCorrectedSeverity] = useState("");
  const [immediateAction, setImmediateAction] = useState("");
  const [treatment, setTreatment] = useState("");
  const [internalNote, setInternalNote] = useState("");
  const [addToRetraining, setAddToRetraining] = useState(false);
  const [heatmapOpacity, setHeatmapOpacity] = useState(65);

  const { data: review, isLoading } = useQuery({
    queryKey: ["expertReview", id],
    queryFn: () => getExpertReview(Number(id), token!),
    enabled: !!token && !!id,
  });

  const mutation = useMutation({
    mutationFn: () => submitExpertReview(Number(id), {
      action,
      corrected_disease: action === "Override / Correct Findings" ? correctedDisease : undefined,
      corrected_severity: action === "Override / Correct Findings" ? correctedSeverity : undefined,
      farmer_guidance: `Immediate Action: ${immediateAction}\nTreatment: ${treatment}`,
      internal_note: internalNote || undefined,
      add_to_retraining: addToRetraining,
    }, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expertQueue"] });
      navigate("/admin/expert");
    },
  });

  if (isLoading) return <div className="flex min-h-[40vh] items-center justify-center text-sm text-muted">{t("loadingClinicalReview")}</div>;
  if (!review) return <Card className="text-danger">{t("reviewNotFound")}</Card>;

  const rawImage = getAssetUrl(review.raw_url || review.raw_path);
  const processedImage = getAssetUrl(review.processed_url || review.processed_path) || rawImage;
  const triggerReason = review.disease_conf < 0.7 ? "Confidence < 70% Threshold" : "Rule Engine Safety Trigger";
  const date = review.created_at ? new Date(review.created_at).toLocaleString() : "Unknown";

  return (
    <div className="space-y-6 pb-12">
      <Card className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-wrap items-center gap-4">
          <button onClick={() => navigate("/admin/expert")} className="inline-flex items-center gap-2 text-sm font-semibold text-muted hover:text-ink"><ArrowLeft size={18} /> {t("backToQueue")}</button>
          <h2 className="font-display text-xl text-ink">{t("case")} #{review.prediction_id}: {review.crop} ({review.disease})</h2>
          <Badge tone={review.status === "verified" ? "success" : "danger"}><ShieldAlert size={14} /> {review.status === "verified" ? t("verified") : t("criticalTriage")}</Badge>
        </div>
        <div className="flex flex-wrap gap-2 text-xs text-muted"><Badge>{triggerReason}</Badge><span>{date}</span></div>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <Card>
            <h3 className="border-b border-line pb-3 font-display text-xl text-ink">{t("visualModelEvidence")}</h3>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <div className="relative aspect-[4/3] overflow-hidden rounded-sm border border-line bg-farmer-950"><span className="absolute left-2 top-2 z-10 rounded-sm bg-black/70 px-2 py-1 text-xs text-white">{t("rawLeaf")}</span><img className="h-full w-full object-contain" src={rawImage} alt="Raw leaf" /></div>
              <div className="relative aspect-[4/3] overflow-hidden rounded-sm border border-line bg-farmer-950"><span className="absolute left-2 top-2 z-10 rounded-sm bg-black/70 px-2 py-1 text-xs text-white">{t("gradcamHeatmap")}</span><img className="h-full w-full object-contain" src={processedImage} alt="Heatmap base" /><div className="absolute inset-0 bg-[radial-gradient(circle,rgba(214,119,86,0.8),rgba(214,119,86,0)_70%)] mix-blend-multiply" style={{ opacity: heatmapOpacity / 100 }} /></div>
            </div>
            <label className="mt-5 flex items-center gap-3 text-sm text-muted">{t("opacity")} <input className="flex-1 accent-farmer-700 dark:accent-farmer-400" type="range" min="0" max="100" value={heatmapOpacity} onChange={event => setHeatmapOpacity(Number(event.target.value))} /><span>{heatmapOpacity}%</span></label>
          </Card>


          <Card>
            <h3 className="border-b border-line pb-3 font-display text-xl text-ink">{t("modelTelemetryContext")}</h3>
            <div className="mt-5 grid gap-6 sm:grid-cols-2">
              <ul className="space-y-3 text-sm text-ink"><li><strong>{t("crop")}:</strong> {review.crop}</li><li><strong>{t("identifiedCondition")}:</strong> {review.disease} ({(review.disease_conf * 100).toFixed(0)}%)</li><li><strong>{t("severity")}:</strong> {review.severity_pct.toFixed(0)}% {t("affectedArea")}</li><li><strong>{t("pests")}:</strong> {t("noPests")}</li></ul>
              <ul className="space-y-3 text-sm text-ink"><li><CloudSun size={16} className="mr-2 inline text-expert-500" /><strong>{t("weather")}:</strong> Current conditions available in prediction</li><li><MapPin size={16} className="mr-2 inline text-expert-500" /><strong>{t("location")}:</strong> Prediction location</li><li><History size={16} className="mr-2 inline text-expert-500" /><strong>{t("history")}:</strong> Review prediction history</li></ul>
            </div>
          </Card>
        </div>

        <Card>
          <h3 className="border-b border-line pb-3 font-display text-xl text-ink">{t("expertDecisionGuidance")}</h3>
          <fieldset className="mt-6"><legend className="mb-3 text-sm font-semibold text-ink">{t("diagnosticVerdict")}</legend><div className="space-y-2">{actions.map(option => <label className={`flex cursor-pointer items-center gap-3 rounded-sm border p-3 text-sm transition-colors ${action === option ? "border-farmer-500 bg-farmer-50 font-semibold text-ink dark:border-farmer-400 dark:bg-farmer-900/40" : "border-line text-ink hover:bg-canvas"}`} key={option}><input type="radio" name="verdict" checked={action === option} onChange={() => setAction(option)} className="accent-farmer-600 dark:accent-farmer-400" />{option === "Approve" ? t("approve") : option === "Override / Correct Findings" ? t("overrideFindings") : t("requestRescan")}</label>)}</div></fieldset>
          {action === "Override / Correct Findings" && (
            <div className="mt-6 space-y-4">
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-ink" htmlFor="corrected-disease">
                  {t("correctedDisease")}
                </label>
                  <Select
                    id="corrected-disease"
                    value={correctedDisease}
                    onChange={(val) => setCorrectedDisease(val)}
                    theme="expert"
                    leadingIcon={<ShieldAlert size={15} className="text-expert-700" />}
                    placeholder={t("selectDisease")}
                    options={[
                      { value: "", label: t("selectDisease") },
                      { value: "Early Blight", label: "Early Blight" },
                      { value: "Late Blight", label: "Late Blight" },
                      { value: "Fusarium Wilt", label: "Fusarium Wilt" },
                      { value: "Nutrient Deficiency", label: "Nutrient Deficiency" },
                    ]}
                  />
              </div>
              <label className="block space-y-2 text-sm font-semibold text-ink">
                {t("correctedSeverity")}
                <input
                  className="min-h-11 w-full rounded-sm border border-line bg-surface px-3 font-normal text-ink focus:border-farmer-500 focus:outline-none focus:ring-1 focus:ring-farmer-500"
                  value={correctedSeverity}
                  onChange={(event) => setCorrectedSeverity(event.target.value)}
                  placeholder={t("affectedPercentage")}
                />
              </label>
            </div>
          )}
          <div className="mt-7 space-y-4"><h4 className="text-sm font-semibold text-ink">{t("farmerGuidance")}</h4><Input label={t("immediateAction")} value={immediateAction} onChange={event => setImmediateAction(event.target.value)} /><Input label={t("treatmentDosage")} value={treatment} onChange={event => setTreatment(event.target.value)} /></div>
          <div className="mt-7 space-y-4">
            <h4 className="text-sm font-semibold text-ink">{t("internalAudit")}</h4>
            <label className="flex items-center gap-2 text-sm text-ink cursor-pointer">
              <input type="checkbox" checked={addToRetraining} onChange={event => setAddToRetraining(event.target.checked)} className="h-4 w-4 rounded border-line accent-farmer-600 dark:accent-farmer-400" />
              <span>{t("flagRetraining")}</span>
            </label>
            <textarea className="min-h-24 w-full rounded-sm border border-line bg-surface p-3 text-sm text-ink placeholder:text-muted focus:border-farmer-500 focus:outline-none focus:ring-1 focus:ring-farmer-500" placeholder={t("retrainingNotesPlaceholder")} value={internalNote} onChange={event => setInternalNote(event.target.value)} />
          </div>
          <div className="mt-8 flex gap-3 border-t border-line pt-5"><Button variant="secondary" className="flex-1" onClick={() => navigate("/admin/expert")}>{t("cancel")}</Button><Button className="flex-1" onClick={() => mutation.mutate()} disabled={mutation.isPending}>{mutation.isPending ? t("submitting") : t("submitReview")}</Button></div>
        </Card>
      </div>
    </div>
  );
}
