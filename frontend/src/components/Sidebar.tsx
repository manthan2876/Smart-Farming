import {
  Activity,
  Bell,
  Camera,
  ChevronDown,
  Leaf,
  LogOut,
  Settings,
  ShieldCheck,
  Sprout,
  UserRound,
  BarChart3,
  Tractor,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { dictionary, type Language } from "../i18n";

type Page =
  | "overview"
  | "scan"
  | "history"
  | "farm"
  | "alerts"
  | "profile"
  | "settings"
  | "admin"
  | "expert";
type Props = { active: Page; onNavigate: (page: Page) => void };

export function Sidebar({ active, onNavigate }: Props) {
  const navigate = useNavigate();
  const { user, signOut, language } = useAuth();
  const labels = dictionary((language || "English") as Language);
  function logout() {
    signOut();
    navigate("/");
  }
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">
          <Leaf size={18} />
        </span>
        <span>
          fieldnote<small>smart farming</small>
        </span>
      </div>
      <div className="season-tag">
        <span className="pulse-dot" /> Kharif season <b>•</b> 2026
      </div>
      <nav>
        <button
          className={active === "overview" ? "nav-active" : ""}
          onClick={() => onNavigate("overview")}
        >
          <Activity size={18} /> {labels.dashboard}
        </button>
        <button
          className={active === "scan" ? "nav-active" : ""}
          onClick={() => onNavigate("scan")}
        >
          <Camera size={18} /> {labels.scan} <span className="nav-key">N</span>
        </button>
        <button
          className={active === "history" ? "nav-active" : ""}
          onClick={() => onNavigate("history")}
        >
          <Sprout size={18} /> {labels.history}
        </button>
        <button
          className={active === "farm" ? "nav-active" : ""}
          onClick={() => onNavigate("farm")}
        >
          <Tractor size={18} /> {labels.farm}
        </button>
        <button
          className={active === "alerts" ? "nav-active" : ""}
          onClick={() => onNavigate("alerts")}
        >
          <Bell size={18} /> {labels.alerts}
        </button>
        <button
          className={active === "profile" ? "nav-active" : ""}
          onClick={() => onNavigate("profile")}
        >
          <UserRound size={18} /> {labels.profile}
        </button>
        <button
          className={active === "settings" ? "nav-active" : ""}
          onClick={() => onNavigate("settings")}
        >
          <Settings size={18} /> {labels.settings}
        </button>
        {(user?.role === "expert" || user?.role === "admin") && (
          <button
            className={active === "expert" ? "nav-active" : ""}
            onClick={() => onNavigate("expert")}
          >
            <ShieldCheck size={18} /> Expert queue
          </button>
        )}
        {user?.role === "admin" && (
          <button
            className={active === "admin" ? "nav-active" : ""}
            onClick={() => onNavigate("admin")}
          >
            <BarChart3 size={18} /> Admin metrics
          </button>
        )}
      </nav>
      <div className="sidebar-note">
        <ShieldCheck size={20} />
        <p>Your crop data stays linked to your farm profile.</p>
      </div>
      <button className="logout-button" onClick={logout}>
        <LogOut size={16} /> {labels.logout}
      </button>
      <div className="profile-mini">
        <div className="avatar">
          {user?.name?.slice(0, 2).toUpperCase() ?? "MP"}
        </div>
        <div>
          <strong>{user?.name ?? "Farmer"}</strong>
          <span>{user?.location ?? "Set your farm location"}</span>
        </div>
        <ChevronDown size={15} />
      </div>
    </aside>
  );
}
