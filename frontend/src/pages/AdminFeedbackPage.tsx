import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { adminFeedback, reviewFeedback } from "../api/admin";
import { motion } from "motion/react";
import "../styles/AdminPages.css";

export default function AdminFeedbackPage() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  const { data: feedbacks = [], isLoading } = useQuery({
    queryKey: ["adminFeedbackList"],
    queryFn: () => adminFeedback(token!),
    enabled: !!token,
  });

  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: number, status: string }) => reviewFeedback(token!, id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminFeedbackList"] });
    }
  });

  if (isLoading) return <div className="admin-page"><p>Loading expert review portal...</p></div>;

  return (
    <motion.div className="admin-page" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div className="admin-header">
        <h1>Expert Review Portal</h1>
        <p>[HUMAN IN THE LOOP - FEEDBACK VALIDATION]</p>
      </div>

      <div className="feedback-grid">
        {feedbacks.length === 0 ? (
          <p>No pending feedback submissions recorded.</p>
        ) : (
          feedbacks.map((fb: any, index: number) => (
            <motion.div className="feedback-card" key={index} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }}>
              <div className="fb-meta">
                <h4>Prediction #{String(fb.prediction_id ?? "").slice(0, 8)}</h4>
                <p>Date: {fb.created_at ? new Date(fb.created_at).toLocaleDateString() : "N/A"}</p>
                <p>Farmer Verdict: <span style={{ color: fb.is_correct ? '#10b981' : '#b44c3c', fontWeight: 'bold' }}>{fb.is_correct ? "CORRECT" : "INCORRECT"}</span></p>
              </div>
              <div className="fb-content">
                <strong>Note:</strong> {fb.farmer_note || "No note provided by farmer."}
              </div>
              <div className="fb-action">
                <button 
                  className="btn-approve" 
                  onClick={() => mutation.mutate({ id: fb.id, status: 'approved' })}
                  disabled={mutation.isPending}
                >
                  Confirm
                </button>
                <button 
                  className="btn-reject" 
                  onClick={() => mutation.mutate({ id: fb.id, status: 'rejected' })}
                  disabled={mutation.isPending}
                >
                  Reject
                </button>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </motion.div>
  );
}
