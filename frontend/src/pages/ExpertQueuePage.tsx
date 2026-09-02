import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AlertCircle, CheckCircle, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getExpertQueue } from "../api/expert";
import { motion } from "motion/react";
import "../styles/DashboardPage.css"; // Reuse card styles

export default function ExpertQueuePage() {
  const { token } = useAuth();

  const { data: queue = [], isLoading, error } = useQuery({
    queryKey: ["expertQueue"],
    queryFn: () => getExpertQueue(token!),
    enabled: !!token,
  });

  return (
    <div className="dashboard-page">
      <div className="dashboard-welcome-banner">
        <div className="welcome-text">
          <h1>Expert Triage Queue</h1>
          <p>Review and verify uncertain diagnoses escalated by the AI system.</p>
        </div>
        <AlertCircle size={48} color="#e1fc84" />
      </div>

      <motion.div
        className="dashboard-card recent-scans-section"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="card-header">
          <h3>Pending Reviews ({queue.length})</h3>
        </div>

        {isLoading ? (
          <p>Loading queue...</p>
        ) : error ? (
          <p className="text-error">Failed to load queue.</p>
        ) : queue.length === 0 ? (
          <div className="empty-state">
            <CheckCircle size={40} color="#10b981" />
            <p>The queue is completely empty. Great job!</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Crop</th>
                  <th>AI Diagnosis</th>
                  <th>Confidence</th>
                  <th>Severity</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {queue.map((item) => (
                  <tr key={item.review_id}>
                    <td>{item.created_at ? new Date(item.created_at).toLocaleDateString() : "N/A"}</td>
                    <td><span className="crop-badge">{item.crop || "Unknown"}</span></td>
                    <td><strong>{item.disease || "Unknown"}</strong></td>
                    <td>{(item.disease_conf * 100).toFixed(1)}%</td>
                    <td>
                      <span className={`severity-indicator ${item.severity_pct > 60 ? 'severe' : item.severity_pct > 25 ? 'moderate' : 'low'}`}>
                        {item.severity_pct > 60 ? 'Severe' : item.severity_pct > 25 ? 'Moderate' : 'Low'}
                      </span>
                    </td>
                    <td>
                      <Link to={`/admin/expert/${item.review_id}`} className="btn btn-outline" style={{padding: '0.5rem 1rem', fontSize: '0.8rem'}}>
                        Review <ArrowRight size={14} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>
    </div>
  );
}
