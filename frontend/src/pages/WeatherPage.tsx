import { useQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import { Link } from "react-router-dom";
import { Cloud, Droplets, Wind, ThermometerSun } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { weather as fetchWeather } from "../api/predictions";
import { Button, Card } from "../components/ui";
import { formatTemperature, formatWindSpeed } from "../lib/format";

export default function WeatherPage() {
  const { user, token, units } = useAuth();
  
  const { data, isLoading, isError } = useQuery({
    queryKey: ["weather", user?.latitude, user?.longitude],
    queryFn: () => fetchWeather(user?.latitude || 0, user?.longitude || 0, token!),
    enabled: !!token,
  });

  if (isLoading) return <div className="flex min-h-[40vh] items-center justify-center text-sm text-muted"><div className="h-5 w-5 animate-spin rounded-full border-2 border-farmer-200 border-t-farmer-700" /><span className="ml-3">Loading regional weather data...</span></div>;
  if (isError || !data) return <div className="rounded-md border border-red-100 bg-red-50 p-6 text-danger">Failed to load weather data.</div>;

  const temp = formatTemperature(data.temperature_celsius, units);
  const hum = data.humidity_percent ?? "--";
  const wind = formatWindSpeed(data.wind_speed_mps, units);

  return (
    <motion.div className="space-y-6 pb-12" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="font-display text-3xl text-ink sm:text-4xl">Regional Weather Context</h1>
          <p className="mt-2 text-muted">Current conditions around your farm.</p>
        </div>
        <Link to="/dashboard"><Button variant="secondary" size="sm">← Back to Dashboard</Button></Link>
      </div>

      <div className="flex flex-col justify-between gap-8 rounded-lg bg-farmer-900 p-7 text-white shadow-card sm:flex-row sm:items-center sm:p-10">
        <div>
          <h2 className="font-display text-6xl text-farmer-200">{temp}</h2>
          <p className="mt-3 text-sm font-semibold uppercase tracking-wide text-white/70">{data.condition?.toUpperCase() || "CLEAR CONDITIONS"} • {user?.location || "FARM LOCATION"}</p>
        </div>
        <div className="text-farmer-300">
          <Cloud size={100} />
        </div>
      </div>

      <div className="grid gap-5 sm:grid-cols-3">
        <Card className="text-center"><h4 className="text-xs font-bold uppercase tracking-wide text-muted">Humidity</h4><p className="mt-3 font-display text-3xl text-ink">{hum}%</p></Card>
        <Card className="text-center"><h4 className="text-xs font-bold uppercase tracking-wide text-muted">Wind Speed</h4><p className="mt-3 font-display text-3xl text-ink">{wind}</p></Card>
        <Card className="text-center"><h4 className="text-xs font-bold uppercase tracking-wide text-muted">Status</h4><p className="mt-3 font-display text-3xl text-farmer-700">Active</p></Card>
      </div>

      <Card className="border-farmer-200 bg-farmer-50" padding="lg">
        <h3 className="font-display text-2xl text-farmer-900">Agronomic Weather Advisory</h3>
        {data.advisory ? (
          <div className="mt-4 whitespace-pre-wrap leading-7 text-muted">
             {data.advisory}
          </div>
        ) : (
          <p className="mt-4 leading-7 text-muted">
            {(data.humidity_percent || 0) > 70 
              ? "High humidity conditions detected. These conditions are highly conducive to fungal outbreaks such as Blight and Mildew. Ensure adequate spacing between crops for airflow and consider preventative fungicidal sprays if symptoms appear."
              : (data.temperature_celsius || 0) > 35
              ? "High temperatures detected. Risk of heat stress and rapid moisture loss. Increase irrigation frequency and monitor for pest populations which may spike in dry, hot conditions."
              : "Current weather conditions are optimal for general crop development. Maintain standard monitoring and watering schedules."}
          </p>
        )}
      </Card>
    </motion.div>
  );
}
