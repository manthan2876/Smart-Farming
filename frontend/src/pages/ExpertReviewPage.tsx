import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, CheckCircle2, ShieldAlert, CloudSun, MapPin, Activity, History } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getExpertReview, submitExpertReview } from "../api/expert";
import { motion } from "motion/react";
import "../styles/ExpertReviewPage.css";

export default function ExpertReviewPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // State
  const [action, setAction] = useState<"Approve" | "Override / Correct Findings" | "Request Rescan">("Approve");
  const [correctedDisease, setCorrectedDisease] = useState("");
  const [correctedSeverity, setCorrectedSeverity] = useState("");
  const [pestVerified, setPestVerified] = useState(false);
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
    mutationFn: () => {
      // Build farmer guidance from components
      const guidance = `Immediate Action: ${immediateAction}\nTreatment: ${treatment}`;
      
      return submitExpertReview(Number(id), {
        action: action as any,
        corrected_disease: action === "Override / Correct Findings" ? correctedDisease : undefined,
        corrected_severity: action === "Override / Correct Findings" ? correctedSeverity : undefined,
        farmer_guidance: guidance,
        internal_note: internalNote || undefined,
        add_to_retraining: addToRetraining
      } as any, token!);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expertQueue"] });
      navigate("/admin/expert");
    }
  });

  if (isLoading) return <div className="loading-state">Loading clinical review...</div>;
  if (!review) return <div className="error-state">Review not found</div>;

  const triggerReason = review.disease_conf < 0.70 ? "Confidence < 70% Threshold" : "Rule Engine Safety Trigger";
  const statusColor = review.status === "verified" ? "#10b981" : "#b44c3c";
  const dateStr = review.created_at ? new Date(review.created_at).toLocaleString() : new Date().toLocaleString();

  return (
    <div className="expert-review-page">
      {/* 1. Header & Case Telemetry Strip */}
      <div className="er-header">
        <div className="er-header-left">
          <button onClick={() => navigate("/admin/expert")} className="btn-back-queue">
            <ArrowLeft size={18} /> Back to Queue
          </button>
          <h2 className="er-title">
            Case #{review.prediction_id}: {review.crop} ({review.disease})
          </h2>
          <div className="status-pill" style={{ color: statusColor, background: review.status === "verified" ? "#e4eee4" : "#fff0eb" }}>
            <ShieldAlert size={14} /> 
            {review.status === "verified" ? "Verified" : "Critical Triage"}
          </div>
        </div>
        <div className="er-header-right">
          <div className="er-trigger-flag">Trigger: {triggerReason}</div>
          <div>{dateStr} | Plot A1</div>
        </div>
      </div>

      <div className="er-grid">
        <div className="er-left-col">
          {/* 2. Zone A: Visual Evidence */}
          <div className="er-zone">
            <h3 className="er-zone-title">Visual & Model Evidence</h3>
            <div className="er-visuals">
              <div className="er-image-comparison">
                <div className="er-img-box">
                  <span className="er-img-label">RAW LEAF</span>
                  <img src={`http://127.0.0.1:8000/${review.raw_path}`} alt="Raw" />
                </div>
                <div className="er-img-box" style={{ position: "relative" }}>
                  <span className="er-img-label">GRAD-CAM HEATMAP</span>
                  {/* Simulate heatmap layering via opacity on a duplicate or processed image */}
                  <img src={`http://127.0.0.1:8000/${review.raw_path}`} alt="Heatmap base" />
                  <div style={{
                    position: "absolute", top: 0, left: 0, right: 0, bottom: 0,
                    background: "radial-gradient(circle, rgba(214,119,86,0.8) 0%, rgba(214,119,86,0) 70%)",
                    opacity: heatmapOpacity / 100,
                    mixBlendMode: "multiply"
                  }}></div>
                </div>
              </div>
              <div className="er-slider-container">
                <label>Opacity Slider:</label>
                <input 
                  type="range" 
                  min="0" max="100" 
                  value={heatmapOpacity} 
                  onChange={(e) => setHeatmapOpacity(Number(e.target.value))} 
                />
                <span>{heatmapOpacity}%</span>
              </div>
            </div>
          </div>

          {/* 3. Zone B: AI Inferences vs Context */}
          <div className="er-zone">
            <h3 className="er-zone-title">Model Telemetry & Agronomic Context</h3>
            <div className="er-telemetry-grid">
              <div className="telemetry-block">
                <h4>AI Predictions</h4>
                <ul className="telemetry-list">
                  <li><Activity size={16} /> <strong>Crop:</strong> {review.crop} ({(100).toFixed(0)}%)</li>
                  <li><Activity size={16} /> <strong>Disease:</strong> {review.disease} ({(review.disease_conf * 100).toFixed(0)}%)</li>
                  <li><Activity size={16} /> <strong>Severity:</strong> {review.severity_pct.toFixed(0)}% affected</li>
                  <li><Activity size={16} /> <strong>Pests:</strong> None detected</li>
                </ul>
              </div>
              <div className="telemetry-block">
                <h4>Context</h4>
                <ul className="telemetry-list">
                  <li><CloudSun size={16} /> <strong>Weather:</strong> 29°C, 74% Humidity</li>
                  <li><MapPin size={16} /> <strong>Location:</strong> Anand, Gujarat</li>
                  <li><History size={16} /> <strong>History:</strong> Healthy 5 days ago</li>
                </ul>
                <div className="er-farmer-note">
                  "Spots spreading quickly after recent rain."
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 4. Zone C: Decision Form */}
        <div className="er-zone">
          <h3 className="er-zone-title">Expert Decision & Guidance Form</h3>
          
          <div className="er-form-group">
            <label>1. Diagnostic Verdict</label>
            <div className="er-radio-group">
              <label className={`er-radio-label ${action === 'Approve' ? 'active' : ''}`}>
                <input type="radio" name="verdict" checked={action === 'Approve'} onChange={() => setAction('Approve')} />
                Approve AI Diagnosis
              </label>
              <label className={`er-radio-label ${action === 'Override / Correct Findings' ? 'active' : ''}`}>
                <input type="radio" name="verdict" checked={action === 'Override / Correct Findings'} onChange={() => setAction('Override / Correct Findings')} />
                Override / Correct Findings
              </label>
              <label className={`er-radio-label ${action === 'Request Rescan' ? 'active' : ''}`}>
                <input type="radio" name="verdict" checked={action === 'Request Rescan'} onChange={() => setAction('Request Rescan')} />
                Request Rescan (Unusable Image)
              </label>
            </div>
          </div>

          {action === "Override / Correct Findings" && (
            <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} style={{ overflow: "hidden" }}>
              <div className="er-form-group">
                <label>Corrected Disease:</label>
                <select className="er-input" value={correctedDisease} onChange={(e) => setCorrectedDisease(e.target.value)}>
                  <option value="">Select Disease...</option>
                  <option value="Early Blight">Early Blight</option>
                  <option value="Late Blight">Late Blight</option>
                  <option value="Fusarium Wilt">Fusarium Wilt</option>
                  <option value="Nutrient Deficiency">Nutrient Deficiency</option>
                </select>
              </div>
              <div className="er-form-group">
                <label>Corrected Severity:</label>
                <select className="er-input" value={correctedSeverity} onChange={(e) => setCorrectedSeverity(e.target.value)}>
                  <option value="">Select Severity...</option>
                  <option value="Healthy">Healthy (0%)</option>
                  <option value="Mild">Mild (&lt;25%)</option>
                  <option value="Moderate">Moderate (25-50%)</option>
                  <option value="Severe">Severe (&gt;50%)</option>
                </select>
              </div>
              <div className="er-form-group">
                <label>Pest Confirmation:</label>
                <label className="er-checkbox-label">
                  <input type="checkbox" checked={pestVerified} onChange={(e) => setPestVerified(e.target.checked)} />
                  Pest presence verified
                </label>
              </div>
            </motion.div>
          )}

          <div className="er-form-group" style={{ marginTop: "2rem" }}>
            <label>2. Farmer Guidance (Verified)</label>
            <div style={{ marginBottom: "1rem" }}>
              <label style={{ fontSize: "0.85rem", color: "#666" }}>Immediate Action:</label>
              <input type="text" className="er-input" placeholder="e.g. Remove infected lower leaves" value={immediateAction} onChange={(e) => setImmediateAction(e.target.value)} />
            </div>
            <div>
              <label style={{ fontSize: "0.85rem", color: "#666" }}>Treatment & Dosage:</label>
              <input type="text" className="er-input" placeholder="e.g. Apply copper oxychloride @ 2g/L" value={treatment} onChange={(e) => setTreatment(e.target.value)} />
            </div>
          </div>

          <div className="er-form-group" style={{ marginTop: "2rem" }}>
            <label>3. Internal Audit (MLOps)</label>
            <label className="er-checkbox-label" style={{ marginBottom: "1rem" }}>
              <input type="checkbox" checked={addToRetraining} onChange={(e) => setAddToRetraining(e.target.checked)} />
              Flag as High-Value Ground Truth for Retraining
            </label>
            <textarea className="er-input" rows={2} placeholder="Notes for model retraining team..." value={internalNote} onChange={(e) => setInternalNote(e.target.value)} />
          </div>

          <div className="er-form-actions">
            <button className="er-btn er-btn-secondary" onClick={() => navigate("/admin/expert")}>Cancel</button>
            <button className="er-btn er-btn-primary" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
              {mutation.isPending ? "Submitting..." : "Submit Review"}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
