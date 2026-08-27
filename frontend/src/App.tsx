import { useRef, useState, type ReactNode } from "react";
import { Activity, CloudSun, X } from "lucide-react";
import {
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { demoPrediction, type Prediction } from "./api/types";
import { history as getHistory } from "./api/predictions";
import { AuthPanel } from "./components/AuthPanel";
import { Sidebar } from "./components/Sidebar";
import { Topbar } from "./components/Topbar";
import { useAuth } from "./context/AuthContext";
import { usePredict } from "./hooks/usePredict";
import { HistoryPage } from "./pages/HistoryPage";
import { AuthPage } from "./pages/AuthPage";
import { ProfilePage } from "./pages/ProfilePage";
import { AdminPage } from "./pages/AdminPage";
import { ResultPage } from "./pages/ResultPage";
import { ProcessingPage } from "./pages/ProcessingPage";
import { FarmPage } from "./pages/FarmPage";
import { AlertsPage } from "./pages/AlertsPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ExpertPage } from "./pages/ExpertPage";
import { ExpertReviewPage } from "./pages/ExpertReviewPage";
import { AdminDataPage } from "./pages/AdminDataPage";
import { MlopsPage } from "./pages/MlopsPage";
import { Overview } from "./pages/Overview";
import { ScanPage } from "./pages/ScanPage";
import { LandingPage } from "./pages/LandingPage";
export type Page =
  | "overview"
  | "scan"
  | "history"
  | "farm"
  | "alerts"
  | "profile"
  | "settings"
  | "admin"
  | "expert";
const historySeed: Prediction[] = [
  demoPrediction,
  {
    ...demoPrediction,
    prediction_id: 198,
    disease: { label: "Leaf mold", confidence: 0.79 },
    severity: { percent: 19, bucket: "low" },
  },
  {
    ...demoPrediction,
    prediction_id: 193,
    disease: { label: "Healthy", confidence: 0.97 },
    severity: { percent: 4, bucket: "low" },
  },
];

function RoleGate({
  role,
  allowed,
  children,
}: {
  role?: string;
  allowed: string[];
  children: ReactNode;
}) {
  return allowed.includes(role ?? "") ? (
    children
  ) : (
    <Navigate to="/dashboard" replace />
  );
}

export default function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const { token, user, ready } = useAuth();
  const [selected, setSelected] = useState<Prediction>(demoPrediction);
  const { data: liveHistory = [] } = useQuery({
    queryKey: ["history", token],
    queryFn: () => getHistory(token!),
    enabled: Boolean(token),
  });
  const history = liveHistory.length ? liveHistory : historySeed;
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("/aphids_tomato.jpeg");
  const [authOpen, setAuthOpen] = useState(false);
  const [notice, setNotice] = useState(
    "Demo data is on. Connect the API to run a live scan.",
  );
  const inputRef = useRef<HTMLInputElement>(null);
  const authenticated = Boolean(token);
  const predictionMutation = usePredict();
  function chooseFile(next: File | undefined) {
    if (!next) {
      setFile(null);
      setPreview("/aphids_tomato.jpeg");
      return;
    }
    setFile(next);
    setPreview(URL.createObjectURL(next));
    navigate("/upload");
    setNotice("Ready to read this leaf.");
  }
  async function runScan() {
    if (!file) {
      setNotice("Choose a leaf image first.");
      return;
    }
    setNotice("Reading texture, color, and field conditions…");
    try {
      navigate(`/scan/processing/${Date.now()}`);
      const result = await predictionMutation.mutateAsync({
        file,
        location: "North plot",
        language: "English",
      });
      setSelected(result);
      navigate(`/result/${result.prediction_id ?? ""}`);
      setNotice("Live scan complete.");
    } catch {
      setSelected(demoPrediction);
      navigate("/");
      setNotice(
        "API is offline or needs an account, so the demo result is shown.",
      );
    }
  }
  if (!ready)
    return <div className="app-loading">Opening your field journal…</div>;
  const active: Page =
    location.pathname === "/scan" || location.pathname === "/upload"
      ? "scan"
      : location.pathname === "/history"
        ? "history"
        : location.pathname === "/farm"
          ? "farm"
          : location.pathname === "/alerts"
            ? "alerts"
            : location.pathname === "/profile"
              ? "profile"
              : location.pathname === "/settings"
                ? "settings"
                : location.pathname.startsWith("/expert")
                  ? "expert"
                  : location.pathname.startsWith("/admin")
                    ? "admin"
                    : "overview";
  function selectPrediction(item: Prediction) {
    setSelected(item);
    navigate(`/result/${item.prediction_id ?? ""}`);
  }
  const pageLabel =
    active === "scan"
      ? "New scan"
      : active === "history"
        ? "Scan history"
        : active === "farm"
          ? "My farm"
          : active === "alerts"
            ? "Alerts"
            : active === "profile"
              ? "Farm profile"
              : active === "settings"
                ? "Settings"
                : active === "expert"
                  ? "Expert queue"
                  : active === "admin"
                    ? "Admin metrics"
                    : "Field pulse";
  function navigatePage(page: Page) {
    navigate(
      page === "scan"
        ? "/scan"
        : page === "history"
          ? "/history"
          : page === "farm"
            ? "/farm"
            : page === "alerts"
              ? "/alerts"
              : page === "profile"
                ? "/profile"
                : page === "settings"
                  ? "/settings"
                  : page === "expert"
                    ? "/expert"
                    : page === "admin"
                      ? "/admin"
                      : "/dashboard",
    );
  }
  if (location.pathname === "/login" || location.pathname === "/register")
    return (
      <AuthPage
        mode={location.pathname === "/register" ? "register" : "login"}
      />
    );
  if (!token) return <LandingPage />;
  return (
    <div className="app-shell">
      <Sidebar active={active} onNavigate={navigatePage} />
      <main>
        <Topbar active={active} />
        <div className="content">
          <section className="welcome">
            <div>
              <p className="eyebrow">North plot · Anand, Gujarat</p>
              <h1>
                Good morning, <em>Manthan.</em>
              </h1>
              <p className="subcopy">
                One clear leaf photo can tell you what your crop needs next.
              </p>
            </div>
            <div className="weather">
              <CloudSun size={28} />
              <div>
                <strong>27°C</strong>
                <span>Clear skies · 68% humidity</span>
              </div>
            </div>
          </section>
          {!authenticated && (
            <button
              className="connect-banner"
              onClick={() => setAuthOpen(true)}
            >
              <Activity size={15} />
              <span>
                <b>Connect your farm account</b>
                <small>Unlock live history and scan sync</small>
              </span>
              <span className="connect-action">Sign in →</span>
            </button>
          )}
          {notice && (
            <div className="notice">
              <span>
                <Activity size={15} /> {notice}
              </span>
              <button onClick={() => setNotice("")}>
                <X size={15} />
              </button>
            </div>
          )}
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route
              path="/dashboard"
              element={
                <Overview
                  prediction={selected}
                  onScan={() => navigate("/scan")}
                  onSelect={selectPrediction}
                  onHistory={() => navigate("/history")}
                  history={history}
                />
              }
            />
            <Route
              path="/scan"
              element={
                <ScanPage
                  preview={preview}
                  file={file}
                  busy={predictionMutation.isPending}
                  inputRef={inputRef}
                  onChoose={chooseFile}
                  onRun={runScan}
                />
              }
            />
            <Route path="/upload" element={<Navigate to="/scan" replace />} />
            <Route path="/scan/processing/:id" element={<ProcessingPage />} />
            <Route
              path="/result/:id"
              element={
                <ResultPage
                  prediction={selected}
                  onBack={() => navigate("/history")}
                />
              }
            />
            <Route
              path="/history"
              element={
                <HistoryPage history={history} onSelect={selectPrediction} />
              }
            />
            <Route
              path="/farm"
              element={<FarmPage history={history} profile={user} />}
            />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route
              path="/expert"
              element={
                <RoleGate role={user?.role} allowed={["expert", "admin"]}>
                  <ExpertPage />
                </RoleGate>
              }
            />
            <Route
              path="/expert/review/:id"
              element={
                <RoleGate role={user?.role} allowed={["expert", "admin"]}>
                  <ExpertReviewPage />
                </RoleGate>
              }
            />
            <Route
              path="/admin"
              element={
                <RoleGate role={user?.role} allowed={["admin"]}>
                  <AdminPage />
                </RoleGate>
              }
            />
            <Route
              path="/admin/predictions"
              element={
                <RoleGate role={user?.role} allowed={["admin"]}>
                  <AdminDataPage kind="predictions" />
                </RoleGate>
              }
            />
            <Route
              path="/admin/feedback"
              element={
                <RoleGate role={user?.role} allowed={["admin"]}>
                  <AdminDataPage kind="feedback" />
                </RoleGate>
              }
            />
            <Route
              path="/admin/mlops"
              element={
                <RoleGate role={user?.role} allowed={["admin"]}>
                  <MlopsPage />
                </RoleGate>
              }
            />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          <span className="sr-only">Current page: {pageLabel}</span>
        </div>
      </main>
      {authOpen && (
        <AuthPanel
          onClose={() => setAuthOpen(false)}
          onLoggedIn={() =>
            setNotice("Account connected. Live field data is now available.")
          }
        />
      )}
    </div>
  );
}