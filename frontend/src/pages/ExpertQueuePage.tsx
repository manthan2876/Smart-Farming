import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AlertCircle, CheckCircle, ArrowRight } from "../components/icons";
import { useAuth } from "../context/AuthContext";
import { getExpertQueue } from "../api/expert";
import { Badge, Card, Table, Skeleton } from "../components/ui";
import { translateCrop, translateDisease } from "../i18n/domain";

export default function ExpertQueuePage() {
  const { token, t, language } = useAuth();

  const { data: queue = [], isLoading, error } = useQuery({
    queryKey: ["expertQueue"],
    queryFn: () => getExpertQueue(token!),
    enabled: !!token,
  });

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-5 rounded-sm border border-line bg-surface p-6 sm:flex-row sm:items-center sm:justify-between sm:p-8">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("specialistReviewDesk")}</span>
          <h1 className="mt-1 font-display text-2xl sm:text-3xl text-ink">{t("expertTriageQueue")}</h1>
          <p className="mt-2 text-sm leading-6 text-muted">{t("expertTriageSubtitle")}</p>
        </div>
        <div className="text-farmer-700 dark:text-farmer-300">
          <AlertCircle size={36} />
        </div>
      </div>

      <div className="rounded-sm border border-line bg-surface p-6">
        <div className="border-b border-line pb-4">
          <h3 className="font-display text-lg text-ink">
            {t("pendingReviews")} ({queue.length})
          </h3>
        </div>

        {isLoading ? (
          <div className="mt-5 space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex justify-between items-center rounded-xs border border-line p-4">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-28" />
                  <Skeleton className="h-5 w-48" />
                </div>
                <Skeleton className="h-6 w-20" />
              </div>
            ))}
          </div>
        ) : error ? (
          <p className="mt-5 text-sm text-danger">{t("failedLoadQueue")}</p>
        ) : queue.length === 0 ? (
          <div className="mt-5 flex flex-col items-center rounded-xs bg-canvas p-8 text-center text-sm text-muted border border-line">
            <CheckCircle className="text-farmer-700 dark:text-farmer-300" size={36} />
            <p className="mt-3 font-semibold text-ink">{t("queueEmpty")}</p>
            <p className="text-xs text-muted mt-1">{t("allScansTriaged")}</p>
          </div>
        ) : (
          <div className="mt-5 overflow-x-auto">
            <Table>
              <thead>
                <tr className="bg-canvas text-xs uppercase tracking-wider text-muted">
                  <th className="px-5 py-3.5 font-semibold">{t("crop")}</th>
                  <th className="px-5 py-3.5 font-semibold">{t("identifiedCondition")}</th>
                  <th className="px-5 py-3.5 font-semibold">{t("confidence")}</th>
                  <th className="px-5 py-3.5 font-semibold">{t("dateOrRequest")}</th>
                  <th className="px-5 py-3.5 font-semibold">{t("action")}</th>
                </tr>
              </thead>
              <tbody>
                {queue.map((item: any) => (
                  <tr key={item.id} className="border-t border-line text-sm text-ink">
                    <td className="px-5 py-4"><Badge>{translateCrop(item.crop, language)}</Badge></td>
                    <td className="px-5 py-4 font-semibold">{translateDisease(item.disease, language)}</td>
                    <td className="px-5 py-4 text-xs font-semibold">{item.confidence ? `${(item.confidence * 100).toFixed(1)}%` : "N/A"}</td>
                    <td className="px-5 py-4 text-xs text-muted">{item.created_at ? new Date(item.created_at).toLocaleDateString() : "N/A"}</td>
                    <td className="px-5 py-4">
                      <Link to={`/admin/expert/${item.id}`} className="inline-flex items-center gap-1 text-xs font-semibold text-farmer-700 hover:text-farmer-900 dark:text-farmer-300 dark:hover:text-farmer-200 transition-colors">
                        <span>{t("viewScan")}</span>
                        <ArrowRight size={13} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
}
