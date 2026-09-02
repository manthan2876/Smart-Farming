import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { getPrediction } from "../api/predictions";
import { request } from "../api/client";
import { motion } from "motion/react";
import { Loader2 } from "lucide-react";
import imageCompression from "browser-image-compression";
import "../styles/ResultPage.css";
import "../styles/DashboardPage.css"; // Ensure standard utilities exist


export default function PredictionResultPage() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const navigate = useNavigate();
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [farmerNote, setFarmerNote] = useState("");

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selected = e.target.files[0];
      try {
        setIsUploading(true);
        const options = {
          maxSizeMB: 1,
          maxWidthOrHeight: 1440,
          useWebWorker: true,
        };
        const compressedFile = await imageCompression(selected, options);
        setSelectedFile(compressedFile);
      } catch (err) {
        console.error("Compression error:", err);
      } finally {
        setIsUploading(false);
      }
    }
  };

  const handleRescanSubmit = async () => {
    if (!selectedFile || !token || !id) return;
    setIsUploading(true);
    try {
      const { rescan } = await import("../api/predictions");
      const newPred = await rescan(id, selectedFile, token);
      
      await refetch();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      console.error(err);
      alert("Failed to upload new photo.");
    } finally {
      setIsUploading(false);
      setSelectedFile(null);
    }
  };

  const { data: prediction, isLoading, isError, refetch } = useQuery({
    queryKey: ["prediction", id],
    queryFn: () => getPrediction(id as string, token!),
    refetchInterval: (query) => {
      const p = query.state.data;
      if (!p) return false;
      const latest = p.follow_up || p;
      if ((latest.status as any)?.pipeline === "processing" || (latest.status as any)?.preprocessing === "processing") return 2000;
      return false;
    }
  });

  const submitFeedback = async (correct: boolean) => {
    setIsCorrect(correct);
    try {
      await request("/feedback", {
        method: "POST",
        body: JSON.stringify({
          prediction_id: Number(id),
          is_correct: correct,
          farmer_note: farmerNote
        })
      }, token!);
      setFeedbackSubmitted(true);
    } catch (e) {
      console.error("Feedback submission failed", e);
    }
  };

  if (isLoading) return <div className="result-page loading skeleton" style={{ height: '600px' }}></div>;
  if (isError || !prediction) return <div className="result-page error">Failed to load prediction details.</div>;

  const primary = prediction.follow_up || prediction;
  const old = prediction.follow_up ? prediction : null;
  const isPendingReview = (primary.status as any)?.expert_review === "pending";
  const isProcessing = (primary.status as any)?.pipeline === "processing" || (primary.status as any)?.preprocessing === "processing";

  const renderPredictionBlock = (pred: any, isOld: boolean = false) => {
    const rawImageUrl = pred.image?.raw_path ? `http://localhost:8000/${pred.image.raw_path}` : null;
    const processedImageUrl = pred.image?.processed_path ? `http://localhost:8000/${pred.image.processed_path}` : null;
    
    return (
      <div style={{ marginTop: isOld ? "1rem" : "0" }}>
        {pred.expert_review_data && (
          <div style={{ background: "#e0f2fe", border: "1px solid #bae6fd", padding: "1.5rem", borderRadius: "12px", marginBottom: "2rem", color: "#0369a1" }}>
            <h3 style={{ margin: "0 0 0.5rem 0" }}>Verified by Agricultural Specialist</h3>
            <p style={{ margin: "0 0 1rem 0" }}><strong>Decision:</strong> {pred.expert_review_data.decision}</p>
            {pred.expert_review_data.corrected_disease && (
              <p style={{ margin: "0 0 1rem 0" }}><strong>Corrected Diagnosis:</strong> {pred.expert_review_data.corrected_disease}</p>
            )}
            {pred.expert_review_data.farmer_guidance && (
              <div>
                <strong>Agronomic Guidance:</strong>
                <p style={{ margin: "0.5rem 0 0 0", whiteSpace: "pre-wrap" }}>{pred.expert_review_data.farmer_guidance}</p>
              </div>
            )}
            
            {!isOld && pred.expert_review_data.decision === "Request New Photo" && !prediction.follow_up && (
              <div style={{ marginTop: "1.5rem", padding: "1.5rem", background: "#fff", borderRadius: "8px", border: "1px dashed #7dd3fc" }}>
                <h4 style={{ margin: "0 0 1rem 0" }}>Upload Follow-up Photo</h4>
                <p style={{ margin: "0 0 1rem 0", fontSize: "0.9rem" }}>The specialist requested a clearer photo. Please upload a new image of the affected plant to rescan.</p>
                <div style={{ display: "flex", gap: "1rem" }}>
                  <input 
                    type="file" 
                    accept="image/jpeg, image/png, image/webp"
                    onChange={handleFileChange}
                    style={{ flex: 1, padding: "0.5rem" }}
                  />
                  <button 
                    className="btn btn-glow" 
                    onClick={handleRescanSubmit}
                    disabled={!selectedFile || isUploading}
                    style={{ padding: "0.5rem 1.5rem" }}
                  >
                    {isUploading ? "Uploading..." : "Submit New Photo"}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="result-grid">
          <div className="image-panel">
            <h3>Visual Analysis</h3>
            <div className="image-comparison">
              <div className="img-box">
                <span>Original Upload</span>
                {rawImageUrl && <img src={rawImageUrl} alt="Raw Leaf" />}
              </div>
              <div className="img-box">
                <span className="gradcam-label">Grad-CAM / Heatmap</span>
                {processedImageUrl && <img src={processedImageUrl} alt="Grad-CAM Processed" />}
              </div>
            </div>
          </div>

          <div className="info-panel">
            <h3>Diagnostic Telemetry</h3>
            <div className="diagnosis-block">
              <h2>{(pred.status as any)?.expert_review === "pending" ? "Pending Verification" : (pred.disease?.label || "Unknown")}</h2>
              <p>Confidence: {( (pred.disease?.confidence || 0) * 100 ).toFixed(1)}%</p>
              <div className="confidence-bar-bg">
                <div className="confidence-bar-fill" style={{ width: `${(pred.disease?.confidence || 0) * 100}%` }}></div>
              </div>
            </div>

            <div className="diagnosis-block">
              <h2>Severity: {pred.severity?.bucket || "N/A"}</h2>
              <p>Affected Area: {pred.severity?.percent || 0}%</p>
              <div className="confidence-bar-bg">
                <div className="confidence-bar-fill" style={{ width: `${pred.severity?.percent || 0}%`, background: '#e1fc84' }}></div>
              </div>
            </div>
            
            <div style={{ marginTop: "1rem", fontFamily: "monospace", color: "#728079", fontSize: "0.85rem" }}>
              <p><strong>CROP:</strong> {pred.crop?.label?.toUpperCase() || "N/A"}</p>
              <p><strong>PESTS:</strong> {pred.pests && pred.pests.length > 0 ? pred.pests.map((p: any) => p.label).join(", ") : "None detected"}</p>
            </div>
          </div>

          {pred.recommendation && (pred.status as any)?.expert_review !== "pending" && (
            <div className="advisory-panel">
              <h3>LLM Advisory Plan</h3>
              <div className="advisory-content">
                {pred.recommendation.fertilizer && <p><strong>Fertilizer:</strong> {pred.recommendation.fertilizer}</p>}
                {pred.recommendation.pesticide && <p><strong>Pesticide:</strong> {pred.recommendation.pesticide}</p>}
                {pred.recommendation.irrigation && <p><strong>Irrigation:</strong> {pred.recommendation.irrigation}</p>}
                {pred.recommendation.prevention_tips && <p><strong>Prevention:</strong> {pred.recommendation.prevention_tips}</p>}
              </div>
              {prediction.recommendation?.safety_disclaimer && (
                <div style={{ marginTop: "1.5rem", padding: "1rem", background: "#fef2f2", borderLeft: "4px solid #ef4444", borderRadius: "0 8px 8px 0", fontSize: "0.85rem", color: "#991b1b" }}>
                  <strong>Important:</strong> {prediction.recommendation.safety_disclaimer}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <>
      {isUploading && (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(255,255,255,0.95)", zIndex: 9999, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <Loader2 size={64} className="animate-spin" color="#10b981" />
          <h2 style={{ marginTop: "2rem", color: "#0F3D2E", fontSize: "2rem" }}>Re-running AI Pipeline...</h2>
          <p style={{ color: "#666", fontSize: "1.2rem" }}>Analyzing your follow-up photo.</p>
        </div>
      )}
      <motion.div className="result-page" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="page-header">
          <Link to="/history" className="back-link">&larr; BACK TO HISTORY</Link>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h1>Scan #{primary.prediction_id || id} Diagnosis {old && <span style={{fontSize: "1.2rem", color: "var(--green)", marginLeft: "1rem"}}>(Follow-up)</span>}</h1>
          </div>
        </div>

        {isPendingReview && (
          <div style={{ background: "#fff3cd", border: "1px solid #ffeeba", padding: "1.5rem", borderRadius: "12px", marginBottom: "2rem", color: "#856404" }}>
            <h3 style={{ margin: "0 0 0.5rem 0" }}>Additional Review Required</h3>
            <p style={{ margin: 0 }}>The system could not diagnose this condition with sufficient confidence. Your crop scan has been routed to an agricultural specialist to verify the issue and ensure safe recommendations. You will be notified once verified.</p>
          </div>
        )}

        {primary.historical_images && primary.historical_images.length > 0 && (
          <div style={{ marginBottom: "2rem", padding: "1.5rem", background: "#f8fafc", borderRadius: "12px", border: "1px solid #cbd5e1" }}>
            <h3 style={{ margin: "0 0 1rem 0", color: "#334155" }}>Disease Progression Timeline</h3>
            <div style={{ display: "flex", alignItems: "center", gap: "1rem", overflowX: "auto", paddingBottom: "0.5rem" }}>
              {primary.historical_images.map((h: any, i: number) => (
                <div key={i} style={{ display: "flex", alignItems: "center" }}>
                  <div style={{ padding: "1rem", background: "#fff", border: "1px solid #e2e8f0", borderRadius: "8px", minWidth: "150px" }}>
                    <div style={{ fontSize: "0.8rem", color: "#64748b" }}>{new Date(h.created_at).toLocaleDateString()}</div>
                    <div style={{ fontWeight: "bold", color: "#0f172a", margin: "0.25rem 0" }}>{h.disease}</div>
                    <div style={{ fontSize: "0.85rem", color: h.severity_pct > 60 ? "#ef4444" : "#10b981" }}>Sev: {h.severity_pct}%</div>
                  </div>
                  <div style={{ width: "30px", height: "2px", background: "#cbd5e1", margin: "0 0.5rem" }}></div>
                </div>
              ))}
              <div style={{ display: "flex", alignItems: "center" }}>
                <div style={{ padding: "1rem", background: "#e0f2fe", border: "2px solid #38bdf8", borderRadius: "8px", minWidth: "150px" }}>
                  <div style={{ fontSize: "0.8rem", color: "#0369a1", fontWeight: "bold" }}>Latest Scan</div>
                  <div style={{ fontWeight: "bold", color: "#0f172a", margin: "0.25rem 0" }}>{primary.disease?.label || "Unknown"}</div>
                  <div style={{ fontSize: "0.85rem", color: (primary.severity?.percent || 0) > 60 ? "#ef4444" : "#10b981" }}>Sev: {primary.severity?.percent || 0}%</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Render Primary (Newest) Prediction */}
        {isProcessing ? <div style={{ padding: "4rem", textAlign: "center", background: "#f8fafc", borderRadius: "16px", border: "1px solid #e2e8f0" }}><Loader2 size={48} className="animate-spin" style={{ margin: "0 auto", color: "#10b981" }} /><h2 style={{ marginTop: "1.5rem", color: "#0F3D2E" }}>Running AI Pipeline...</h2><p style={{ color: "#666" }}>Analyzing your crop image in the background. Please wait.</p></div> : renderPredictionBlock(primary, false)}

        {/* Render Old (Original) Prediction as a collapsible section if it exists */}
        {old && (
          <div style={{ marginTop: "3rem", padding: "2rem", background: "#f8fafc", borderRadius: "16px", border: "1px solid #e2e8f0" }}>
            <details style={{ cursor: "pointer" }}>
              <summary style={{ fontSize: "1.2rem", fontWeight: "bold", color: "#475569" }}>View Original Prediction Details</summary>
              <div style={{ marginTop: "2rem", cursor: "default" }}>
                {renderPredictionBlock(old, true)}
              </div>
            </details>
          </div>
        )}

        {!isPendingReview && (
          <div style={{ marginTop: "3rem", padding: "2rem", background: "#fff", borderRadius: "16px", border: "1px solid var(--line)" }}>
            <h3 style={{ marginTop: 0 }}>Farmer Field Feedback</h3>
            {feedbackSubmitted ? (
              <div style={{ padding: "1rem", background: "var(--green)", color: "#fff", borderRadius: "8px", fontWeight: 500 }}>
                Thank you for verifying this diagnosis. Your feedback helps improve the AI for everyone!
              </div>
            ) : (
              <div>
                <p style={{ color: "var(--muted)", marginBottom: "1.5rem" }}>Did this diagnosis match what you observed in the field? Help us improve the model by validating the result.</p>
                <textarea 
                  placeholder="Optional notes (e.g. 'Spots spread after rain' or 'Extension officer said it was blight')"
                  value={farmerNote}
                  onChange={e => setFarmerNote(e.target.value)}
                  style={{ width: "100%", padding: "12px", borderRadius: "8px", border: "1px solid var(--line)", minHeight: "80px", marginBottom: "1rem", fontFamily: "inherit" }}
                />
                <div style={{ display: "flex", gap: "1rem" }}>
                  <button onClick={() => submitFeedback(true)} style={{ flex: 1, padding: "12px", background: "#e4eee4", color: "var(--green)", border: "none", borderRadius: "8px", fontWeight: "bold", cursor: "pointer" }}>✅ Yes, Accurate</button>
                  <button onClick={() => submitFeedback(false)} style={{ flex: 1, padding: "12px", background: "#fdf2f2", color: "#b44c3c", border: "none", borderRadius: "8px", fontWeight: "bold", cursor: "pointer" }}>❌ No, Incorrect</button>
                </div>
              </div>
            )}
          </div>
        )}
      </motion.div>
    </>
  );
}
