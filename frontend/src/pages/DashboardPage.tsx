import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { CloudSun, Activity, Scan, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { motion } from "motion/react";
import "../styles/DashboardPage.css";

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
  const { user, token } = useAuth();

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
    <div className="dashboard-page">
      <header className="dashboard-welcome-banner">
        <div className="welcome-text">
          <h1>Welcome back, {user?.name || "Farmer"}! </h1>
          <p>Monitor your crop health, analyze leaf scans with AI, and track local weather conditions in real-time.</p>
        </div>
        <div className="welcome-action">
          <Link to="/scan" className="btn btn-primary btn-glow">
            <Scan size={18} /> Start New Scan
          </Link>
        </div>
      </header>

      <div className="dashboard-grid">
        {/* Quick Weather Widget */}
        <motion.div 
          className="dashboard-card weather-widget-card"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="card-header">
            <h3><CloudSun size={20} /> Live Farm Weather</h3>
            <Link to="/weather" className="link-inline">Details <ArrowRight size={14} /></Link>
          </div>
          {weather ? (
            <div className="weather-stats-row">
              <div className="temp-display">
                <span className="temp-value">{weather.temperature_celsius ?? "--"}°C</span>
                <span className="temp-desc">{weather.condition || "Clear"}</span>
              </div>
              <div className="weather-substats">
                <div><span>Humidity</span><h4 className="disease-title">{weather.humidity_percent ?? "--"}%</h4></div>
                <div><span>Wind</span><h4 className="disease-title">{weather.wind_speed_mps ?? "--"} km/h</h4></div>
              </div>
            </div>
          ) : (
            <p className="loading-text">Loading weather telemetry...</p>
          )}
        </motion.div>

        {/* System & Farm Stats */}
        <motion.div 
          className="dashboard-card stats-overview-card"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="card-header">
            <h3><Activity size={20} /> Farm Status</h3>
          </div>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Location</span>
              <div className="stat-val">{user?.location || "Unknown"}</div>
            </div>
            <div className="stat-item">
              <span className="stat-label">Crops</span>
              <div className="stat-val">{user?.crop_history?.length || 0} active</div>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div 
        className="dashboard-card recent-scans-card"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="card-header">
          <h3>Recent Diagnostics</h3>
          <Link to="/history" className="link-inline">View All <ArrowRight size={14} /></Link>
        </div>
        
        {history.length === 0 ? (
          <div className="empty-state">
            <p>No recent scans found.</p>
            <Link to="/scan" className="btn btn-outline">Start First Scan</Link>
          </div>
        ) : (
          <div className="scans-list">
            {history.map((scan) => (
              <Link to={`/predictions/${scan.prediction_id}`} key={scan.prediction_id} className="scan-row-item" style={{textDecoration: "none", color: "inherit"}}>
                <div className="scan-row-info">
                  <span className="crop-badge">{scan.crop?.label || "Unknown Crop"}</span>
                  <h4 className="disease-title">{scan.disease?.label || "Unknown Disease" || "Unknown"}</h4>
                </div>
                <div className="scan-meta">
                  <span className={`severity-indicator ${scan.severity?.bucket || "N/A"?.toLowerCase() || 'unknown'}`}>
                    {scan.severity?.bucket || "N/A"}
                  </span>
                  <span className="scan-date">
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






