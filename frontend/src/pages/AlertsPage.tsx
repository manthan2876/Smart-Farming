import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Bell, CheckCircle2, ShieldAlert, AlertTriangle, Info, Check, ArrowRight } from "../components/icons";
import { useAuth } from "../context/AuthContext";
import { fetchAlerts, markAlertRead, markAllAlertsRead, AlertItem } from "../api/alerts";
import { Badge, Button, Card, Skeleton } from "../components/ui";
import { translateAlertTitle, translateSeverityBucket } from "../i18n/domain";

export default function AlertsPage() {
  const { token, language, t } = useAuth();
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<"all" | "unread" | "weather" | "expert">("all");

  const { data: alerts = [], isLoading, error } = useQuery<AlertItem[]>({
    queryKey: ["alerts", language],
    queryFn: () => fetchAlerts(token!, language),
    enabled: !!token,
  });

  const markReadMutation = useMutation({
    mutationFn: (id: number) => markAlertRead(id, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  const markAllMutation = useMutation({
    mutationFn: () => markAllAlertsRead(alerts, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  const filteredAlerts = alerts.filter((alert) => {
    if (filter === "unread") return !alert.is_read;
    if (filter === "weather") {
      const lowerKind = alert.kind?.toLowerCase() || "";
      const lowerTitle = alert.title?.toLowerCase() || "";
      return (
        lowerKind.includes("weather") ||
        lowerTitle.includes("weather") ||
        lowerTitle.includes("मौसम") ||
        lowerTitle.includes("હવામાન") ||
        lowerTitle.includes("વરસાદ") ||
        lowerTitle.includes("ગરમી") ||
        lowerTitle.includes("જોખમ") ||
        lowerTitle.includes("जोखिम")
      );
    }
    if (filter === "expert") {
      const lowerKind = alert.kind?.toLowerCase() || "";
      const lowerTitle = alert.title?.toLowerCase() || "";
      return (
        lowerKind.includes("expert") ||
        lowerTitle.includes("expert") ||
        lowerTitle.includes("विशेषज्ञ") ||
        lowerTitle.includes("નિષ્ણાત")
      );
    }
    return true;
  });

  const unreadCount = alerts.filter((a) => !a.is_read).length;

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <header className="flex flex-col gap-5 rounded-lg border border-farmer-800 bg-farmer-900 p-7 text-farmer-100 shadow-card sm:flex-row sm:items-center sm:justify-between sm:p-10">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-display text-3xl text-farmer-200 sm:text-4xl">{t("farmAlertsTitle")}</h1>
            {unreadCount > 0 && (
              <span className="rounded-full bg-danger px-3 py-0.5 text-xs font-bold text-white">
                {unreadCount} {t("new")}
              </span>
            )}
          </div>
          <p className="mt-3 max-w-2xl leading-7 text-farmer-100/90">
            {t("farmAlertsSubtitle")}
          </p>
        </div>
        {unreadCount > 0 && (
          <Button
            className="bg-farmer-400 font-bold text-farmer-950 hover:bg-farmer-300 shadow-soft transition-colors"
            onClick={() => markAllMutation.mutate()}
            disabled={markAllMutation.isPending}
          >
            <Check size={18} /> {t("markAllRead")}
          </Button>
        )}
      </header>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-line pb-3">
        <button
          onClick={() => setFilter("all")}
          className={`rounded-sm px-4 py-2 text-sm font-semibold transition-colors ${
            filter === "all" ? "bg-farmer-700 text-white" : "text-muted hover:bg-canvas hover:text-ink"
          }`}
        >
          {t("allAlerts")} ({alerts.length})
        </button>
        <button
          onClick={() => setFilter("unread")}
          className={`rounded-sm px-4 py-2 text-sm font-semibold transition-colors ${
            filter === "unread" ? "bg-farmer-700 text-white" : "text-muted hover:bg-canvas hover:text-ink"
          }`}
        >
          {t("unread")} ({unreadCount})
        </button>
        <button
          onClick={() => setFilter("weather")}
          className={`rounded-sm px-4 py-2 text-sm font-semibold transition-colors ${
            filter === "weather" ? "bg-farmer-700 text-white" : "text-muted hover:bg-canvas hover:text-ink"
          }`}
        >
          {t("weatherAdvisoriesFilter")}
        </button>
        <button
          onClick={() => setFilter("expert")}
          className={`rounded-sm px-4 py-2 text-sm font-semibold transition-colors ${
            filter === "expert" ? "bg-farmer-700 text-white" : "text-muted hover:bg-canvas hover:text-ink"
          }`}
        >
          {t("expertOverridesFilter")}
        </button>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex gap-4 rounded-sm border border-line bg-surface p-5">
                <Skeleton className="h-10 w-10 shrink-0" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-5 w-48" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-3 w-32" />
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <Card className="text-danger">{t("failedAlerts")}</Card>
        ) : filteredAlerts.length === 0 ? (
          <div className="flex flex-col items-center rounded-sm border border-line bg-surface p-12 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-xs bg-farmer-100 dark:bg-farmer-900/60 text-farmer-800 dark:text-farmer-200">
              <CheckCircle2 size={24} />
            </div>
            <h3 className="mt-4 font-display text-xl text-ink">{t("noAlertsFound")}</h3>
            <p className="mt-2 text-xs text-muted">{t("noAlertsFilterDesc")}</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const isExpert = alert.kind?.toLowerCase().includes("expert") || alert.title?.toLowerCase().includes("expert");
            const isCritical = alert.severity === "high" || alert.severity === "critical";

            return (
              <div
                key={alert.id}
                className={`relative flex flex-col justify-between gap-4 rounded-sm border p-5 transition-colors sm:flex-row sm:items-center ${
                  alert.is_read
                    ? "border-line bg-surface opacity-90"
                    : "border-farmer-300 bg-farmer-50/50 dark:border-farmer-700 dark:bg-farmer-900/30"
                }`}
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-md ${
                      isExpert
                        ? "bg-expert-100 text-expert-700"
                        : isCritical
                        ? "bg-red-100 text-danger dark:bg-red-950/60 dark:text-red-300"
                        : "bg-farmer-100 text-farmer-800"
                    }`}
                  >
                    {isExpert ? (
                      <ShieldAlert size={20} />
                    ) : isCritical ? (
                      <AlertTriangle size={20} />
                    ) : (
                      <Info size={20} />
                    )}
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="font-display text-lg text-ink">{translateAlertTitle(alert.title, language)}</h4>
                      {!alert.is_read && (
                        <span className="rounded-sm bg-danger px-1.5 py-0.5 text-[0.65rem] font-bold uppercase tracking-wide text-white">
                          {t("new")}
                        </span>
                      )}
                      {alert.severity && (
                        <Badge
                          tone={
                            alert.severity === "high" || alert.severity === "critical"
                              ? "danger"
                              : alert.severity === "moderate"
                              ? "warning"
                              : "neutral"
                          }
                        >
                          {translateSeverityBucket(alert.severity, language).toUpperCase()}
                        </Badge>
                      )}
                    </div>
                    <p className="mt-2 text-sm leading-6 text-muted">{alert.body}</p>
                    <span className="mt-2 block text-xs text-muted">
                      {alert.created_at ? new Date(alert.created_at).toLocaleString() : t("recently")}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-center">
                  {alert.prediction_id && (
                    <Link
                      to={`/predictions/${alert.prediction_id}`}
                      onClick={() => {
                        if (!alert.is_read) {
                          markReadMutation.mutate(alert.id);
                        }
                      }}
                      className="inline-flex items-center gap-1 rounded-sm border border-line bg-surface px-3 py-2 text-xs font-semibold text-farmer-800 hover:bg-canvas dark:text-farmer-300 dark:hover:text-farmer-200 dark:border-farmer-700/60 dark:hover:bg-farmer-900/60 transition-colors"
                    >
                      {t("viewScan")} <ArrowRight size={14} />
                    </Link>
                  )}
                  {!alert.is_read && (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => markReadMutation.mutate(alert.id)}
                      disabled={markReadMutation.isPending}
                    >
                      {t("markAsRead")}
                    </Button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
