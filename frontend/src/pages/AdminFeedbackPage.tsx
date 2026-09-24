import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { adminFeedback, reviewFeedback } from "../api/admin";
import { motion } from "motion/react";
import { Badge, Button, Card } from "../components/ui";

export default function AdminFeedbackPage() {
  const { token, t } = useAuth();
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

  if (isLoading) return <div className="flex min-h-[40vh] items-center justify-center text-sm text-muted">{t("loadingExpertPortal")}</div>;

  return (
    <motion.div className="space-y-6 pb-12" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div>
        <h1 className="font-display text-3xl text-ink sm:text-4xl">{t("expertReviewPortal")}</h1>
        <p className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-muted">{t("humanInTheLoopSubtitle")}</p>
      </div>

      <div className="grid gap-5">
        {feedbacks.length === 0 ? (
          <Card><p className="text-sm text-muted">{t("noFeedbackSubmissions")}</p></Card>
        ) : (
          feedbacks.map((fb: any, index: number) => (
            <motion.div className="grid gap-5 rounded-md border border-line bg-surface p-5 shadow-soft lg:grid-cols-[1fr_2fr_auto] lg:items-center" key={index} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }}>
              <div>
                <h4 className="font-display text-xl text-ink">{t("prediction")} #{String(fb.prediction_id ?? "").slice(0, 8)}</h4>
                <p className="mt-1 text-xs text-muted">{t("date")}: {fb.created_at ? new Date(fb.created_at).toLocaleDateString() : "N/A"}</p>
                <p className="mt-2 text-sm text-muted">{t("farmerVerdict")}: <Badge tone={fb.is_correct ? "success" : "danger"}>{fb.is_correct ? t("correctVerdict") : t("incorrectVerdict")}</Badge></p>
                <p className="mt-1 text-xs text-muted">{t("reviewStatus")}: {fb.review_status === "pending" || !fb.review_status ? t("pending") : fb.review_status}</p>
              </div>
              <div className="border-l-2 border-farmer-300 pl-4 text-sm leading-6 text-muted">
                <strong className="text-ink">{t("note")}:</strong> {fb.farmer_note || t("noFarmerNote")}
              </div>
              <div className="flex gap-2 lg:justify-end">
                <Button size="sm"
                  onClick={() => mutation.mutate({ id: fb.id, status: 'approved' })}
                  disabled={mutation.isPending}
                >
                  {t("confirm")}
                </Button>
                <Button size="sm" variant="secondary" className="border-danger text-danger"
                  onClick={() => mutation.mutate({ id: fb.id, status: 'rejected' })}
                  disabled={mutation.isPending}
                >
                  {t("reject")}
                </Button>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </motion.div>
  );
}
