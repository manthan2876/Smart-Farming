import { Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import AboutPage from "./pages/AboutPage";
import ServicesPage from "./pages/ServicesPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import ScanPage from "./pages/ScanPage";
import PredictionResultPage from "./pages/PredictionResultPage";
import ProcessingPage from "./pages/ProcessingPage";
import HistoryPage from "./pages/HistoryPage";
import FarmSettingsPage from "./pages/FarmSettingsPage";
import SettingsPage from "./pages/SettingsPage";
import WeatherPage from "./pages/WeatherPage";
import CropsPage from "./pages/CropsPage";
import AdminMetricsPage from "./pages/AdminMetricsPage";
import AdminFeedbackPage from "./pages/AdminFeedbackPage";
import ExpertQueuePage from "./pages/ExpertQueuePage";
import ExpertReviewPage from "./pages/ExpertReviewPage";
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
      <Route path="/about" element={<AboutPage />} />
      <Route path="/services" element={<ServicesPage />} />
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      <Route path="/crops" element={<CropsPage />} />
      <Route path="/docs" element={<ExternalRedirect to="http://localhost:8000/docs" />} />

      {/* Authenticated Routes wrapped inside AppShell */}
      <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/predictions/:id/processing" element={<ProcessingPage />} />
        <Route path="/predictions/:id" element={<PredictionResultPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/farm/settings" element={<FarmSettingsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        <Route path="/weather" element={<WeatherPage />} />

        {/* Admin Only Routes */}
        <Route path="/admin/metrics" element={<ProtectedRoute strictAdminOnly><AdminMetricsPage /></ProtectedRoute>} />
        <Route path="/admin/feedback" element={<ProtectedRoute adminOnly><AdminFeedbackPage /></ProtectedRoute>} />
        <Route path="/admin/expert" element={<ProtectedRoute adminOnly><ExpertQueuePage /></ProtectedRoute>} />
        <Route path="/admin/expert/:id" element={<ProtectedRoute adminOnly><ExpertReviewPage /></ProtectedRoute>} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
