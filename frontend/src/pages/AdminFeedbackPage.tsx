import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { adminFeedback, reviewFeedback } from "../api/admin";
import { motion } from "motion/react";
import { Badge, Button, Card } from "../components/ui";

export default function AdminFeedbackPage() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  const { data: feedbacks = [], isLoading } = useQuery({
    queryKey: ["adminFeedbackList"],
    queryFn: () => adminFeedback(token!),
    enabled: !!token,
  });

  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: number, status: "approved" | "rejected" }) => reviewFeedback(token!, id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminFeedbackList"] });
    }
  });

  if (isLoading) return <div className="flex min-h-[40vh] items-center justify-center text-sm text-muted">Loading expert review portal...</div>;

  return (
    <motion.div className="space-y-6 pb-12" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div>
        <h1 className="font-display text-3xl text-ink sm:text-4xl">Expert Review Portal</h1>
        <p className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-muted">[HUMAN IN THE LOOP - FEEDBACK VALIDATION]</p>
      </div>

      <div className="grid gap-5">
        {feedbacks.length === 0 ? (
          <Card><p className="text-sm text-muted">No pending feedback submissions recorded.</p></Card>
        ) : (
          feedbacks.map((fb: any, index: number) => (
            <motion.div className="grid gap-5 rounded-md border border-line bg-surface p-5 shadow-soft lg:grid-cols-[1fr_2fr_auto] lg:items-center" key={index} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }}>
              <div>
                <h4 className="font-display text-xl text-ink">Prediction #{String(fb.prediction_id ?? "").slice(0, 8)}</h4>
                <p className="mt-1 text-xs text-muted">Date: {fb.created_at ? new Date(fb.created_at).toLocaleDateString() : "N/A"}</p>
                <p className="mt-2 text-sm text-muted">Farmer Verdict: <Badge tone={fb.is_correct ? "success" : "danger"}>{fb.is_correct ? "CORRECT" : "INCORRECT"}</Badge></p>
                <p className="mt-1 text-xs text-muted">Review: {fb.review_status || "pending"}</p>
              </div>
              <div className="border-l-2 border-farmer-300 pl-4 text-sm leading-6 text-muted">
                <strong className="text-ink">Note:</strong> {fb.farmer_note || "No note provided by farmer."}
              </div>
              <div className="flex gap-2 lg:justify-end">
                <Button size="sm"
                  onClick={() => mutation.mutate({ id: fb.id, status: 'approved' })}
                  disabled={mutation.isPending}
                >
                  Confirm
                </Button>
                <Button size="sm" variant="secondary" className="border-danger text-danger"
                  onClick={() => mutation.mutate({ id: fb.id, status: 'rejected' })}
                  disabled={mutation.isPending}
                >
                  Reject
                </Button>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </motion.div>
  );
}
