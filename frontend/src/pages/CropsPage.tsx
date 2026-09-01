import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Sprout, ArrowRight, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

interface CropListResponse {
  crops: string[];
}

const fetchSupportedCrops = async (): Promise<CropListResponse> => {
  const response = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/crops`);
  if (!response.ok) {
    throw new Error("Failed to fetch supported crops");
  }
  return response.json();
};

export default function CropsPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["supportedCrops"],
    queryFn: fetchSupportedCrops,
  });

  const crops = data?.crops || [];

  return (
    <div className="crops-page-public">
      <header className="page-header text-center">
        <div className="badge-pill mb-2"><Sprout size={14} /> AI Model Catalog</div>
        <h1>Supported Crops & Disease Database</h1>
        <p>Our computer vision models are custom-trained to diagnose pest infestations and plant pathologies for the following staple crops.</p>
        <div className="header-actions mt-4">
          <Link to="/scan" className="btn btn-primary">Start Diagnostic Scan</Link>
          <Link to="/" className="btn btn-secondary">Back to Home</Link>
        </div>
      </header>

      <main className="page-content container">
        {isLoading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading supported crop inventory...</p>
          </div>
        )}

        {isError && (
          <div className="error-state card">
            <h3>Unable to load crop catalog</h3>
            <p>{error instanceof Error ? error.message : "Connection error."}</p>
            <button onClick={() => window.location.reload()} className="btn btn-outline mt-3">Try Again</button>
          </div>
        )}

        {!isLoading && !isError && crops.length === 0 && (
          <div className="empty-state card">
            <p>No crops are currently active in backend configurations.</p>
          </div>
        )}

        {!isLoading && !isError && crops.length > 0 && (
          <motion.div 
            className="crops-grid"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {crops.map((crop: string, index: number) => (
              <div key={index} className="crop-card card">
                <div className="crop-card-header">
                  <div className="crop-initial-icon">{crop.charAt(0).toUpperCase()}</div>
                  <span className="status-badge success"><ShieldCheck size={14} /> Fully Supported</span>
                </div>
                <div className="crop-card-body">
                  <h3>{crop}</h3>
                  <p>AI pipeline ready for leaf segmentation, Grad-CAM generation, and localized LLM remedy generation.</p>
                </div>
                <div className="crop-card-footer">
                  <Link to="/scan" className="link-inline">Run scan for {crop} <ArrowRight size={14} /></Link>
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </main>
    </div>
  );
}