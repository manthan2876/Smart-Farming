import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { adminFeedback, reviewFeedback } from "../api/admin";
import { Badge, Button, Card, Skeleton } from "../components/ui";

export default function AdminFeedbackPage() {
  const { token, t } = useAuth();
  const queryClient = useQueryClient();

  const { data: feedbacks = [], isLoading } = useQuery({
    queryKey: ["adminFeedbackList"],
    queryFn: () => adminFeedback(token!),
    enabled: !!token,
  });

  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: "approved" | "rejected" }) => reviewFeedback(token!, id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminFeedbackList"] });
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-6 pb-12">
        <div className="space-y-2">
          <Skeleton className="h-8 w-60" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="rounded-sm border border-line bg-surface p-5 space-y-3">
              <Skeleton className="h-5 w-44" />
              <Skeleton className="h-4 w-full" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12">
      <div>
        <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("agronomistReviewDesk")}</span>
        <h1 className="mt-1 font-display text-2xl sm:text-3xl text-ink">{t("expertReviewPortal")}</h1>
        <p className="mt-1 text-xs text-muted">{t("humanInTheLoopSubtitle")}</p>
      </div>

      <div className="grid gap-4">
        {feedbacks.length === 0 ? (
          <Card><p className="text-sm text-muted">{t("noFeedbackSubmissions")}</p></Card>
        ) : (
          feedbacks.map((fb: any, index: number) => (
            <div 
              className="grid gap-5 rounded-sm border border-line bg-surface p-5 lg:grid-cols-[1fr_2fr_auto] lg:items-center" 
              key={fb.id || index}
            >
              <div>
                <h4 className="font-display text-lg text-ink">{t("prediction")} #{String(fb.prediction_id ?? "").slice(0, 8)}</h4>
                <p className="mt-1 text-xs text-muted">{t("date")}: {fb.created_at ? new Date(fb.created_at).toLocaleDateString() : "N/A"}</p>
                <div className="mt-2 text-xs text-muted flex items-center gap-1.5">
                  <span>{t("farmerVerdict")}:</span>
                  <Badge tone={fb.is_correct ? "success" : "danger"}>
                    {fb.is_correct ? t("correctVerdict") : t("incorrectVerdict")}
                  </Badge>
                </div>
                <p className="mt-1 text-xs text-muted">{t("reviewStatus")}: {fb.review_status === "pending" || !fb.review_status ? t("pending") : fb.review_status}</p>
              </div>

              <div className="rounded-xs border border-line bg-canvas p-3 text-xs leading-5 text-ink/90">
                <strong className="text-ink">{t("note")}:</strong> {fb.farmer_note || t("noFarmerNote")}
              </div>

              <div className="flex gap-2 lg:justify-end">
                <Button 
                  size="sm"
                  onClick={() => mutation.mutate({ id: fb.id, status: 'approved' })}
                  disabled={mutation.isPending}
                >
                  {t("confirm")}
                </Button>
                <Button 
                  size="sm" 
                  variant="secondary" 
                  className="border-danger text-danger hover:bg-red-50 dark:border-red-500 dark:text-red-400"
                  onClick={() => mutation.mutate({ id: fb.id, status: 'rejected' })}
                  disabled={mutation.isPending}
                >
                  {t("reject")}
                </Button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
