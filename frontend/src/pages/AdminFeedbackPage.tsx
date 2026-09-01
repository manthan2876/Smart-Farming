import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { adminFeedback } from "../api/admin";
import { CheckCircle2, XCircle } from "lucide-react";
import { motion } from "framer-motion";

export default function AdminFeedbackPage() {
  const { token } = useAuth();

  const { data: feedbacks = [], isLoading } = useQuery({
    queryKey: ["adminFeedbackList"],
    queryFn: () => adminFeedback(token!),
    enabled: !!token,
  });

  if (isLoading) return <div className="loading-state"><div className="spinner"></div></div>;

  return (
    <div className="admin-feedback-page">
      <div className="page-header">
        <h1>Expert Feedback Review Portal</h1>
        <p>Examine farmer-submitted verification notes and corrected labels for model retraining.</p>
      </div>

      <motion.div 
        className="card table-container"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {feedbacks.length === 0 ? (
          <p className="empty-text">No feedback submissions recorded yet.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Prediction ID</th>
                <th>Farmer Note</th>
                <th>Verdict</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
{feedbacks.map((fb: any, index: number) => (
                <tr key={index}>
                  <td><code>{String(fb.prediction_id ?? "").slice(0, 8)}...</code></td>
                  <td>{fb.farmer_note || <span className="text-muted">No note provided</span>}</td>
                  <td>
                    {fb.is_correct ? (
                      <span className="badge-success"><CheckCircle2 size={14} /> Correct</span>
                    ) : (
                      <span className="badge-danger"><XCircle size={14} /> Incorrect</span>
                    )}
                  </td>
                  <td>{fb.created_at ? new Date(fb.created_at).toLocaleDateString() : "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </motion.div>
    </div>
  );
}