import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Bell, CheckCircle2, ShieldAlert, AlertTriangle, Info, Check, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { fetchAlerts, markAlertRead, markAllAlertsRead, AlertItem } from "../api/alerts";
import { motion } from "motion/react";
import { Badge, Button, Card } from "../components/ui";

export default function AlertsPage() {
  const { token, t } = useAuth();
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<"all" | "unread" | "weather" | "expert">("all");

  const { data: alerts = [], isLoading, error } = useQuery<AlertItem[]>({
    queryKey: ["alerts"],
    queryFn: () => fetchAlerts(token!),
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
    if (filter === "weather") return alert.kind?.toLowerCase().includes("weather") || alert.title?.toLowerCase().includes("weather");
    if (filter === "expert") return alert.kind?.toLowerCase().includes("expert") || alert.title?.toLowerCase().includes("expert");
    return true;
  });

  const unreadCount = alerts.filter((a) => !a.is_read).length;

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <header className="flex flex-col gap-5 rounded-lg bg-farmer-900 p-7 text-white shadow-card sm:flex-row sm:items-center sm:justify-between sm:p-10">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-display text-3xl text-farmer-200 sm:text-4xl">Farm Alerts & Advisories</h1>
            {unreadCount > 0 && (
              <span className="rounded-full bg-danger px-3 py-0.5 text-xs font-bold text-white">
                {unreadCount} New
              </span>
            )}
          </div>
          <p className="mt-3 max-w-2xl leading-7 text-white/70">
            Real-time proactive notifications regarding micro-climate weather risks, disease outbreaks, and expert clinical evaluations.
          </p>
        </div>
        {unreadCount > 0 && (
          <Button
            className="bg-farmer-300 text-ink hover:bg-farmer-200"
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
          All Alerts ({alerts.length})
        </button>
        <button
          onClick={() => setFilter("unread")}
          className={`rounded-sm px-4 py-2 text-sm font-semibold transition-colors ${
            filter === "unread" ? "bg-farmer-700 text-white" : "text-muted hover:bg-canvas hover:text-ink"
          }`}
        >
          Unread ({unreadCount})
        </button>
        <button
          onClick={() => setFilter("weather")}
          className={`rounded-sm px-4 py-2 text-sm font-semibold transition-colors ${
            filter === "weather" ? "bg-farmer-700 text-white" : "text-muted hover:bg-canvas hover:text-ink"
          }`}
        >
          Weather Advisories
        </button>
        <button
          onClick={() => setFilter("expert")}
          className={`rounded-sm px-4 py-2 text-sm font-semibold transition-colors ${
            filter === "expert" ? "bg-farmer-700 text-white" : "text-muted hover:bg-canvas hover:text-ink"
          }`}
        >
          Expert Overrides
        </button>
      </div>

      {/* Alerts List */}
      <motion.div
        className="space-y-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {isLoading ? (
          <div className="flex min-h-[30vh] items-center justify-center text-sm text-muted">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-farmer-200 border-t-farmer-700" />
            <span className="ml-3">Loading farm alerts...</span>
          </div>
        ) : error ? (
          <Card className="text-danger">Failed to load alerts feed.</Card>
        ) : filteredAlerts.length === 0 ? (
          <div className="flex flex-col items-center rounded-md border border-line bg-surface p-12 text-center shadow-soft">
            <CheckCircle2 size={48} className="text-farmer-700" />
            <h3 className="mt-4 font-display text-xl text-ink">No alerts found</h3>
            <p className="mt-2 text-sm text-muted">You are up to date! There are currently no warnings matching your filter.</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const isExpert = alert.kind?.toLowerCase().includes("expert") || alert.title?.toLowerCase().includes("expert");
            const isCritical = alert.severity === "high" || alert.severity === "critical";

            return (
              <div
                key={alert.id}
                className={`relative flex flex-col justify-between gap-4 rounded-md border p-5 shadow-soft transition-all duration-200 sm:flex-row sm:items-center ${
                  alert.is_read
                    ? "border-line bg-surface opacity-90"
                    : "border-farmer-300 bg-farmer-50/70"
                }`}
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-md ${
                      isExpert
                        ? "bg-expert-100 text-expert-700"
                        : isCritical
                        ? "bg-red-100 text-danger"
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
                      <h4 className="font-display text-lg text-ink">{alert.title}</h4>
                      {!alert.is_read && (
                        <span className="rounded-sm bg-danger px-1.5 py-0.5 text-[0.65rem] font-bold uppercase tracking-wide text-white">
                          New
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
                          {alert.severity.toUpperCase()}
                        </Badge>
                      )}
                    </div>
                    <p className="mt-2 text-sm leading-6 text-muted">{alert.body}</p>
                    <span className="mt-2 block text-xs text-muted">
                      {alert.created_at ? new Date(alert.created_at).toLocaleString() : "Recently"}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-center">
                  {alert.prediction_id && (
                    <Link
                      to={`/predictions/${alert.prediction_id}`}
                      className="inline-flex items-center gap-1 rounded-sm border border-line bg-surface px-3 py-2 text-xs font-semibold text-farmer-800 hover:bg-canvas"
                    >
                      View Scan <ArrowRight size={14} />
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
      </motion.div>
    </div>
  );
}
