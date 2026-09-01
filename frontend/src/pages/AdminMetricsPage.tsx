import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { adminMetrics } from "../api/admin";
import { ShieldAlert, Activity, CheckCircle, Award } from "lucide-react";
import { motion } from "framer-motion";

export default function AdminMetricsPage() {
  const { token } = useAuth();

  const { data: metrics, isLoading } = useQuery({
    queryKey: ["adminMetrics"],
    queryFn: () => adminMetrics(token!),
    enabled: !!token,
  });

  if (isLoading) return <div className="loading-state"><div className="spinner"></div></div>;

  return (
    <div className="admin-metrics-page">
      <div className="page-header">
        <h1>System Operations & MLOps Metrics</h1>
        <p>Real-time telemetry and pipeline accuracy diagnostics across all farmer scans.</p>
      </div>

      <motion.div 
        className="metrics-grid"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="card stat-card">
          <Activity size={24} className="text-primary" />
          <div>
            <span>Total Scans Processed</span>
            <h2>{metrics?.total_predictions ?? 0}</h2>
          </div>
        </div>
<div className="card stat-card">
          <CheckCircle size={24} className="text-success" />
          <div>
            <span>Feedback Accuracy Rate</span>
            <h2>{metrics?.accuracy_rate_pct !== null && metrics?.accuracy_rate_pct !== undefined ? `${metrics.accuracy_rate_pct}%` : "N/A"}</h2>
          </div>
        </div>
        <div className="card stat-card">
          <Award size={24} className="text-warning" />
          <div>
            <span>Avg Crop Confidence</span>
            <h2>{metrics?.avg_crop_confidence ? `${(metrics.avg_crop_confidence * 100).toFixed(1)}%` : "N/A"}</h2>
          </div>
        </div>
        <div className="card stat-card">
          <ShieldAlert size={24} className="text-danger" />
          <div>
            <span>Avg Disease Confidence</span>
            <h2>{metrics?.avg_disease_confidence ? `${(metrics.avg_disease_confidence * 100).toFixed(1)}%` : "N/A"}</h2>
          </div>
        </div>
      </motion.div>
    </div>
  );
}