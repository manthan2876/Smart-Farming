import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { getPrediction } from "../api/predictions";
import { motion } from "motion/react";
import "../styles/ResultPage.css";

export default function PredictionResultPage() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();

  const { data: prediction, isLoading, isError } = useQuery({
    queryKey: ["prediction", id],
    queryFn: () => getPrediction(id as string, token!),
    enabled: !!id && !!token,
  });

  if (isLoading) return <div className="result-page"><p>Loading diagnosis...</p></div>;
  if (isError || !prediction) return <div className="result-page"><p>Error loading prediction.</p></div>;

  const rawImageUrl = prediction.image?.raw_path ? `http://localhost:8000/` + prediction.image.raw_path : "";
  const processedImageUrl = prediction.image?.processed_path ? `http://localhost:8000/` + prediction.image.processed_path : "";

  return (
    <motion.div className="result-page" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div className="result-header">
        <Link to="/history" className="back-link">← BACK TO HISTORY</Link>
        <h1>Scan #{id} Diagnosis</h1>
      </div>

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
          <div style={{ marginTop: "1.5rem", padding: "1rem", background: "#fdfdf9", borderRadius: "12px", border: "1px solid #eee", fontSize: "0.9rem", color: "#444" }}>
            <strong style={{ display: "block", marginBottom: "0.5rem", color: "#0F3D2E" }}>Heatmap Legend:</strong>
            <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <div style={{ width: "16px", height: "16px", background: "blue", borderRadius: "4px" }}></div>
                <span><strong>Blue:</strong> Diseased Areas</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <div style={{ width: "16px", height: "16px", background: "#228B22", borderRadius: "4px" }}></div>
                <span><strong>Green/Yellow:</strong> Healthy Tissue</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <div style={{ width: "16px", height: "16px", background: "red", borderRadius: "4px" }}></div>
                <span><strong>Red:</strong> Background / Edges</span>
              </div>
            </div>
          </div>
        </div>

        <div className="info-panel">
          <h3>Diagnostic Telemetry</h3>
          <div className="diagnosis-block">
            <h2>{prediction.disease?.label || "Unknown"}</h2>
            <p>Confidence: {( (prediction.disease?.confidence || 0) * 100 ).toFixed(1)}%</p>
            <div className="confidence-bar-bg">
              <div className="confidence-bar-fill" style={{ width: `${(prediction.disease?.confidence || 0) * 100}%` }}></div>
            </div>
          </div>

          <div className="diagnosis-block">
            <h2>Severity: {prediction.severity?.bucket || "N/A"}</h2>
            <p>Affected Area: {prediction.severity?.percent || 0}%</p>
            <div className="confidence-bar-bg">
              <div className="confidence-bar-fill" style={{ width: `${prediction.severity?.percent || 0}%`, background: '#e1fc84' }}></div>
            </div>
          </div>
          
          <div style={{ marginTop: "1rem", fontFamily: "monospace", color: "#728079", fontSize: "0.85rem" }}>
            <p><strong>CROP:</strong> {prediction.crop?.label?.toUpperCase() || "N/A"}</p>
            <p><strong>PESTS:</strong> {prediction.pests && prediction.pests.length > 0 ? prediction.pests.map(p => p.label).join(", ") : "None detected"}</p>
          </div>
        </div>

        {prediction.recommendation && (
          <div className="advisory-panel">
            <h3>LLM Advisory Plan</h3>
            <div className="advisory-content">
              {prediction.recommendation.fertilizer && <p><strong>Fertilizer:</strong> {prediction.recommendation.fertilizer}</p>}
              {prediction.recommendation.pesticide && <p><strong>Pesticide:</strong> {prediction.recommendation.pesticide}</p>}
              {prediction.recommendation.irrigation && <p><strong>Irrigation:</strong> {prediction.recommendation.irrigation}</p>}
              {prediction.recommendation.prevention_tips && <p><strong>Prevention:</strong> {prediction.recommendation.prevention_tips}</p>}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
