import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { CloudSun, Thermometer, Droplets, Wind, Gauge, Cloud } from "lucide-react";
import { motion } from "framer-motion";

export default function WeatherPage() {
  const { user, token } = useAuth();
  const lat = user?.latitude || 21.7645;
  const lon = user?.longitude || 72.1519;

  const { data: weather, isLoading, error } = useQuery({
    queryKey: ["liveWeatherFull", lat, lon],
    queryFn: () => request<any>(`/weather?lat=${lat}&lon=${lon}`, {}, token!),
    enabled: !!token,
  });

  // Helper to safely format values while respecting 0 as a valid number
  const formatVal = (val: number | undefined | null, unit: string = "") => 
    val !== undefined && val !== null ? `${val}${unit}` : `--${unit}`;

  return (
    <div className="weather-page">
      <div className="page-header">
        <h1>Live Weather & Advisory</h1>
        <p>Real-time atmospheric telemetry for optimal irrigation and disease spray planning.</p>
      </div>

      {isLoading ? (
        <div className="loading-state"><div className="spinner"></div><p>Fetching satellite weather telemetry...</p></div>
      ) : error ? (
        <div className="error-state text-danger"><p>Failed to load weather telemetry. Please check your connection.</p></div>
      ) : (
        <motion.div 
          className="weather-dashboard-grid"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="weather-hero-card card">
            <div className="hero-main-info">
              <CloudSun size={64} className="text-warning" />
              <div>
                <h2>{formatVal(weather?.temperature, "°C")}</h2>
                <p className="condition-text">{weather?.description || "Clear skies"}</p>
                <span className="location-pill">Coordinates: {lat}, {lon}</span>
              </div>
            </div>
          </div>

          <div className="weather-metrics-grid">
            <div className="metric-card card">
              <Droplets size={24} className="text-primary" />
              <div>
                <span>Humidity</span>
                <h3>{formatVal(weather?.humidity, "%")}</h3>
              </div>
            </div>
            <div className="metric-card card">
              <Wind size={24} className="text-info" />
              <div>
                <span>Wind Speed</span>
                <h3>{formatVal(weather?.wind_speed, " km/h")}</h3>
              </div>
            </div>
            <div className="metric-card card">
              <Gauge size={24} className="text-success" />
              <div>
                <span>Pressure</span>
                <h3>{formatVal(weather?.pressure, " hPa")}</h3>
              </div>
            </div>
            <div className="metric-card card">
              <Cloud size={24} className="text-secondary" />
              <div>
                <span>Cloudiness</span>
                <h3>{formatVal(weather?.cloudiness, "%")}</h3>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}