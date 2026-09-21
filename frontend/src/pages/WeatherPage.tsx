import { useQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import { Link } from "react-router-dom";
import { Cloud, Droplets, Wind, ThermometerSun } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { weather as fetchWeather } from "../api/predictions";
import { Button, Card } from "../components/ui";
import { formatTemperature, formatWindSpeed } from "../lib/format";
import { translateWeather } from "../i18n/domain";

export default function WeatherPage() {
  const { user, token, units, language, t } = useAuth();
  
  const { data, isLoading, isError } = useQuery({
    queryKey: ["weather", user?.latitude, user?.longitude],
    queryFn: () => fetchWeather(user?.latitude || 0, user?.longitude || 0, token!),
    enabled: !!token,
  });

  if (isLoading) return (
    <div className="flex min-h-[40vh] items-center justify-center text-sm text-muted">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-farmer-200 border-t-farmer-700" />
      <span className="ml-3">{t("loadingWeatherData")}</span>
    </div>
  );
  if (isError || !data) return (
    <div className="rounded-md border border-red-100 bg-red-50 p-6 text-danger">
      {t("failedWeatherData")}
    </div>
  );

  const temp = formatTemperature(data.temperature_celsius, units);
  const hum = data.humidity_percent ?? "--";
  const wind = formatWindSpeed(data.wind_speed_mps, units);
  const conditionTranslated = translateWeather(data.condition, language);

  const advisoryFallback = (data.humidity_percent || 0) > 70 
    ? t("weatherAdvisoryHighHumidity")
    : (data.temperature_celsius || 0) > 35
    ? t("weatherAdvisoryHighHeat")
    : t("weatherAdvisoryOptimal");

  return (
    <motion.div className="space-y-6 pb-12" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="font-display text-3xl text-ink sm:text-4xl">{t("regionalWeatherContext")}</h1>
          <p className="mt-2 text-muted">{t("currentConditionsAroundFarm")}</p>
        </div>
        <Link to="/dashboard"><Button variant="secondary" size="sm">{t("backToDashboard")}</Button></Link>
      </div>

      <div className="flex flex-col justify-between gap-8 rounded-lg bg-farmer-900 p-7 text-white shadow-card sm:flex-row sm:items-center sm:p-10">
        <div>
          <h2 className="font-display text-6xl text-farmer-200">{temp}</h2>
          <p className="mt-3 text-sm font-semibold uppercase tracking-wide text-white/70">
            {conditionTranslated.toUpperCase()} • {user?.location || t("farmLocation")}
          </p>
        </div>
        <div className="text-farmer-300">
          <Cloud size={100} />
        </div>
      </div>

      <div className="grid gap-5 sm:grid-cols-3">
        <Card className="text-center">
          <h4 className="text-xs font-bold uppercase tracking-wide text-muted">{t("humidity")}</h4>
          <p className="mt-3 font-display text-3xl text-ink">{hum}%</p>
        </Card>
        <Card className="text-center">
          <h4 className="text-xs font-bold uppercase tracking-wide text-muted">{t("windSpeed")}</h4>
          <p className="mt-3 font-display text-3xl text-ink">{wind}</p>
        </Card>
        <Card className="text-center">
          <h4 className="text-xs font-bold uppercase tracking-wide text-muted">{t("status")}</h4>
          <p className="mt-3 font-display text-3xl text-farmer-700">{t("active")}</p>
        </Card>
      </div>

      <Card className="border-farmer-200 bg-farmer-50" padding="lg">
        <h3 className="font-display text-2xl text-farmer-900">{t("agronomicWeatherAdvisory")}</h3>
        <p className="mt-4 leading-7 text-muted">
          {data.advisory || advisoryFallback}
        </p>
      </Card>
    </motion.div>
  );
}
