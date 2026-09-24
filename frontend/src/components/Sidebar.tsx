import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { 
  Bell,
  LayoutDashboard, 
  Scan, 
  History, 
  MapPin,
  Settings, 
  CloudSun, 
  Sprout, 
  ShieldAlert, 
  FileText, 
  LogOut,
  Menu,
  X,
  Users,
  GraduationCap,
  ClipboardList,
} from "lucide-react";

import { useQuery } from "@tanstack/react-query";
import { request } from "../api/client";
import { useState } from "react";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { user, token, signOut, t } = useAuth();
  const navigate = useNavigate();
  const isExpert = user?.role === "expert";
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

  const badgeBg = isSuperAdmin
    ? "bg-blue-100 text-blue-800"
    : isExpert
    ? "bg-purple-100 text-purple-800"
    : "bg-farmer-100 text-farmer-800";

  const avatarBg = isSuperAdmin
    ? "bg-blue-700"
    : isExpert
    ? "bg-purple-700"
    : "bg-farmer-700";

  return (
    <>
      {showNotifications && (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-ink/20 backdrop-blur-[1px]"
          onClick={(event) => {
            if (event.target === event.currentTarget) {
              setShowNotifications(false);
            }
          }}
          aria-label="Close notifications"
        />
      )}
      {isOpen && <button type="button" className="fixed inset-0 z-40 bg-ink/30 lg:hidden" onClick={onClose} aria-label="Close navigation" />}
      <aside className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col overflow-visible border-r border-line bg-surface transition-transform duration-200 lg:z-30 lg:translate-x-0 ${isOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="relative flex items-center justify-between border-b border-line px-5 py-5">
          <div className="flex min-w-0 items-center gap-3">
            <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-md ${avatarBg} text-xl text-white shadow-soft`}>SF</div>
            <div className="min-w-0">
              <h2 className="truncate font-display text-lg text-ink">Smart Farming</h2>
              <span className={`mt-1 inline-flex rounded-full px-2 py-0.5 text-[0.68rem] font-bold uppercase tracking-wide ${badgeBg}`}>
                {user?.role === "expert" ? t("roleExpert") : user?.role === "admin" ? t("roleAdmin") : t("roleFarmer")}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button type="button" className="relative rounded-sm p-2 text-muted hover:bg-canvas hover:text-ink" onClick={() => setShowNotifications(!showNotifications)} aria-label="Open notifications" aria-expanded={showNotifications}>
              <Bell size={19} />
              {unreadCount > 0 && <span className="absolute right-0.5 top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-danger px-1 text-[0.6rem] font-bold text-white">{unreadCount}</span>}
            </button>
            <button type="button" className="rounded-sm p-2 text-muted hover:bg-canvas hover:text-ink lg:hidden" onClick={onClose} aria-label="Close navigation"><X size={19} /></button>
          </div>
          {unreadCount > 0 && (
            <span className="sr-only">{unreadCount} unread notifications</span>
          )}

        {showNotifications && (
          <div
            className="fixed left-3 top-16 z-[60] max-h-[24rem] w-[calc(100vw-2rem)] overflow-y-auto rounded-md border border-line bg-surface shadow-lift pointer-events-auto lg:left-[18rem] lg:w-[22rem]"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-line p-4 font-semibold">
              <span>{t("notifications")}</span>
              <button type="button" className="text-xs font-semibold text-farmer-700 hover:text-farmer-900" onClick={() => { alerts.filter(a => !a.is_read).forEach(a => markRead(a.id)); setShowNotifications(false); }}>{t("markAllRead")}</button>
            </div>
            {alerts.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted">{t("noNewAlerts")}</div>
            ) : (
              alerts.map((alert: any) => (
                <div key={alert.id} className={`border-b border-line p-4 last:border-0 ${alert.is_read ? "bg-surface" : "bg-farmer-50"}`}>
                  <div className="mb-1 break-words text-sm font-bold text-ink">{alert.title}</div>
                  <div className="mb-2 break-words text-xs leading-5 text-muted">{alert.body}</div>
                  {!alert.is_read && (
                    <button onClick={() => markRead(alert.id)} className="p-0 text-xs font-semibold text-farmer-700 hover:text-farmer-900">{t("markAsRead")}</button>
                  )}
                </div>
              ))
            )}
          </div>
        )}
        </div>

        <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-6">
          {/* DEDICATED EXPERT WORKFLOW */}
          {isExpert ? (
            <>
              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.68rem] font-bold uppercase tracking-[0.14em] text-purple-700">{t("agronomyDesk")}</span>
                <NavLink onClick={onClose} to="/admin/expert" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-purple-100 text-purple-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <ClipboardList size={18} />
                  <span>{t("reviewQueue")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/admin/feedback" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-purple-100 text-purple-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <FileText size={18} />
                  <span>{t("feedbackAudits")}</span>
                </NavLink>
              </div>

              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.68rem] font-bold uppercase tracking-[0.14em] text-muted">{t("fieldTools")}</span>
                <NavLink onClick={onClose} to="/scan" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-purple-100 text-purple-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <Scan size={18} />
                  <span>{t("diagnosticScanner")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/history" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-purple-100 text-purple-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <History size={18} />
                  <span>{t("history")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/weather" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-purple-100 text-purple-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <CloudSun size={18} />
                  <span>{t("weatherAdvisory")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/alerts" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-purple-100 text-purple-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <Bell size={18} />
                  <span>{t("alerts")}</span>
                  {unreadCount > 0 && (
                    <span className="ml-auto rounded-full bg-danger px-1.5 py-0.5 text-[0.65rem] font-bold text-white">
                      {unreadCount}
                    </span>
                  )}
                </NavLink>
              </div>

              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.68rem] font-bold uppercase tracking-[0.14em] text-muted">{t("account")}</span>
                <NavLink onClick={onClose} to="/settings" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-purple-100 text-purple-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <Settings size={18} />
                  <span>{t("settings")}</span>
                </NavLink>
              </div>
            </>
          ) : isSuperAdmin ? (
            /* DEDICATED SUPER ADMIN WORKFLOW */
            <>
              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.68rem] font-bold uppercase tracking-[0.14em] text-blue-700">{t("platformControl")}</span>
                <NavLink onClick={onClose} to="/admin/metrics" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-blue-100 text-blue-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <ShieldAlert size={18} />
                  <span>{t("metricsMlops")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/admin/users" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-blue-100 text-blue-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <Users size={18} />
                  <span>{t("userRoles")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/admin/expert" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-blue-100 text-blue-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <ClipboardList size={18} />
                  <span>{t("reviewQueue")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/admin/feedback" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-blue-100 text-blue-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <FileText size={18} />
                  <span>{t("feedbackLogs")}</span>
                </NavLink>
              </div>

              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.68rem] font-bold uppercase tracking-[0.14em] text-muted">{t("operations")}</span>
                <NavLink onClick={onClose} to="/dashboard" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <LayoutDashboard size={18} />
                  <span>{t("dashboard")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/scan" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <Scan size={18} />
                  <span>{t("scan")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/history" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <History size={18} />
                  <span>{t("history")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/farm/settings" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <MapPin size={18} />
                  <span>{t("farmPlots")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/weather" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <CloudSun size={18} />
                  <span>{t("weather")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/alerts" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <Bell size={18} />
                  <span>{t("alerts")}</span>
                  {unreadCount > 0 && (
                    <span className="ml-auto rounded-full bg-danger px-1.5 py-0.5 text-[0.65rem] font-bold text-white">
                      {unreadCount}
                    </span>
                  )}
                </NavLink>
              </div>

              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.68rem] font-bold uppercase tracking-[0.14em] text-muted">{t("account")}</span>
                <NavLink onClick={onClose} to="/settings" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <Settings size={18} />
                  <span>{t("settings")}</span>
                </NavLink>
              </div>
            </>
          ) : (
            /* STANDARD GROWER WORKFLOW */
            <>
              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.68rem] font-bold uppercase tracking-[0.14em] text-muted">{t("core")}</span>
                <NavLink onClick={onClose} to="/dashboard" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <LayoutDashboard size={18} />
                  <span>{t("dashboard")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/scan" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <Scan size={18} />
                  <span>{t("scan")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/history" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <History size={18} />
                  <span>{t("history")}</span>
                </NavLink>
              </div>

              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.68rem] font-bold uppercase tracking-[0.14em] text-muted">{t("management")}</span>
                <NavLink onClick={onClose} to="/farm/settings" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <MapPin size={18} />
                  <span>{t("farm")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/alerts" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <Bell size={18} />
                  <span>{t("alerts")}</span>
                  {unreadCount > 0 && (
                    <span className="ml-auto rounded-full bg-danger px-1.5 py-0.5 text-[0.65rem] font-bold text-white">
                      {unreadCount}
                    </span>
                  )}
                </NavLink>
                <NavLink onClick={onClose} to="/weather" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <CloudSun size={18} />
                  <span>{t("weatherAdvisory")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/settings" className={({ isActive }) => `flex items-center gap-3 rounded-sm px-3 py-3 text-sm font-semibold transition-colors ${isActive ? "bg-farmer-100 text-farmer-900" : "text-muted hover:bg-canvas hover:text-ink"}`}>
                  <Settings size={18} />
                  <span>{t("settings")}</span>
                </NavLink>
              </div>
            </>
          )}
        </nav>


        <div className="flex items-center justify-between gap-3 border-t border-line bg-canvas/40 p-4">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-farmer-700 text-sm font-bold text-white">{user?.name ? user.name.charAt(0).toUpperCase() : "F"}</div>
            <div className="min-w-0">
              <span className="block truncate text-sm font-semibold text-ink">
                {user?.name === "Admin User" || user?.name === "Super Administrator" || user?.name === "Administrator"
                  ? t("roleAdmin")
                  : user?.name === "Expert Agronomist" || user?.name === "Expert User" || user?.name === "Expert"
                  ? t("roleExpert")
                  : user?.name === "Farmer User" || user?.name === "Farmer"
                  ? t("roleFarmer")
                  : user?.name || (user?.role === "expert" ? t("roleExpert") : user?.role === "admin" ? t("roleAdmin") : t("roleFarmer"))}
              </span>
              <span className="block truncate text-xs text-muted">{user?.email || user?.phone || ""}</span>
            </div>
          </div>
          <button onClick={handleSignOut} className="rounded-sm p-2 text-muted hover:bg-red-50 hover:text-danger" title={t("logout")} aria-label={t("logout")}>
            <LogOut size={18} />
          </button>
        </div>
      </aside>
    </>
  );
}