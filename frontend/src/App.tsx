import { Routes, Route, Navigate } from "react-router-dom";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
// import { DashboardPage } from "./pages/DashboardPage";
// import { ScanPage } from "./pages/ScanPage";
// import { PredictionResultPage } from "./pages/PredictionResultPage";
// import { HistoryPage } from "./pages/HistoryPage";
// import { FarmSettingsPage } from "./pages/FarmSettingsPage";
// import { WeatherPage } from "./pages/WeatherPage";
// import { CropsPage } from "./pages/CropsPage";
// import { AdminMetricsPage } from "./pages/AdminMetricsPage";
// import { AdminFeedbackPage } from "./pages/AdminFeedbackPage";
// import { ProtectedRoute } from "./components/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      {/*<Route path="/crops" element={<CropsPage />} />
      <Route path="/docs" element={() => { window.location.href = "http://localhost:8000/docs"; return null; }} />

      {/* Protected Farmer Routes 
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/scan" element={<ProtectedRoute><ScanPage /></ProtectedRoute>} />
      <Route path="/predictions/:id" element={<ProtectedRoute><PredictionResultPage /></ProtectedRoute>} />
      <Route path="/history" element={<ProtectedRoute><HistoryPage /></ProtectedRoute>} />
      <Route path="/farm/settings" element={<ProtectedRoute><FarmSettingsPage /></ProtectedRoute>} />
      <Route path="/weather" element={<ProtectedRoute><WeatherPage /></ProtectedRoute>} />

      {/* Protected Admin Routes 
      <Route path="/admin/metrics" element={<ProtectedRoute adminOnly><AdminMetricsPage /></ProtectedRoute>} />
      <Route path="/admin/feedback" element={<ProtectedRoute adminOnly><AdminFeedbackPage /></ProtectedRoute>} />

      {/* Fallback 
      <Route path="*" element={<Navigate to="/" replace />} /> */}
    </Routes>
  );
}
