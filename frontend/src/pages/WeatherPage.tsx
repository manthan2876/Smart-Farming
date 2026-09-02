import { useQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import { Link } from "react-router-dom";
import { Cloud, Droplets, Wind, ThermometerSun } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { weather as fetchWeather } from "../api/predictions";

import "../styles/WeatherCrops.css";

export default function WeatherPage() {
  const { user, token } = useAuth();
  
  const { data, isLoading, isError } = useQuery({
    queryKey: ["weather", user?.latitude, user?.longitude],
    queryFn: () => fetchWeather(user?.latitude || 0, user?.longitude || 0, token!),
    enabled: !!token,
  });

  if (isLoading) return <div className="weather-page"><p>Loading regional weather data...</p></div>;
  if (isError || !data) return <div className="weather-page"><p>Failed to load weather data.</p></div>;

  const temp = data.temperature_celsius ?? "--";
  const hum = data.humidity_percent ?? "--";
  const wind = data.wind_speed_mps ?? "--";

  return (
    <motion.div className="weather-page" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div className="page-header">
        <h1>Regional Weather Context</h1>
        <Link to="/dashboard" className="back-btn">← Back to Dashboard</Link>
      </div>

      <div className="weather-hero">
        <div>
          <h2>{temp}°C</h2>
          <p>{data.condition?.toUpperCase() || "CLEAR CONDITIONS"} • {user?.location || "FARM LOCATION"}</p>
        </div>
        <div className="weather-icon-large">
          <Cloud size={100} color="#e1fc84" />
        </div>
      </div>

      <div className="weather-details">
        <div className="weather-stat">
          <h4>Humidity</h4>
          <p>{hum}%</p>
        </div>
        <div className="weather-stat">
          <h4>Wind Speed</h4>
          <p>{wind} km/h</p>
        </div>
        <div className="weather-stat">
          <h4>Status</h4>
          <p>Active</p>
        </div>
      </div>

      <div className="weather-advisory">
        <h3>Agronomic Weather Advisory</h3>
        {data.advisory ? (
          <div className="advisory-content">
             <div style={{ whiteSpace: "pre-wrap" }}>{data.advisory}</div>
          </div>
        ) : (
          <p>
            {(data.humidity_percent || 0) > 70 
              ? "High humidity conditions detected. These conditions are highly conducive to fungal outbreaks such as Blight and Mildew. Ensure adequate spacing between crops for airflow and consider preventative fungicidal sprays if symptoms appear."
              : (data.temperature_celsius || 0) > 35
              ? "High temperatures detected. Risk of heat stress and rapid moisture loss. Increase irrigation frequency and monitor for pest populations which may spike in dry, hot conditions."
              : "Current weather conditions are optimal for general crop development. Maintain standard monitoring and watering schedules."}
          </p>
        )}
      </div>
    </motion.div>
  );
}
