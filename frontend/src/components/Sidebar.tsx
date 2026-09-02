import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { 
  Bell,
  LayoutDashboard, 
  Scan, 
  History, 
  MapPin, 
  CloudSun, 
  Sprout, 
  ShieldAlert, 
  FileText, 
  LogOut 
} from "lucide-react";


import { useQuery } from "@tanstack/react-query";
import { request } from "../api/client";
import { useState } from "react";

export default function Sidebar() {
  const { user, token, signOut } = useAuth();
  const navigate = useNavigate();
  const isAdmin = user?.role === "admin" || user?.role === "expert";

  const { data: alerts = [], refetch: refetchAlerts } = useQuery({
    queryKey: ["alerts"],
    queryFn: () => request<any[]>("/alerts", {}, token!),
    enabled: !!token,
    refetchInterval: 15000,
  });

  const unreadCount = alerts.filter((a: any) => !a.is_read).length;
  const [showNotifications, setShowNotifications] = useState(false);

  const markRead = async (id: number) => {
    await request(`/alerts/${id}/read`, { method: "POST" }, token!);
    refetchAlerts();
  };


  const handleSignOut = () => {
    signOut();
    navigate("/auth/login");
  };

  return (
    <aside className="app-sidebar">
      <div className="sidebar-header">
        <div className="logo-icon">🌿</div>
        <div className="logo-text">
          <h2>Smart Farming</h2>
          <span className="user-role-badge">{user?.role || "Farmer"}</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section">
          <span className="nav-section-title">Core</span>
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </NavLink>
          <NavLink to="/scan" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            <Scan size={20} />
            <span>AI Diagnostic Scan</span>
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            <History size={20} />
            <span>Scan History</span>
          </NavLink>
        </div>

        <div className="nav-section">
          <span className="nav-section-title">Management</span>
          <NavLink to="/farm/settings" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            <MapPin size={20} />
            <span>Farm Settings</span>
          </NavLink>
          <NavLink to="/weather" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            <CloudSun size={20} />
            <span>Weather Advisory</span>
          </NavLink>
          <NavLink to="/crops" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            <Sprout size={20} />
            <span>Supported Crops</span>
          </NavLink>
        </div>

        {isAdmin && (
          <div className="nav-section">
            <span className="nav-section-title">Administration</span>
            <NavLink to="/admin/metrics" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              <ShieldAlert size={20} />
              <span>System Metrics</span>
            </NavLink>
            <NavLink to="/admin/feedback" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              <FileText size={20} />
              <span>Expert Feedback</span>
            </NavLink>
            <NavLink to="/admin/expert" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              <ShieldAlert size={20} />
              <span>Expert Triage Queue</span>
            </NavLink>
          </div>
        )}
      </nav>

      <div className="sidebar-footer">
        <div className="user-profile-snippet">
          <div className="avatar">{user?.name ? user.name.charAt(0).toUpperCase() : "F"}</div>
          <div className="user-info">
            <span className="user-name">{user?.name || "Farmer"}</span>
            <span className="user-email">{user?.email || user?.phone || ""}</span>
          </div>
        </div>
        <button onClick={handleSignOut} className="btn-signout" title="Sign Out">
          <LogOut size={18} />
        </button>
      </div>
    </aside>
  );
}