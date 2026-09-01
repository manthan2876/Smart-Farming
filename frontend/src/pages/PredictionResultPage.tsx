import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { ArrowLeft, CheckCircle2, XCircle, ShieldCheck, Bug, CloudSun, Sparkles, MessageSquare } from "lucide-react";
import { motion } from "framer-motion";

export default function PredictionResultPage() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [farmerNote, setFarmerNote] = useState("");
  const [, setIsCorrect] = useState<boolean | null>(null);

  const { data: prediction, isLoading, error } = useQuery({
    queryKey: ["prediction", id],
    queryFn: () => request<any>(`/predictions/${id}`, {}, token!),
    enabled: !!token && !!id,
  });

const feedbackMutation = useMutation({
    mutationFn: async (correct: boolean) => {
      return request("/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prediction_id: Number(id),
          is_correct: correct,
          farmer_note: farmerNote,
        }),
      }, token!);
    },
    onSuccess: () => {
      setFeedbackSubmitted(true);
    },
  });

  if (isLoading) {
    return (
      <div className="loading-state-container">
        <div className="spinner"></div>
        <p>Loading full diagnostic snapshot...</p>
      </div>
    );
  }

  if (error || !prediction) {
    return (
      <div className="error-state-container">
        <h2>Diagnostic record not found</h2>
        <p>Could not retrieve telemetry for this scan ID.</p>
        <Link to="/dashboard" className="btn btn-primary">Return to Dashboard</Link>
      </div>
    );
  }

  // Extract nested properties safely matching your schema structure
  const cropName = prediction.crop?.label || prediction.crop?.name || "Unknown Crop";
  const diseaseName = prediction.disease?.label || prediction.disease?.name || "Unidentified Condition";
  const confidence = prediction.disease?.confidence ?? prediction.confidence;
  
  const rawSeverity = prediction.severity;
  const severityText = typeof rawSeverity === "object" && rawSeverity !== null
    ? (rawSeverity.bucket || rawSeverity.level || rawSeverity.name || "Unknown")
    : String(rawSeverity || "Unknown");

  const recommendation = prediction.recommendation;
  const weather = prediction.weather;
  const pests = prediction.pests || [];
  const imageUrl = prediction.image?.raw_path;
  const processedImageUrl = prediction.image?.processed_path;

  // Safe confidence calculation
  const safeConfidence = confidence != null ? (Number(confidence) * 100).toFixed(1) : "N/A";

  return (
    <div className="prediction-result-page">
      <div className="result-topbar">
        <Link to="/dashboard" className="back-link"><ArrowLeft size={16} /> Back to Dashboard</Link>
        <span className="timestamp-badge">Scan ID: {id ? id.slice(0, 8) : "N/A"}...</span>
      </div>

      <motion.div 
        className="result-container"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {/* Header Summary Card */}
        <div className="result-hero-card">
          <div className="hero-primary-info">
            <span className="crop-tag">{cropName}</span>
            <h1 className="disease-title">{diseaseName}</h1>
            <div className="metrics-badges">
              <span className={`severity-badge ${severityText.toLowerCase()}`}>
                Severity: {severityText}
              </span>
              <span className="confidence-badge">
                <ShieldCheck size={16} /> {safeConfidence}% Confidence
              </span>
            </div>
          </div>

          <div className="images-preview-grid">
            {imageUrl && (
              <div className="img-box">
                <span className="img-label">Original Leaf Scan</span>
                <img src={`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/${imageUrl}`} alt="Original Leaf" />
              </div>
            )}
            {processedImageUrl && (
              <div className="img-box">
                <span className="img-label">Grad-CAM / Processed Overlay</span>
                <img src={`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/${processedImageUrl}`} alt="Grad-CAM Overlay" />
              </div>
            )}
          </div>
        </div>

        {/* Telemetry & Pest Row */}
        <div className="result-subgrid">
          {pests.length > 0 && (
            <div className="card pest-alert-card">
              <h3><Bug size={18} className="text-danger" /> Pests / Risk Factors Detected</h3>
              <ul>
                {pests.map((pest: any, idx: number) => (
                  <li key={idx}>{pest.label || pest.name || "Pest identified"} ({((pest.confidence || 0) * 100).toFixed(1)}%)</li>
                ))}
              </ul>
            </div>
          )}

          {weather && (
            <div className="card weather-snap-card">
              <h3><CloudSun size={18} /> Weather Context</h3>
              <div className="weather-snap-stats">
                <span>Temp: <strong>{weather.temperature_celsius ?? weather.temperature ?? "N/A"}°C</strong></span>
                <span>Humidity: <strong>{weather.humidity_percent ?? weather.humidity ?? "N/A"}%</strong></span>
              </div>
            </div>
          )}
        </div>

        {/* LLM Recommendation Section */}
        <div className="card recommendations-card">
          <h3><Sparkles size={18} className="text-warning" /> Tailored AI Advisory & Recommendations</h3>
          <div className="recommendation-content">
            {!recommendation ? (
              <p>No specific recommendations available for this scan.</p>
            ) : typeof recommendation === "string" ? (
              <p>{recommendation}</p>
            ) : (
              <div className="structured-recs">
                {recommendation.fertilizer && (
                  <div className="rec-section">
                    <h4>Recommended Fertilizers / Treatment</h4>
                    <p>{recommendation.fertilizer}</p>
                  </div>
                )}
                {recommendation.pesticide && (
                  <div className="rec-section">
                    <h4>Pesticide / Spray Protocol</h4>
                    <p>{recommendation.pesticide}</p>
                  </div>
                )}
                {recommendation.irrigation && (
                  <div className="rec-section">
                    <h4>Irrigation Guidelines</h4>
                    <p>{recommendation.irrigation}</p>
                  </div>
                )}
                {recommendation.prevention_tips && (
                  <div className="rec-section">
                    <h4>Preventative Measures</h4>
                    <p>{recommendation.prevention_tips}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Farmer Feedback Section */}
        <div className="card feedback-card">
          <h3><MessageSquare size={18} /> Help Us Improve</h3>
          <p>Was this AI disease diagnosis accurate for your crop?</p>

          {feedbackSubmitted ? (
            <div className="feedback-success-banner">
              <CheckCircle2 size={20} className="text-success" />
              <span>Thank you! Your feedback has been recorded for model MLOps tracking.</span>
            </div>
          ) : (
            <div className="feedback-form-controls">
              <textarea 
                placeholder="Optional notes or corrections for expert review..."
                value={farmerNote}
                onChange={(e) => setFarmerNote(e.target.value)}
                className="form-control"
                rows={2}
              />
              <div className="feedback-action-buttons">
                <button 
                  onClick={() => { setIsCorrect(true); feedbackMutation.mutate(true); }}
                  className="btn btn-success"
                  disabled={feedbackMutation.isPending}
                >
                  <CheckCircle2 size={16} /> Correct Diagnosis
                </button>
                <button 
                  onClick={() => { setIsCorrect(false); feedbackMutation.mutate(false); }}
                  className="btn btn-danger"
                  disabled={feedbackMutation.isPending}
                >
                  <XCircle size={16} /> Incorrect / Needs Review
                </button>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}