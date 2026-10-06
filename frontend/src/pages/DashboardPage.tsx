import { useQuery } from "@tanstack/react-query";
import { Link, Navigate } from "react-router-dom";
import { CloudSun, Activity, Scan, ArrowRight } from "../components/icons";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { Badge, Button, Card, Skeleton } from "../components/ui";
import { formatTemperature, formatWindSpeed } from "../lib/format";
import { translateCrop, translateDisease, translateSeverityBucket, translateWeather } from "../i18n/domain";

interface ScanItem {
  id?: number;
  prediction_id?: number;
  crop?: { label?: string };
  disease?: { label?: string };
  severity?: { bucket?: string };
  created_at?: string;
}

interface WeatherData {
  temperature_celsius?: number;
  humidity_percent?: number;
  condition?: string;
  wind_speed_mps?: number;
}

export default function DashboardPage() {
  const { user, token, units, language, t } = useAuth();

  const { data: history = [], isLoading: isHistoryLoading } = useQuery<ScanItem[]>({
    queryKey: ["scanHistorySummary"],
    queryFn: () => request<ScanItem[]>("/history?limit=3", {}, token!),
    enabled: !!token,
  });

  const lat = user?.latitude || 22.2587;
  const lon = user?.longitude || 71.1924;

  const { data: weather, isLoading: isWeatherLoading } = useQuery<WeatherData>({
    queryKey: ["dashboardWeather", lat, lon],
    queryFn: () => request<WeatherData>(`/weather?lat=${lat}&lon=${lon}`, {}, token!),
    enabled: !!token,
  });

  if (user?.role === "expert") {
    return <Navigate to="/admin/expert" replace />;
  }

  return (
    <div className="space-y-6 pb-12">
      <header className="flex flex-col gap-6 rounded-sm border border-line bg-surface p-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("farmStatus")}</span>
          <h1 className="mt-1 font-display text-2xl sm:text-3xl text-ink">
            {t("greeting")}, {user?.name || "Farmer"}
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{t("scanCtaCopy")}</p>
        </div>
        <div>
          <Link to="/scan">
            <Button className="bg-farmer-700 font-semibold text-white hover:bg-farmer-800 transition-colors">
              <Scan size={18} /> {t("scanCta")}
            </Button>
          </Link>
        </div>
      </header>

      <div className="grid gap-5 lg:grid-cols-2">
        {/* Quick Weather Widget */}
        <div className="rounded-sm border border-line bg-surface p-6">
          <div className="flex items-center justify-between gap-4 border-b border-line pb-4">
            <h3 className="flex items-center gap-2 font-display text-lg text-ink">
              <CloudSun className="text-farmer-700 dark:text-farmer-300" size={18} /> {t("liveWeather")}
            </h3>
            <Link to="/weather" className="inline-flex items-center gap-1 text-xs font-semibold text-farmer-700 hover:text-farmer-900 dark:text-farmer-300 dark:hover:text-farmer-200">
              {t("details")} <ArrowRight size={13} />
            </Link>
          </div>

          {isWeatherLoading ? (
            <div className="mt-6 space-y-4">
              <div className="flex justify-between items-end">
                <Skeleton className="h-10 w-24" />
                <Skeleton className="h-6 w-32" />
              </div>
              <Skeleton className="h-4 w-48" />
            </div>
          ) : weather ? (
            <div className="mt-6 flex flex-wrap items-end justify-between gap-6">
              <div>
                <span className="font-display text-4xl text-ink">{formatTemperature(weather.temperature_celsius, units)}</span>
                <span className="mt-1 block text-xs text-muted">{translateWeather(weather.condition, language)}</span>
              </div>
              <div className="flex gap-6 text-right">
                <div>
                  <span className="block text-xs text-muted">{t("humidity")}</span>
                  <strong className="text-base text-ink">{weather.humidity_percent ?? "N/A"}%</strong>
                </div>
                <div>
                  <span className="block text-xs text-muted">{t("wind")}</span>
                  <strong className="text-base text-ink">{formatWindSpeed(weather.wind_speed_mps, units)}</strong>
                </div>
              </div>
            </div>
          ) : (
            <p className="mt-6 text-xs text-muted">{t("failedWeatherData")}</p>
          )}
        </div>

        {/* System & Farm Stats */}
        <div className="rounded-sm border border-line bg-surface p-6">
          <div className="border-b border-line pb-4">
            <h3 className="flex items-center gap-2 font-display text-lg text-ink">
              <Activity className="text-farmer-700 dark:text-farmer-300" size={18} /> {t("farmStatus")}
            </h3>
          </div>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xs border border-line bg-canvas p-4">
              <span className="block text-xs font-semibold uppercase tracking-wider text-muted">{t("location")}</span>
              <div className="mt-1.5 font-semibold text-ink text-sm">{user?.location || t("unknown")}</div>
            </div>
            <div className="rounded-xs border border-line bg-canvas p-4">
              <span className="block text-xs font-semibold uppercase tracking-wider text-muted">{t("crop")}</span>
              <div className="mt-1.5 font-semibold text-ink text-sm">{user?.crop_history?.length || 0} active plots</div>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-sm border border-line bg-surface p-6">
        <div className="flex items-center justify-between gap-4 border-b border-line pb-4">
          <h3 className="font-display text-lg text-ink">{t("recentDiagnostics")}</h3>
          <Link to="/history" className="inline-flex items-center gap-1 text-xs font-semibold text-farmer-700 hover:text-farmer-900 dark:text-farmer-300 dark:hover:text-farmer-200 transition-colors">
            {t("viewAll")} <ArrowRight size={13} />
          </Link>
        </div>
        
        {isHistoryLoading ? (
          <div className="mt-5 space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex justify-between items-center rounded-xs border border-line p-4">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-5 w-40" />
                </div>
                <Skeleton className="h-6 w-24" />
              </div>
            ))}
          </div>
        ) : history.length === 0 ? (
          <div className="mt-6 rounded-xs border border-line bg-canvas p-6 text-center">
            <p className="text-sm text-muted">{t("noRecentScans")}</p>
            <Link to="/scan" className="mt-4 inline-block">
              <Button variant="secondary" size="sm">{t("startFirstScan")}</Button>
            </Link>
          </div>
        ) : (
          <div className="mt-5 space-y-3">
            {history.map((scan) => (
              <Link 
                to={`/predictions/${scan.prediction_id}`} 
                key={scan.prediction_id} 
                className="flex flex-col gap-3 rounded-xs border border-line p-4 transition-colors hover:border-farmer-700 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <Badge>{translateCrop(scan.crop?.label, language)}</Badge>
                  <h4 className="mt-1.5 font-display text-base text-ink">{translateDisease(scan.disease?.label, language)}</h4>
                </div>
                <div className="flex items-center gap-3 sm:flex-col sm:items-end">
                  <Badge tone={scan.severity?.bucket?.toLowerCase() === "severe" || scan.severity?.bucket?.toLowerCase() === "critical" ? "danger" : scan.severity?.bucket?.toLowerCase() === "moderate" ? "warning" : "success"}>
                    {translateSeverityBucket(scan.severity?.bucket, language)}
                  </Badge>
                  <span className="text-xs text-muted">
                    {scan.created_at ? new Date(scan.created_at).toLocaleDateString() : t("recently")}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
