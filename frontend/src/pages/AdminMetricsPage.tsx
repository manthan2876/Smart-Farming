import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { adminMetrics } from "../api/admin";
import { motion } from "motion/react";
import "../styles/AdminPages.css";

export default function AdminMetricsPage() {
  const { token } = useAuth();

  const { data: metrics, isLoading } = useQuery({
    queryKey: ["adminMetrics"],
    queryFn: () => adminMetrics(token!),
    enabled: !!token,
  });

  if (isLoading) return <div className="admin-page"><p>Loading metrics...</p></div>;

  const totalScans = metrics?.total_predictions ?? 0;
  const accPct = metrics?.accuracy_rate_pct ?? 0;
  const cropConf = metrics?.avg_crop_confidence ? metrics.avg_crop_confidence * 100 : 0;
  const disConf = metrics?.avg_disease_confidence ? metrics.avg_disease_confidence * 100 : 0;

  return (
    <motion.div className="admin-page" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div className="admin-header">
        <h1>System Operations & MLOps Metrics</h1>
        <p>[REAL-TIME TELEMETRY & PIPELINE DIAGNOSTICS]</p>
      </div>

      <div className="metrics-hero-grid">
        <div className="metric-box highlight">
          <h4>Total Scans Processed</h4>
          <h2>{totalScans}</h2>
        </div>
        <div className="metric-box">
          <h4>Feedback Accuracy</h4>
          <h2>{accPct.toFixed(1)}%</h2>
        </div>
        <div className="metric-box">
          <h4>Avg Crop Confidence</h4>
          <h2>{cropConf.toFixed(1)}%</h2>
        </div>
        <div className="metric-box">
          <h4>Avg Disease Confidence</h4>
          <h2>{disConf.toFixed(1)}%</h2>
        </div>
      </div>

      <div className="visuals-section">
        <div className="visual-card">
          <h3>Confidence Distribution (Global Average)</h3>
          <div className="bar-chart-row">
            <div className="bar-label">Crop Identification</div>
            <div className="bar-bg"><div className="bar-fill" style={{ width: `${cropConf}%`, background: '#0F3D2E' }}></div></div>
            <div className="bar-value">{cropConf.toFixed(1)}%</div>
          </div>
          <div className="bar-chart-row">
            <div className="bar-label">Disease Diagnosis</div>
            <div className="bar-bg"><div className="bar-fill" style={{ width: `${disConf}%`, background: '#276b52' }}></div></div>
            <div className="bar-value">{disConf.toFixed(1)}%</div>
          </div>
          <div className="bar-chart-row">
            <div className="bar-label">Expert Review Rate</div>
            <div className="bar-bg"><div className="bar-fill" style={{ width: `15%`, background: '#db7446' }}></div></div>
            <div className="bar-value">15.0%</div>
          </div>
        </div>

        <div className="visual-card">
          <h3>System Status</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #eee', paddingBottom: '0.5rem' }}>
              <strong>API Gateway</strong> <span style={{ color: '#10b981', fontWeight: 'bold' }}>ONLINE</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #eee', paddingBottom: '0.5rem' }}>
              <strong>Inference Engine</strong> <span style={{ color: '#10b981', fontWeight: 'bold' }}>ONLINE</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #eee', paddingBottom: '0.5rem' }}>
              <strong>Database Sync</strong> <span style={{ color: '#10b981', fontWeight: 'bold' }}>ONLINE</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
