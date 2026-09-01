import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { Scan, CloudSun, ArrowRight, ShieldCheck, Activity } from "lucide-react";
import { motion } from "framer-motion";

interface SeverityObj {
  percent?: number;
  affected_area?: number;
  bucket?: string;
}

interface ScanItem {
  prediction_id?: number;
  id?: number;
  crop?: { label: string; confidence?: number };
  disease?: { label: string; confidence?: number };
  severity?: SeverityObj | string | number;
  created_at?: string;
}

interface WeatherData {
  temperature: number;
  humidity: number;
  description: string;
  wind_speed: number;
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
          <h1>Welcome back, {user?.name || "Farmer"}! 🌱</h1>
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
                <span className="temp-value">{weather.temperature}°C</span>
                <span className="temp-desc">{weather.description}</span>
              </div>
              <div className="weather-substats">
                <div><span>Humidity</span><strong>{weather.humidity}%</strong></div>
                <div><span>Wind</span><strong>{weather.wind_speed} km/h</strong></div>
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
              <span className="stat-label">Farm Location</span>
              <strong className="stat-val">{user?.location || "Configured"}</strong>
            </div>
            <div className="stat-item">
              <span className="stat-label">AI Model Status</span>
              <strong className="stat-val text-success"><ShieldCheck size={16} /> Online</strong>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Recent Scans Section */}
      <motion.section 
        className="recent-scans-section"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="section-header">
          <h2>Recent Diagnostic Scans</h2>
          <Link to="/history" className="view-all-link">View Full History</Link>
        </div>

        {history.length === 0 ? (
          <div className="empty-scans-box">
            <p>No scans recorded yet. Upload your first crop leaf photo to run an AI diagnostic check.</p>
            <Link to="/scan" className="btn btn-outline btn-sm">Run First Scan</Link>
          </div>
        ) : (
          <div className="scans-list">
            {history.map((scan, index) => {
              const scanId = scan.prediction_id || scan.id || index;
              const cropName = scan.crop?.label || "Unknown Crop";
              const diseaseName = scan.disease?.label || "Healthy / Unknown";
              
              // Handle severity object safely
              let severityLabel = "Unknown";
              let severityClass = "";
              if (scan.severity && typeof scan.severity === "object") {
                severityLabel = scan.severity.bucket || `${scan.severity.percent ?? 0}%`;
                severityClass = (scan.severity.bucket || "").toLowerCase();
              } else if (scan.severity) {
                severityLabel = String(scan.severity);
                severityClass = severityLabel.toLowerCase();
              }

              const scanDate = scan.created_at ? new Date(scan.created_at).toLocaleDateString() : "";

              return (
                <Link to={`/predictions/${scanId}`} key={scanId} className="scan-row-item">
                  <div className="scan-row-info">
                    <span className="crop-badge">{cropName}</span>
                    <h4 className="disease-title">{diseaseName}</h4>
                    {scanDate && <span className="scan-date">{scanDate}</span>}
                  </div>
                  <div className="scan-row-meta">
                    <span className={`severity-pill ${severityClass}`}>
                      {severityLabel}
                    </span>
                    <ArrowRight size={16} className="arrow-icon" />
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </motion.section>
    </div>
  );
}