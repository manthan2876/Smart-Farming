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
  const isSuperAdmin = user?.role === "admin";

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
      <div className="sidebar-header" style={{ position: 'relative', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div className="logo-icon">🌿</div>
          <div className="logo-text">
            <h2>Smart Farming</h2>
            <span className="user-role-badge">{user?.role || "Farmer"}</span>
          </div>
        </div>
        
        <div className="notification-bell" style={{ position: 'relative', cursor: 'pointer', color: 'var(--muted)' }} onClick={() => setShowNotifications(!showNotifications)}>
          <Bell size={24} />
          {unreadCount > 0 && (
            <span style={{ position: 'absolute', top: -4, right: -4, background: '#ef4444', color: 'white', borderRadius: '50%', width: 16, height: 16, fontSize: '0.65rem', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
              {unreadCount}
            </span>
          )}
        </div>

        {showNotifications && (
          <div className="notifications-dropdown" style={{ position: 'absolute', top: '100%', right: 0, width: '280px', background: 'white', border: '1px solid var(--line)', borderRadius: '8px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)', zIndex: 50, maxHeight: '400px', overflowY: 'auto' }}>
            <div style={{ padding: '1rem', borderBottom: '1px solid var(--line)', fontWeight: 'bold', display: 'flex', justifyContent: 'space-between' }}>
              <span>Notifications</span>
              <span style={{ fontSize: '0.8rem', color: 'var(--green)', cursor: 'pointer' }} onClick={() => { alerts.filter(a => !a.is_read).forEach(a => markRead(a.id)); setShowNotifications(false); }}>Mark all read</span>
            </div>
            {alerts.length === 0 ? (
              <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--muted)', fontSize: '0.9rem' }}>No new alerts</div>
            ) : (
              alerts.map((alert: any) => (
                <div key={alert.id} style={{ padding: '1rem', borderBottom: '1px solid var(--line)', background: alert.is_read ? 'white' : '#f0fdf4' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '0.9rem', marginBottom: '0.25rem', color: 'var(--ink)' }}>{alert.title}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>{alert.body}</div>
                  {!alert.is_read && (
                    <button onClick={() => markRead(alert.id)} style={{ fontSize: '0.75rem', background: 'none', border: 'none', color: 'var(--green)', cursor: 'pointer', padding: 0 }}>Mark as read</button>
                  )}
                </div>
              ))
            )}
          </div>
        )}
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

        </div>

        {isAdmin && (
          <div className="nav-section">
            <span className="nav-section-title">Administration</span>
            {isSuperAdmin && (
              <NavLink to="/admin/metrics" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
                <ShieldAlert size={20} />
                <span>System Metrics</span>
              </NavLink>
            )}
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