import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AlertCircle, CheckCircle, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getExpertQueue } from "../api/expert";
import { motion } from "motion/react";
import { Badge, Card, Table } from "../components/ui";
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
      <div className="flex flex-col gap-5 rounded-lg border border-expert-500/30 bg-[#163834] p-7 shadow-card sm:flex-row sm:items-center sm:justify-between sm:p-10 dark:border-cyan-900/60 dark:bg-[#091a18]">
        <div>
          <h1 className="font-display text-3xl text-cyan-200 dark:text-cyan-300 sm:text-4xl">{t("expertTriageQueue")}</h1>
          <p className="mt-3 text-cyan-100/90 dark:text-cyan-100/85">{t("expertTriageSubtitle")}</p>
        </div>
        <AlertCircle className="text-cyan-300 dark:text-cyan-400" size={48} />
      </div>

      <motion.div
        className="rounded-md border border-line bg-surface p-5 shadow-soft sm:p-6"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h3 className="font-display text-xl text-ink">{t("pendingReviews")} ({queue.length})</h3>
        </div>

        {isLoading ? (
          <p className="mt-5 text-sm text-muted">{t("loadingQueue")}</p>
        ) : error ? (
          <p className="mt-5 text-sm text-danger">{t("failedLoadQueue")}</p>
        ) : queue.length === 0 ? (
          <div className="mt-5 flex flex-col items-center rounded-sm bg-farmer-50 dark:bg-farmer-900/40 p-8 text-center text-sm text-muted border border-line">
            <CheckCircle className="text-farmer-700 dark:text-farmer-300" size={40} />
            <p className="mt-3">{t("queueEmpty")}</p>
          </div>
        ) : (
          <Table className="mt-5">
              <thead>
                <tr className="bg-canvas text-xs uppercase tracking-wide text-muted">
                  {[t("date"), t("crop"), t("aiDiagnosis"), t("confidence"), t("severity"), t("action")].map((heading) => <th key={heading} className="px-5 py-4 font-semibold">{heading}</th>)}
                </tr>
              </thead>
              <tbody>
                {queue.map((item) => (
                  <tr className="border-t border-line text-sm text-ink" key={item.review_id}>
                    <td className="px-5 py-4 text-muted">{item.created_at ? new Date(item.created_at).toLocaleDateString() : "N/A"}</td>
                    <td className="px-5 py-4"><Badge>{translateCrop(item.crop, language) || t("unknown")}</Badge></td>
                    <td className="px-5 py-4 font-semibold">{translateDisease(item.disease, language) || t("unknown")}</td>
                    <td className="px-5 py-4">{(item.disease_conf * 100).toFixed(1)}%</td>
                    <td className="px-5 py-4">
                      <Badge tone={item.severity_pct > 60 ? "danger" : item.severity_pct > 25 ? "warning" : "success"}>
                        {item.severity_pct > 60 ? t("severe") : item.severity_pct > 25 ? t("moderate") : t("low")}
                      </Badge>
                    </td>
                    <td>
                      <Link to={`/admin/expert/${item.review_id}`} className="inline-flex items-center gap-1 font-semibold text-expert-700 hover:text-expert-500 dark:text-cyan-400 dark:hover:text-cyan-300">
                        {t("review")} <ArrowRight size={14} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
          </Table>
        )}
      </motion.div>
    </div>
  );
}
