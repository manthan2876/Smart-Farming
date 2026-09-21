import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { CloudSun, Activity, Scan, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { motion } from "motion/react";
import { Badge, Button, Card } from "../components/ui";
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

  const { data: history = [] } = useQuery<ScanItem[]>({
    queryKey: ["scanHistorySummary"],
    queryFn: () => request<ScanItem[]>("/history?limit=3", {}, token!),
    enabled: !!token,
  });

  const lat = user?.latitude || 22.2587;
  const lon = user?.longitude || 71.1924;

  const { data: weather } = useQuery<WeatherData>({
    queryKey: ["dashboardWeather", lat, lon],
    queryFn: () => request<WeatherData>(`/weather?lat=${lat}&lon=${lon}`, {}, token!),
    enabled: !!token,
  });

  return (
    <div className="space-y-6 pb-12">
      <header className="flex flex-col gap-6 rounded-lg bg-farmer-900 p-7 text-white shadow-card sm:p-10 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="font-display text-3xl text-farmer-200 sm:text-4xl">{t("greeting")}, {user?.name || "Farmer"}!</h1>
          <p className="mt-3 max-w-2xl leading-7 text-white/70">{t("scanCtaCopy")}</p>
        </div>
        <div>
          <Link to="/scan">
            <Button className="bg-farmer-300 text-ink hover:bg-farmer-200">
            <Scan size={18} /> {t("scanCta")}
            </Button>
          </Link>
        </div>
      </header>

      <div className="grid gap-5 lg:grid-cols-2">
        {/* Quick Weather Widget */}
        <motion.div 
          className="relative overflow-hidden rounded-md border border-line bg-surface p-6 shadow-soft before:absolute before:inset-x-0 before:top-0 before:h-1 before:bg-expert-500"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="flex items-center justify-between gap-4">
            <h3 className="flex items-center gap-2 font-display text-xl text-ink"><CloudSun className="text-expert-500" size={20} /> {t("liveWeather")}</h3>
            <Link to="/weather" className="inline-flex items-center gap-1 text-sm font-semibold text-farmer-700 hover:text-farmer-900">{t("details")} <ArrowRight size={14} /></Link>
          </div>
          {weather ? (
            <div className="mt-8 flex flex-wrap items-end justify-between gap-6">
              <div>
                <span className="font-display text-5xl text-ink">{formatTemperature(weather.temperature_celsius, units)}</span>
                <span className="mt-1 block text-sm text-muted">{translateWeather(weather.condition, language)}</span>
              </div>
              <div className="flex gap-6 text-right">
                <div><span className="block text-xs text-muted">{t("humidity")}</span><strong className="text-lg text-ink">{weather.humidity_percent ?? "--"}%</strong></div>
                <div><span className="block text-xs text-muted">{t("wind")}</span><strong className="text-lg text-ink">{formatWindSpeed(weather.wind_speed_mps, units)}</strong></div>
              </div>
            </div>
          ) : (
            <p className="mt-8 text-sm text-muted">Loading weather telemetry...</p>
          )}
        </motion.div>

        {/* System & Farm Stats */}
        <motion.div 
          className="relative overflow-hidden rounded-md border border-line bg-surface p-6 shadow-soft before:absolute before:inset-x-0 before:top-0 before:h-1 before:bg-farmer-500"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div>
            <h3 className="flex items-center gap-2 font-display text-xl text-ink"><Activity className="text-farmer-700" size={20} /> {t("farmStatus")}</h3>
          </div>
          <div className="mt-8 grid gap-5 sm:grid-cols-2">
            <div className="rounded-sm bg-canvas p-4">
              <span className="block text-xs font-semibold uppercase tracking-wide text-muted">{t("location")}</span>
              <div className="mt-2 font-semibold text-ink">{user?.location || "Unknown"}</div>
            </div>
            <div className="rounded-sm bg-canvas p-4">
              <span className="block text-xs font-semibold uppercase tracking-wide text-muted">{t("crop")}</span>
              <div className="mt-2 font-semibold text-ink">{user?.crop_history?.length || 0} active</div>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div 
        className="rounded-md border border-line bg-surface p-5 shadow-soft sm:p-6"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="flex items-center justify-between gap-4">
          <h3 className="font-display text-xl text-ink">{t("recentDiagnostics")}</h3>
          <Link to="/history" className="inline-flex items-center gap-1 text-sm font-semibold text-farmer-700 hover:text-farmer-900">{t("viewAll")} <ArrowRight size={14} /></Link>
        </div>
        
        {history.length === 0 ? (
          <div className="mt-6 rounded-sm bg-canvas p-6 text-center">
            <p className="text-sm text-muted">{t("noRecentScans")}</p>
            <Link to="/scan" className="mt-4 inline-block"><Button variant="secondary" size="sm">{t("startFirstScan")}</Button></Link>
          </div>
        ) : (
          <div className="mt-5 space-y-3">
            {history.map((scan) => (
              <Link to={`/predictions/${scan.prediction_id}`} key={scan.prediction_id} className="flex flex-col gap-4 rounded-sm border border-line p-4 transition hover:-translate-y-0.5 hover:border-farmer-300 hover:shadow-soft sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <Badge>{translateCrop(scan.crop?.label, language)}</Badge>
                  <h4 className="mt-2 font-display text-lg text-ink">{translateDisease(scan.disease?.label, language)}</h4>
                </div>
                <div className="flex items-center gap-3 sm:flex-col sm:items-end">
                  <Badge tone={scan.severity?.bucket?.toLowerCase() === "severe" || scan.severity?.bucket?.toLowerCase() === "critical" ? "danger" : scan.severity?.bucket?.toLowerCase() === "moderate" ? "warning" : "success"}>
                    {translateSeverityBucket(scan.severity?.bucket, language)}
                  </Badge>
                  <span className="text-xs text-muted">
                    {scan.created_at ? new Date(scan.created_at).toLocaleDateString() : "Just now"}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}






