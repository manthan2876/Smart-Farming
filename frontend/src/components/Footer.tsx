import { Link } from "react-router-dom";
import { getApiUrl } from "../api/client";
import { useAuth } from "../context/AuthContext";
import LanguageToggle from "./LanguageToggle";

export default function Footer() {
  const { t } = useAuth();

  return (
    <footer className="border-t border-line bg-surface text-ink transition-colors">
      <div className="mx-auto max-w-7xl px-5 py-12 sm:px-8 lg:py-16">
        <div className="grid gap-8 lg:grid-cols-4">
          <div className="space-y-4 lg:col-span-2">
            <div className="flex items-center gap-2.5">
              <span className="flex h-8 w-8 items-center justify-center rounded-xs bg-farmer-700 text-xs font-bold text-white">
                SF
              </span>
              <span className="font-display text-lg tracking-tight">Smart Farming Platform</span>
            </div>
            <p className="max-w-md text-sm leading-6 text-muted">
              {t("footerTagline")}
            </p>
            <div className="text-xs text-muted">
              {t("footerAcademic")}
            </div>
            <div className="pt-2">
              <LanguageToggle variant="segmented" />
            </div>
          </div>

          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">{t("footerPlatform")}</h3>
            <ul className="mt-4 space-y-2.5 text-sm">
              <li>
                <Link to="/" className="text-muted hover:text-ink transition-colors">{t("navHome")}</Link>
              </li>
              <li>
                <Link to="/about" className="text-muted hover:text-ink transition-colors">{t("footerArchitecture")}</Link>
              </li>
              <li>
                <Link to="/services" className="text-muted hover:text-ink transition-colors">{t("footerCapabilities")}</Link>
              </li>
              <li>
                <Link to="/crops" className="text-muted hover:text-ink transition-colors">{t("navCrops")}</Link>
              </li>
              <li>
                <a href={`${getApiUrl()}/docs`} target="_blank" rel="noreferrer" className="text-muted hover:text-ink transition-colors">
                  {t("footerApiDocs")}
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">{t("footerLegal")}</h3>
            <ul className="mt-4 space-y-2.5 text-sm">
              <li>
                <Link to="/terms" className="text-muted hover:text-ink transition-colors">{t("footerTerms")}</Link>
              </li>
              <li>
                <Link to="/privacy" className="text-muted hover:text-ink transition-colors">{t("footerPrivacy")}</Link>
              </li>
              <li>
                <Link to="/auth/login" className="text-muted hover:text-ink transition-colors">{t("footerAgronomistSignIn")}</Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-start justify-between gap-4 border-t border-line pt-6 text-xs text-muted sm:flex-row sm:items-center">
          <div>
            (c) {new Date().getFullYear()} {t("footerCopyright")}
          </div>
          <div className="flex items-center gap-4">
            <Link to="/terms" className="hover:text-ink transition-colors">{t("footerTerms")}</Link>
            <Link to="/privacy" className="hover:text-ink transition-colors">{t("footerPrivacy")}</Link>
            <span className="text-muted/60">{t("footerDeterministic")}</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
