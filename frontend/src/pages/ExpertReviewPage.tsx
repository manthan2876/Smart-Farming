import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, CheckCircle, XCircle, Camera } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getExpertReview, submitExpertReview } from "../api/expert";
import { motion } from "motion/react";
import "../styles/ResultPage.css"; // Reuse prediction layout

export default function ExpertReviewPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [action, setAction] = useState<"Approve" | "Correct Diagnosis" | "Request New Photo">("Approve");
  const [correctedDisease, setCorrectedDisease] = useState("");
  const [farmerGuidance, setFarmerGuidance] = useState("");
  const [internalNote, setInternalNote] = useState("");

  const { data: review, isLoading } = useQuery({
    queryKey: ["expertReview", id],
    queryFn: () => getExpertReview(Number(id), token!),
    enabled: !!token && !!id,
  });

  const mutation = useMutation({
    mutationFn: () => submitExpertReview(Number(id), {
      action,
      corrected_disease: action === "Correct Diagnosis" ? correctedDisease : undefined,
      farmer_guidance: farmerGuidance || undefined,
      internal_note: internalNote || undefined
    }, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expertQueue"] });
      navigate("/admin/expert");
    }
  });

  if (isLoading) return <div className="loading-state">Loading clinical review...</div>;
  if (!review) return <div className="error-state">Review not found</div>;

  return (
    <div className="prediction-result-page">
      <div className="page-header">
        <button onClick={() => navigate("/admin/expert")} className="btn-back">
          <ArrowLeft size={18} /> Back to Queue
        </button>
        <h1>Clinical Expert Review</h1>
      </div>

      <div className="result-grid">
        <div className="result-left">
          <motion.div className="result-card" initial={{opacity:0}} animate={{opacity:1}}>
            <h2>Captured Image</h2>
            <div className="image-comparison">
              <div className="image-wrapper">
                <img src={`http://127.0.0.1:8000/${review.raw_path}`} alt="Raw Crop" />
              </div>
            </div>
            <div className="prediction-summary" style={{marginTop: '2rem'}}>
              <h3>AI Diagnosis</h3>
              <p><strong>Crop:</strong> {review.crop}</p>
              <p><strong>Disease:</strong> {review.disease}</p>
              <p><strong>Confidence:</strong> {(review.disease_conf * 100).toFixed(1)}%</p>
              <p><strong>Severity:</strong> {review.severity_pct.toFixed(1)}% affected</p>
            </div>
          </motion.div>
        </div>

        <div className="result-right">
          <motion.div className="action-card" initial={{opacity:0, x:20}} animate={{opacity:1, x:0}}>
            <h2>Expert Decision</h2>
            
            <div className="form-group" style={{marginBottom: '1.5rem'}}>
              <label>Decision Action</label>
              <div style={{display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem'}}>
                <button 
                  className={`btn ${action === 'Approve' ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setAction("Approve")}
                >
                  <CheckCircle size={16} style={{marginRight: '0.5rem'}} /> Approve AI
                </button>
                <button 
                  className={`btn ${action === 'Correct Diagnosis' ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setAction("Correct Diagnosis")}
                  style={action === 'Correct Diagnosis' ? {backgroundColor: '#eab308', color: '#000'} : {}}
                >
                  <XCircle size={16} style={{marginRight: '0.5rem'}} /> Correct AI
                </button>
                <button 
                  className={`btn ${action === 'Request New Photo' ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setAction("Request New Photo")}
                >
                  <Camera size={16} style={{marginRight: '0.5rem'}} /> Request New Photo
                </button>
              </div>
            </div>

            {action === "Correct Diagnosis" && (
              <div className="form-group" style={{marginBottom: '1.5rem'}}>
                <label>Corrected Disease Name</label>
                <input 
                  type="text" 
                  className="form-input" 
                  value={correctedDisease}
                  onChange={(e) => setCorrectedDisease(e.target.value)}
                  placeholder="Enter the actual disease..."
                />
              </div>
            )}

            <div className="form-group" style={{marginBottom: '1.5rem'}}>
              <label>Agronomic Guidance for Farmer (Public)</label>
              <textarea 
                className="form-input" 
                rows={4} 
                value={farmerGuidance}
                onChange={(e) => setFarmerGuidance(e.target.value)}
                placeholder="Instructions on treatment or next steps..."
              />
            </div>

            <div className="form-group" style={{marginBottom: '1.5rem'}}>
              <label>Internal Note (MLOps / Hidden)</label>
              <textarea 
                className="form-input" 
                rows={2} 
                value={internalNote}
                onChange={(e) => setInternalNote(e.target.value)}
                placeholder="Notes for model retraining team..."
              />
            </div>

            <button 
              className="btn btn-primary" 
              style={{width: '100%', padding: '1rem', fontSize: '1.1rem'}}
              onClick={() => mutation.mutate()}
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Submitting..." : "Submit Verified Review"}
            </button>
            {mutation.isError && <p className="text-error" style={{marginTop: '1rem'}}>Failed to submit review.</p>}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
