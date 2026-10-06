import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { 
  Bell,
  LayoutDashboard, 
  Scan, 
  History, 
  MapPin,
  Settings, 
  CloudSun, 
  ShieldAlert, 
  FileText, 
  LogOut,
  X,
  Users,
  ClipboardList,
} from "./icons";

import { useQuery } from "@tanstack/react-query";
import { request } from "../api/client";
import { useState } from "react";

import ThemeToggle from "./ThemeToggle";
import LanguageToggle from "./LanguageToggle";
import { translateAlertTitle } from "../i18n/domain";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { user, token, signOut, t, language } = useAuth();
  const navigate = useNavigate();
  const isExpert = user?.role === "expert";
  const isSuperAdmin = user?.role === "admin";

  const { data: alerts = [], refetch: refetchAlerts } = useQuery({
    queryKey: ["alerts", language],
    queryFn: () => request<any[]>(`/alerts?lang=${encodeURIComponent(language)}`, {}, token!),
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

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 rounded-sm px-3 py-2.5 text-sm transition-colors ${
      isActive
        ? "bg-farmer-100 font-semibold text-farmer-900 border-l-2 border-farmer-700 dark:bg-farmer-900/60 dark:text-farmer-100 dark:border-farmer-400"
        : "text-muted hover:bg-canvas hover:text-ink"
    }`;

  return (
    <>
      {showNotifications && (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-ink/30"
          onClick={(event) => {
            if (event.target === event.currentTarget) {
              setShowNotifications(false);
            }
          }}
          aria-label="Close notifications"
        />
      )}
      {isOpen && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-ink/40 lg:hidden"
          onClick={onClose}
          aria-label="Close navigation"
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-line bg-surface transition-transform duration-200 lg:z-30 lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="relative flex items-center justify-between border-b border-line px-4 py-4 sm:px-5">
          <div className="flex min-w-0 flex-1 items-center gap-2.5">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-sm bg-farmer-700 text-sm font-bold text-white">
              SF
            </div>
            <div className="min-w-0 flex-1">
              <h2 className="truncate font-display text-base text-ink">Smart Farming</h2>
              <span className="mt-0.5 inline-flex whitespace-nowrap rounded-xs border border-line bg-canvas px-1.5 py-0.5 text-[0.62rem] font-semibold uppercase tracking-wider text-muted">
                {user?.role === "expert" ? t("roleExpert") : user?.role === "admin" ? t("roleAdmin") : t("roleFarmer")}
              </span>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-1">
            <LanguageToggle />
            <ThemeToggle />
            <button
              type="button"
              className="relative rounded-sm p-2 text-muted hover:bg-canvas hover:text-ink transition-colors"
              onClick={() => setShowNotifications(!showNotifications)}
              aria-label="Open notifications"
              aria-expanded={showNotifications}
            >
              <Bell size={18} />
              {unreadCount > 0 && (
                <span className="absolute right-1 top-1 flex h-4 min-w-4 items-center justify-center rounded-xs bg-danger px-1 text-[0.6rem] font-bold text-white">
                  {unreadCount}
                </span>
              )}
            </button>
            <button
              type="button"
              className="rounded-sm p-2 text-muted hover:bg-canvas hover:text-ink lg:hidden transition-colors"
              onClick={onClose}
              aria-label="Close navigation"
            >
              <X size={18} />
            </button>
          </div>

          {showNotifications && (
            <div
              className="fixed left-3 top-16 z-[60] max-h-[24rem] w-[calc(100vw-2rem)] overflow-y-auto rounded-sm border border-line bg-surface lg:left-[18rem] lg:w-[22rem] custom-scrollbar"
              onClick={(event) => event.stopPropagation()}
            >
              <div className="flex items-center justify-between border-b border-line p-3 font-semibold text-ink">
                <span className="text-xs uppercase tracking-wider text-muted">{t("notifications")}</span>
                <button
                  type="button"
                  className="text-xs font-semibold text-farmer-700 hover:text-farmer-900 dark:text-farmer-300 dark:hover:text-farmer-100 transition-colors"
                  onClick={() => {
                    alerts.filter((a: any) => !a.is_read).forEach((a: any) => markRead(a.id));
                    setShowNotifications(false);
                  }}
                >
                  {t("markAllRead")}
                </button>
              </div>
              {alerts.length === 0 ? (
                <div className="p-4 text-center text-sm text-muted">{t("noNewAlerts")}</div>
              ) : (
                alerts.map((alert: any) => (
                  <div
                    key={alert.id}
                    className={`border-b border-line p-3 last:border-0 ${
                      alert.is_read ? "bg-surface" : "bg-farmer-50 dark:bg-farmer-900/30"
                    }`}
                  >
                    <div className="mb-1 text-sm font-semibold text-ink">
                      {translateAlertTitle(alert.title, language)}
                    </div>
                    <div className="mb-2 text-xs leading-5 text-muted">{alert.body}</div>
                    <div className="flex items-center gap-3">
                      {alert.prediction_id && (
                        <Link
                          to={`/predictions/${alert.prediction_id}`}
                          onClick={() => {
                            if (!alert.is_read) markRead(alert.id);
                            setShowNotifications(false);
                            if (onClose) onClose();
                          }}
                          className="text-xs font-semibold text-farmer-700 hover:text-farmer-900 dark:text-farmer-300 dark:hover:text-farmer-200"
                        >
                          {t("viewScan") || "View Scan"}
                        </Link>
                      )}
                      {!alert.is_read && (
                        <button
                          onClick={() => markRead(alert.id)}
                          className="p-0 text-xs font-semibold text-muted hover:text-ink transition-colors"
                        >
                          {t("markAsRead")}
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-5 custom-scrollbar">
          {isExpert ? (
            <>
              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.65rem] font-bold uppercase tracking-wider text-muted">
                  {t("agronomyDesk")}
                </span>
                <NavLink onClick={onClose} to="/admin/expert" className={navLinkClass}>
                  <ClipboardList size={18} />
                  <span>{t("reviewQueue")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/admin/feedback" className={navLinkClass}>
                  <FileText size={18} />
                  <span>{t("feedbackAudits")}</span>
                </NavLink>
              </div>

              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.65rem] font-bold uppercase tracking-wider text-muted">
                  {t("fieldTools")}
                </span>
                <NavLink onClick={onClose} to="/scan" className={navLinkClass}>
                  <Scan size={18} />
                  <span>{t("diagnosticScanner")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/history" className={navLinkClass}>
                  <History size={18} />
                  <span>{t("history")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/weather" className={navLinkClass}>
                  <CloudSun size={18} />
                  <span>{t("weatherAdvisory")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/alerts" className={navLinkClass}>
                  <Bell size={18} />
                  <span>{t("alerts")}</span>
                  {unreadCount > 0 && (
                    <span className="ml-auto rounded-xs bg-danger px-1.5 py-0.5 text-[0.65rem] font-bold text-white">
                      {unreadCount}
                    </span>
                  )}
                </NavLink>
              </div>

              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.65rem] font-bold uppercase tracking-wider text-muted">
                  {t("account")}
                </span>
                <NavLink onClick={onClose} to="/settings" className={navLinkClass}>
                  <Settings size={18} />
                  <span>{t("settings")}</span>
                </NavLink>
              </div>
            </>
          ) : isSuperAdmin ? (
            <>
              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.65rem] font-bold uppercase tracking-wider text-muted">
                  {t("platformControl")}
                </span>
                <NavLink onClick={onClose} to="/admin/metrics" className={navLinkClass}>
                  <ShieldAlert size={18} />
                  <span>{t("metricsMlops")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/admin/users" className={navLinkClass}>
                  <Users size={18} />
                  <span>{t("userRoles")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/admin/expert" className={navLinkClass}>
                  <ClipboardList size={18} />
                  <span>{t("reviewQueue")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/admin/feedback" className={navLinkClass}>
                  <FileText size={18} />
                  <span>{t("feedbackLogs")}</span>
                </NavLink>
              </div>

              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.65rem] font-bold uppercase tracking-wider text-muted">
                  {t("operations")}
                </span>
                <NavLink onClick={onClose} to="/dashboard" className={navLinkClass}>
                  <LayoutDashboard size={18} />
                  <span>{t("dashboard")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/scan" className={navLinkClass}>
                  <Scan size={18} />
                  <span>{t("scan")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/history" className={navLinkClass}>
                  <History size={18} />
                  <span>{t("history")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/farm/settings" className={navLinkClass}>
                  <MapPin size={18} />
                  <span>{t("farmPlots")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/weather" className={navLinkClass}>
                  <CloudSun size={18} />
                  <span>{t("weather")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/alerts" className={navLinkClass}>
                  <Bell size={18} />
                  <span>{t("alerts")}</span>
                  {unreadCount > 0 && (
                    <span className="ml-auto rounded-xs bg-danger px-1.5 py-0.5 text-[0.65rem] font-bold text-white">
                      {unreadCount}
                    </span>
                  )}
                </NavLink>
              </div>

              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.65rem] font-bold uppercase tracking-wider text-muted">
                  {t("account")}
                </span>
                <NavLink onClick={onClose} to="/settings" className={navLinkClass}>
                  <Settings size={18} />
                  <span>{t("settings")}</span>
                </NavLink>
              </div>
            </>
          ) : (
            <>
              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.65rem] font-bold uppercase tracking-wider text-muted">
                  {t("core")}
                </span>
                <NavLink onClick={onClose} to="/dashboard" className={navLinkClass}>
                  <LayoutDashboard size={18} />
                  <span>{t("dashboard")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/scan" className={navLinkClass}>
                  <Scan size={18} />
                  <span>{t("scan")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/history" className={navLinkClass}>
                  <History size={18} />
                  <span>{t("history")}</span>
                </NavLink>
              </div>

              <div className="space-y-1">
                <span className="mb-2 block px-3 text-[0.65rem] font-bold uppercase tracking-wider text-muted">
                  {t("management")}
                </span>
                <NavLink onClick={onClose} to="/farm/settings" className={navLinkClass}>
                  <MapPin size={18} />
                  <span>{t("farm")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/alerts" className={navLinkClass}>
                  <Bell size={18} />
                  <span>{t("alerts")}</span>
                  {unreadCount > 0 && (
                    <span className="ml-auto rounded-xs bg-danger px-1.5 py-0.5 text-[0.65rem] font-bold text-white">
                      {unreadCount}
                    </span>
                  )}
                </NavLink>
                <NavLink onClick={onClose} to="/weather" className={navLinkClass}>
                  <CloudSun size={18} />
                  <span>{t("weatherAdvisory")}</span>
                </NavLink>
                <NavLink onClick={onClose} to="/settings" className={navLinkClass}>
                  <Settings size={18} />
                  <span>{t("settings")}</span>
                </NavLink>
              </div>
            </>
          )}
        </nav>

        <div className="flex items-center justify-between gap-3 border-t border-line bg-canvas p-3.5">
          <div className="flex min-w-0 items-center gap-2.5">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xs bg-farmer-700 text-xs font-bold text-white">
              {user?.name ? user.name.charAt(0).toUpperCase() : "F"}
            </div>
            <div className="min-w-0">
              <span className="block truncate text-xs font-semibold text-ink">
                {user?.name === "Admin User" || user?.name === "Super Administrator" || user?.name === "Administrator"
                  ? t("roleAdmin")
                  : user?.name === "Expert Agronomist" || user?.name === "Expert User" || user?.name === "Expert"
                  ? t("roleExpert")
                  : user?.name === "Farmer User" || user?.name === "Farmer"
                  ? t("roleFarmer")
                  : user?.name || (user?.role === "expert" ? t("roleExpert") : user?.role === "admin" ? t("roleAdmin") : t("roleFarmer"))}
              </span>
              <span className="block truncate text-[0.7rem] text-muted">{user?.email || user?.phone || ""}</span>
            </div>
          </div>
          <button
            onClick={handleSignOut}
            className="rounded-xs p-1.5 text-muted hover:bg-red-50 hover:text-danger transition-colors"
            title={t("logout")}
            aria-label={t("logout")}
          >
            <LogOut size={16} />
          </button>
        </div>
      </aside>
    </>
  );
}