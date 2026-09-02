import { motion } from "motion/react";
import { Link } from "react-router-dom";
import { Sprout } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { fetchSupportedCrops } from "../api/crops";
import "../styles/WeatherCrops.css";

export default function CropsPage() {
  const { token } = useAuth();
  const { data: crops, isLoading, isError } = useQuery({
    queryKey: ["supportedCrops"],
    queryFn: () => fetchSupportedCrops(token!),
    enabled: !!token,
  });

  return (
    <motion.div className="crops-page" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div className="page-header">
        <h1>Supported Crops</h1>
        <Link to="/dashboard" className="back-btn">← Back to Dashboard</Link>
      </div>

      {isLoading && <p>Loading supported crops...</p>}
      {isError && <p>Failed to load crops from server.</p>}

      <div className="crops-grid">
        {crops?.map((cropName: string, i: number) => (
          <motion.div key={cropName} className="crop-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
            <div className="crop-icon"><Sprout size={40} /></div>
            <h3>{cropName}</h3>
            <p style={{ color: "#728079", fontFamily: "monospace", fontSize: "0.85rem", marginTop: "1rem" }}>
              Active Model Pipeline
            </p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
