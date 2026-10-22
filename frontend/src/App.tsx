import { lazy, Suspense, useEffect } from "react";
import { Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import AppErrorBoundary from "./components/AppErrorBoundary";
import ProtectedRoute from "./components/ProtectedRoute";
import AppShell from "./components/Appshell";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { useAuth } from "./context/AuthContext";
import { getApiUrl } from "./api/client";
import { Analytics } from "@vercel/analytics/react";

const LandingPage = lazy(() => import("./pages/LandingPage"));
const AboutPage = lazy(() => import("./pages/AboutPage"));
const ServicesPage = lazy(() => import("./pages/ServicesPage"));
const LoginPage = lazy(() => import("./pages/LoginPage"));
const RegisterPage = lazy(() => import("./pages/RegisterPage"));
const ForgotPasswordPage = lazy(() => import("./pages/ForgotPasswordPage"));
const ResetPasswordPage = lazy(() => import("./pages/ResetPasswordPage"));
const VerifyEmailPage = lazy(() => import("./pages/VerifyEmailPage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const ScanPage = lazy(() => import("./pages/ScanPage"));
const PredictionResultPage = lazy(() => import("./pages/PredictionResultPage"));
const ProcessingPage = lazy(() => import("./pages/ProcessingPage"));
const HistoryPage = lazy(() => import("./pages/HistoryPage"));
const FarmSettingsPage = lazy(() => import("./pages/FarmSettingsPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));
const WeatherPage = lazy(() => import("./pages/WeatherPage"));
const CropsPage = lazy(() => import("./pages/CropsPage"));
const AdminMetricsPage = lazy(() => import("./pages/AdminMetricsPage"));
const AdminFeedbackPage = lazy(() => import("./pages/AdminFeedbackPage"));
const AdminUsersPage = lazy(() => import("./pages/AdminUsersPage"));
const ExpertQueuePage = lazy(() => import("./pages/ExpertQueuePage"));
const ExpertReviewPage = lazy(() => import("./pages/ExpertReviewPage"));
const AlertsPage = lazy(() => import("./pages/AlertsPage"));
const TermsPage = lazy(() => import("./pages/TermsPage"));
const PrivacyPage = lazy(() => import("./pages/PrivacyPage"));

function AppErrorFallback() {
  const { t } = useAuth();
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col items-center justify-center gap-4 p-6 text-center">
      <p role="alert">{t("renderErrorMessage")}</p>
      <button className="rounded-sm border px-4 py-2" onClick={() => window.location.reload()}>
        {t("retry")}
      </button>
    </main>
  );
}

function RouteLoadingFallback() {
  const { t } = useAuth();
  return <div className="p-6 text-center" role="status">{t("loading")}</div>;
}

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
      <AppErrorBoundary fallback={<AppErrorFallback />}>
      <Suspense fallback={<RouteLoadingFallback />}>
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
        </Suspense>
        </AppErrorBoundary>
      <Analytics />
    </AuthProvider>
  </ThemeProvider>
  );
}
