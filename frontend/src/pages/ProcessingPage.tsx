import { useState, useEffect } from 'react';
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useQuery } from "@tanstack/react-query";
import { getPrediction } from "../api/predictions";
import { motion } from "motion/react";
import { Loader2, Check, Wheat, Leaf, TreeDeciduous, Sprout, Clover, Bug, Activity, Sparkles, Wand2 } from "lucide-react";

export default function ProcessingPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const predictionId = Number(id);
  const { token } = useAuth();

  const { data: prediction, error } = useQuery({
    queryKey: ["prediction", predictionId],
    queryFn: () => getPrediction(String(predictionId), token || ''),
    enabled: !isNaN(predictionId),
    refetchInterval: (query) => {
      const p = query.state.data;
      if (!p) return 800;
      const latest = p.follow_up || p;
      if ((latest.status as any)?.pipeline === "processing" || (latest.status as any)?.preprocessing === "processing") return 800;
      return false;
    }
  });

  const [activeCropIdx, setActiveCropIdx] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setActiveCropIdx(prev => (prev + 1) % 5), 400);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (prediction) {
      const latest = prediction.follow_up || prediction;
      const isProcessing = (latest.status as any)?.pipeline === "processing" || (latest.status as any)?.preprocessing === "processing";
      
      // If it's no longer processing, wait 1.5s for the user to see the final "Advisory Ready" state, then navigate

      if (!isProcessing) {
        navigate(`/predictions/${predictionId}`, { replace: true });
      }
    }
  }, [prediction, navigate, predictionId]);


  const targetPred = prediction?.follow_up || prediction;
  const statusDict: any = targetPred?.status || {};
  
  const isPreprocDone = statusDict.preprocessing === "completed";
  const isCropDone = statusDict.crop_identification === "completed";
  const isDiseaseDone = statusDict.disease_classification === "completed";
  const isPestDone = statusDict.pest_detection === "completed";
  const isAdvisoryDone = statusDict.recommendation === "completed";

  const cropLabel = targetPred?.crop?.label;
  const diseaseLabel = targetPred?.disease?.label;
  const pestLabel = targetPred?.pests && targetPred.pests.length > 0 ? targetPred.pests[0].label : (isPestDone ? "No Pests" : null);

  const CROP_ICONS = [<Wheat size={20}/>, <Leaf size={20}/>, <TreeDeciduous size={20}/>, <Sprout size={20}/>, <Clover size={20}/>];

  if (error) {
    return (
      <div style={{ padding: "4rem", textAlign: "center", color: "#b44c3c" }}>
        <h2>Error Loading Status</h2>
        <p>Something went wrong. Please check your network connection.</p>
        <button onClick={() => navigate("/dashboard")} style={{ padding: "10px 20px", background: "#e4eee4", color: "#10b981", border: "none", borderRadius: "8px", fontWeight: "bold", cursor: "pointer", marginTop: "1rem" }}>Back to Dashboard</button>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <div style={{ padding: "3rem", background: "#f8fafc", borderRadius: "16px", border: "1px solid #e2e8f0", overflow: "hidden" }}>
        <div style={{ textAlign: "center", marginBottom: "3rem" }}>
          <Loader2 size={48} className="animate-spin" style={{ margin: "0 auto", color: "#10b981" }} />
          <h2 style={{ marginTop: "1.5rem", color: "#1e293b" }}>Running AI Pipeline</h2>
          <p style={{ color: "#64748b" }}>Analyzing your crop and generating diagnostics in real-time...</p>
        </div>
        
        <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
          {/* Stage 1: Preprocessing */}
          <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
            <div style={{ background: "#10b981", color: "#fff", width: 44, height: 44, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <Check size={24} />
            </div>
            <div>
              <h4 style={{ margin: 0, color: "#1e293b", fontSize: "1.1rem" }}>1. Image Preprocessing</h4>
              <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.9rem", color: "#64748b" }}>Verified leaf presence and clarity.</p>
            </div>
          </div>

          {/* Stage 2: Crop ID */}
          <div style={{ display: "flex", alignItems: "center", gap: "1.5rem", opacity: 1 }}>
            <div style={{ background: isCropDone ? "#10b981" : "#e0f2fe", color: isCropDone ? "#fff" : "#0284c7", width: 44, height: 44, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              {isCropDone ? <Check size={24} /> : CROP_ICONS[activeCropIdx]}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <h4 style={{ margin: 0, color: "#1e293b", fontSize: "1.1rem" }}>2. Crop Identification</h4>
              {!isCropDone ? (
                <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginTop: "0.5rem" }}>
                  <span style={{ fontSize: "0.9rem", color: "#64748b" }}>Scanning species...</span>
                </div>
              ) : (
                <p style={{ margin: "0.25rem 0 0 0", fontSize: "1rem", color: "#10b981", fontWeight: 600 }}>Detected: {cropLabel}</p>
              )}
            </div>
          </div>

          {/* Stage 3: Disease */}
          <div style={{ display: "flex", alignItems: "center", gap: "1.5rem", opacity: isCropDone ? 1 : 0.4 }}>
            <div style={{ background: isDiseaseDone ? "#10b981" : (isCropDone ? "#e0f2fe" : "#e2e8f0"), color: isDiseaseDone ? "#fff" : "#0284c7", width: 44, height: 44, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
               {isDiseaseDone ? <Check size={24} /> : (isCropDone ? <Loader2 size={24} className="animate-spin" /> : "3")}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <h4 style={{ margin: 0, color: "#1e293b", fontSize: "1.1rem" }}>3. Disease Classification</h4>
              {isCropDone && !isDiseaseDone && <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginTop: "0.5rem" }}><div className="skeleton" style={{ width: "100px", height: "10px" }}/> <span style={{ fontSize: "0.9rem", color: "#64748b", whiteSpace: "nowrap" }}>Analyzing pathology...</span></div>}
              {isDiseaseDone && <p style={{ margin: "0.25rem 0 0 0", fontSize: "1rem", color: "#db7446", fontWeight: 600 }}>Identified: {diseaseLabel || "Unknown"}</p>}
            </div>
          </div>

          {/* Stage 4: Pest */}
          <div style={{ display: "flex", alignItems: "center", gap: "1.5rem", opacity: isDiseaseDone ? 1 : 0.4 }}>
            <div style={{ background: isPestDone ? "#10b981" : (isDiseaseDone ? "#e0f2fe" : "#e2e8f0"), color: isPestDone ? "#fff" : "#0284c7", width: 44, height: 44, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
               {isPestDone ? <Check size={24} /> : (isDiseaseDone ? <Loader2 size={24} className="animate-spin" /> : "4")}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <h4 style={{ margin: 0, color: "#1e293b", fontSize: "1.1rem" }}>4. Pest Detection</h4>
              {isDiseaseDone && !isPestDone && <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginTop: "0.5rem" }}><div className="skeleton" style={{ width: "100px", height: "10px" }}/> <span style={{ fontSize: "0.9rem", color: "#64748b", whiteSpace: "nowrap" }}>Scanning for insects...</span></div>}
              {isPestDone && <p style={{ margin: "0.25rem 0 0 0", fontSize: "1rem", color: "#db7446", fontWeight: 600 }}>Result: {pestLabel}</p>}
            </div>
          </div>

          {/* Stage 5: Advisory */}
          <div style={{ display: "flex", alignItems: "center", gap: "1.5rem", opacity: isPestDone ? 1 : 0.4 }}>
            <div style={{ background: isAdvisoryDone ? "#10b981" : (isPestDone ? "#e0f2fe" : "#e2e8f0"), color: isAdvisoryDone ? "#fff" : "#0284c7", width: 44, height: 44, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
               {isAdvisoryDone ? <Check size={24} /> : (isPestDone ? <Sparkles size={24} className="animate-pulse" /> : "5")}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <h4 style={{ margin: 0, color: "#1e293b", fontSize: "1.1rem" }}>5. Advisory Generation</h4>
              {isPestDone && !isAdvisoryDone && <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginTop: "0.5rem", color: "#8b5cf6" }}><Sparkles size={20} className="animate-pulse" /> <span style={{ fontSize: "0.9rem", fontStyle: "italic", whiteSpace: "nowrap" }}>Synthesizing expert recommendations...</span></div>}
              {isAdvisoryDone && <p style={{ margin: "0.25rem 0 0 0", fontSize: "1rem", color: "#10b981", fontWeight: 600 }}>Advisory Ready.</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
