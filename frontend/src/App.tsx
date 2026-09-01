import { Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import ScanPage from "./pages/ScanPage";
import PredictionResultPage from "./pages/PredictionResultPage";
import HistoryPage from "./pages/HistoryPage";
import FarmSettingsPage from "./pages/FarmSettingsPage";
import WeatherPage from "./pages/WeatherPage";
import CropsPage from "./pages/CropsPage";
import AdminMetricsPage from "./pages/AdminMetricsPage";
import AdminFeedbackPage from "./pages/AdminFeedbackPage";
import ProtectedRoute from "./components/ProtectedRoute";
import AppShell from "./components/Appshell";

function ExternalRedirect({ to }: { to: string }) {
  window.location.href = to;
  return null;
}

export default function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      <Route path="/crops" element={<CropsPage />} />
      <Route path="/docs" element={<ExternalRedirect to="http://localhost:8000/docs" />} />

      {/* Authenticated Routes wrapped inside AppShell */}
      <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/predictions/:id" element={<PredictionResultPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/farm/settings" element={<FarmSettingsPage />} />
        <Route path="/weather" element={<WeatherPage />} />

        {/* Admin Only Routes */}
        <Route path="/admin/metrics" element={<ProtectedRoute adminOnly><AdminMetricsPage /></ProtectedRoute>} />
        <Route path="/admin/feedback" element={<ProtectedRoute adminOnly><AdminFeedbackPage /></ProtectedRoute>} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}