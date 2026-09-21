import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, CloudSun, History, MapPin, ShieldAlert } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getExpertReview, submitExpertReview } from "../api/expert";
import { getAssetUrl } from "../api/client";
import { Badge, Button, Card, Input } from "../components/ui";

const actions = ["Approve", "Override / Correct Findings", "Request Rescan"] as const;
type ReviewAction = (typeof actions)[number];

export default function ExpertReviewPage() {
  const { id } = useParams();
  const { token } = useAuth();
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

  if (isLoading) return <div className="flex min-h-[40vh] items-center justify-center text-sm text-muted">Loading clinical review...</div>;
  if (!review) return <Card className="text-danger">Review not found</Card>;

  const rawImage = getAssetUrl(review.raw_path);
  const triggerReason = review.disease_conf < 0.7 ? "Confidence < 70% Threshold" : "Rule Engine Safety Trigger";
  const date = review.created_at ? new Date(review.created_at).toLocaleString() : "Unknown";

  return (
    <div className="space-y-6 pb-12">
      <Card className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-wrap items-center gap-4">
          <button onClick={() => navigate("/admin/expert")} className="inline-flex items-center gap-2 text-sm font-semibold text-muted hover:text-ink"><ArrowLeft size={18} /> Back to Queue</button>
          <h2 className="font-display text-xl text-ink">Case #{review.prediction_id}: {review.crop} ({review.disease})</h2>
          <Badge tone={review.status === "verified" ? "success" : "danger"}><ShieldAlert size={14} /> {review.status === "verified" ? "Verified" : "Critical Triage"}</Badge>
        </div>
        <div className="flex flex-wrap gap-2 text-xs text-muted"><Badge>{triggerReason}</Badge><span>{date}</span></div>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <Card>
            <h3 className="border-b border-line pb-3 font-display text-xl text-ink">Visual & Model Evidence</h3>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <div className="relative aspect-[4/3] overflow-hidden rounded-sm bg-ink"><span className="absolute left-2 top-2 z-10 rounded-sm bg-ink/80 px-2 py-1 text-xs text-white">RAW LEAF</span><img className="h-full w-full object-contain" src={rawImage} alt="Raw leaf" /></div>
              <div className="relative aspect-[4/3] overflow-hidden rounded-sm bg-ink"><span className="absolute left-2 top-2 z-10 rounded-sm bg-ink/80 px-2 py-1 text-xs text-white">GRAD-CAM HEATMAP</span><img className="h-full w-full object-contain" src={rawImage} alt="Heatmap base" /><div className="absolute inset-0 bg-[radial-gradient(circle,rgba(214,119,86,0.8),rgba(214,119,86,0)_70%)] mix-blend-multiply" style={{ opacity: heatmapOpacity / 100 }} /></div>
            </div>
            <label className="mt-5 flex items-center gap-3 text-sm text-muted">Opacity <input className="flex-1 accent-farmer-700" type="range" min="0" max="100" value={heatmapOpacity} onChange={event => setHeatmapOpacity(Number(event.target.value))} /><span>{heatmapOpacity}%</span></label>
          </Card>

          <Card>
            <h3 className="border-b border-line pb-3 font-display text-xl text-ink">Model Telemetry & Agronomic Context</h3>
            <div className="mt-5 grid gap-6 sm:grid-cols-2">
              <ul className="space-y-3 text-sm text-ink"><li><strong>Crop:</strong> {review.crop}</li><li><strong>Disease:</strong> {review.disease} ({(review.disease_conf * 100).toFixed(0)}%)</li><li><strong>Severity:</strong> {review.severity_pct.toFixed(0)}% affected</li><li><strong>Pests:</strong> None detected</li></ul>
              <ul className="space-y-3 text-sm text-ink"><li><CloudSun size={16} className="mr-2 inline text-expert-500" /><strong>Weather:</strong> Current conditions available in prediction</li><li><MapPin size={16} className="mr-2 inline text-expert-500" /><strong>Location:</strong> Prediction location</li><li><History size={16} className="mr-2 inline text-expert-500" /><strong>History:</strong> Review prediction history</li></ul>
            </div>
          </Card>
        </div>

        <Card>
          <h3 className="border-b border-line pb-3 font-display text-xl text-ink">Expert Decision & Guidance</h3>
          <fieldset className="mt-6"><legend className="mb-3 text-sm font-semibold text-ink">Diagnostic Verdict</legend><div className="space-y-2">{actions.map(option => <label className={`flex cursor-pointer items-center gap-3 rounded-sm border p-3 text-sm ${action === option ? "border-farmer-500 bg-farmer-50 font-semibold" : "border-line"}`} key={option}><input type="radio" name="verdict" checked={action === option} onChange={() => setAction(option)} />{option}</label>)}</div></fieldset>
          {action === "Override / Correct Findings" && <div className="mt-6 space-y-4"><label className="block space-y-2 text-sm font-semibold text-ink">Corrected Disease<select className="min-h-11 w-full rounded-sm border border-line bg-surface px-3 font-normal" value={correctedDisease} onChange={event => setCorrectedDisease(event.target.value)}><option value="">Select Disease...</option><option>Early Blight</option><option>Late Blight</option><option>Fusarium Wilt</option><option>Nutrient Deficiency</option></select></label><label className="block space-y-2 text-sm font-semibold text-ink">Corrected Severity<input className="min-h-11 w-full rounded-sm border border-line px-3 font-normal" value={correctedSeverity} onChange={event => setCorrectedSeverity(event.target.value)} placeholder="Affected percentage" /></label></div>}
          <div className="mt-7 space-y-4"><h4 className="text-sm font-semibold text-ink">Farmer Guidance</h4><Input label="Immediate Action" value={immediateAction} onChange={event => setImmediateAction(event.target.value)} /><Input label="Treatment & Dosage" value={treatment} onChange={event => setTreatment(event.target.value)} /></div>
          <div className="mt-7 space-y-4"><h4 className="text-sm font-semibold text-ink">Internal Audit</h4><label className="flex items-center gap-2 text-sm text-muted"><input type="checkbox" checked={addToRetraining} onChange={event => setAddToRetraining(event.target.checked)} /> Flag for retraining</label><textarea className="min-h-24 w-full rounded-sm border border-line p-3 text-sm" placeholder="Notes for model retraining team..." value={internalNote} onChange={event => setInternalNote(event.target.value)} /></div>
          <div className="mt-8 flex gap-3 border-t border-line pt-5"><Button variant="secondary" className="flex-1" onClick={() => navigate("/admin/expert")}>Cancel</Button><Button className="flex-1" onClick={() => mutation.mutate()} disabled={mutation.isPending}>{mutation.isPending ? "Submitting..." : "Submit Review"}</Button></div>
        </Card>
      </div>
    </div>
  );
}
