import { Link } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";
import LanguageToggle from "./LanguageToggle";
import { useAuth } from "../context/AuthContext";

export default function PublicNav() {
  const { t } = useAuth();

  return (
    <nav className="mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-4 px-5 py-5 sm:px-8 border-b border-line">
      <Link to="/" className="flex items-center gap-2.5 text-ink">
        <span className="flex h-9 w-9 items-center justify-center rounded-xs bg-farmer-700 text-xs font-bold text-white">SF</span>
        <span className="font-display text-lg tracking-tight">Smart Farming</span>
      </Link>
      <div className="flex flex-wrap items-center justify-end gap-x-6 gap-y-2 text-xs font-semibold text-muted">
        <Link className="transition-colors hover:text-ink" to="/">{t("navHome")}</Link>
        <Link className="transition-colors hover:text-ink" to="/about">{t("navAbout")}</Link>
        <Link className="transition-colors hover:text-ink" to="/services">{t("navServices")}</Link>
        <Link className="transition-colors hover:text-ink" to="/crops">{t("navCrops")}</Link>
        <div className="flex items-center gap-2">
          <LanguageToggle />
          <ThemeToggle />
        </div>
        <Link className="rounded-sm bg-farmer-700 px-3.5 py-2 text-white border border-farmer-800 transition-colors hover:bg-farmer-800" to="/auth/login">{t("signIn")}</Link>
      </div>
    </nav>
  );
}
