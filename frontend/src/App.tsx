import { useEffect } from "react";
import { Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import AboutPage from "./pages/AboutPage";
import ServicesPage from "./pages/ServicesPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import VerifyEmailPage from "./pages/VerifyEmailPage";
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
import AdminUsersPage from "./pages/AdminUsersPage";
import ExpertQueuePage from "./pages/ExpertQueuePage";
import ExpertReviewPage from "./pages/ExpertReviewPage";
import AlertsPage from "./pages/AlertsPage";
import TermsPage from "./pages/TermsPage";
import PrivacyPage from "./pages/PrivacyPage";
import ProtectedRoute from "./components/ProtectedRoute";
import AppShell from "./components/Appshell";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { getApiUrl } from "./api/client";

function ExternalRedirect({ to }: { to: string }) {
  window.location.href = to;
  return null;
}

function AuthHashHandler() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const hash = window.location.hash;
    if (!hash) return;

    const params = new URLSearchParams(hash.startsWith("#") ? hash.substring(1) : hash);
    const hasError = params.has("error") || params.has("error_code") || params.has("error_description");
    const type = params.get("type");

    if (location.pathname === "/") {
      if (hasError) {
        if (type === "recovery") {
          navigate(`/auth/reset-password${window.location.hash}`, { replace: true });
        } else {
          navigate(`/auth/verify-email${window.location.hash}`, { replace: true });
        }
      } else if (type === "recovery") {
        navigate(`/auth/reset-password${window.location.hash}`, { replace: true });
      } else if (type === "signup" || type === "email_change") {
        navigate(`/auth/verify-email${window.location.hash}`, { replace: true });
      }
    }
  }, [navigate, location.pathname]);

  return null;
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AuthHashHandler />
        <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/services" element={<ServicesPage />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      <Route path="/auth/verify-email" element={<VerifyEmailPage />} />
      <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/auth/reset-password" element={<ResetPasswordPage />} />
      <Route path="/crops" element={<CropsPage />} />
      <Route path="/docs" element={<ExternalRedirect to={`${getApiUrl()}/docs`} />} />

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
        <Route path="/alerts" element={<AlertsPage />} />

        {/* Admin Only Routes */}
        <Route path="/admin/metrics" element={<ProtectedRoute strictAdminOnly><AdminMetricsPage /></ProtectedRoute>} />
        <Route path="/admin/users" element={<ProtectedRoute strictAdminOnly><AdminUsersPage /></ProtectedRoute>} />
        <Route path="/admin/feedback" element={<ProtectedRoute adminOnly><AdminFeedbackPage /></ProtectedRoute>} />
        <Route path="/admin/expert" element={<ProtectedRoute adminOnly><ExpertQueuePage /></ProtectedRoute>} />
        <Route path="/admin/expert/:id" element={<ProtectedRoute adminOnly><ExpertReviewPage /></ProtectedRoute>} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  </ThemeProvider>
  );
}
