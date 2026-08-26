import { Menu, Search } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { updateProfile } from "../api/auth";
import { useAuth } from "../context/AuthContext";

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
export function Topbar({ active }: { active: Page }) {
  const navigate = useNavigate();
  const { token, language, setLanguage } = useAuth();
  const languageMutation = useMutation({
    mutationFn: (nextLanguage: string) =>
      updateProfile({ language: nextLanguage }, token!),
    onSuccess: (data) => setLanguage(data.language),
  });
  const label =
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
  return (
    <header className="topbar">
      <button
        className="mobile-menu"
        onClick={() => navigate("/dashboard")}
        aria-label="Open dashboard"
      >
        <Menu size={20} />
      </button>
      <div className="crumb">
        Tuesday, 25 August 2026 <span>/</span> <b>{label}</b>
      </div>
      <div className="top-actions">
        <select
          className="header-language"
          aria-label="Advice language"
          value={language}
          disabled={languageMutation.isPending}
          onChange={(event) => languageMutation.mutate(event.target.value)}
        >
          <option>English</option>
          <option>Gujarati</option>
          <option>Hindi</option>
        </select>
        <button
          className="icon-button"
          title="Search history"
          onClick={() => navigate("/history")}
        >
          <Search size={18} />
        </button>
        <span className="online">
          <span className="pulse-dot" /> API ready
        </span>
      </div>
    </header>
  );
}
