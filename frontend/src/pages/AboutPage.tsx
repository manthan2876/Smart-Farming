import { Link } from "react-router-dom";
import PublicNav from "../components/PublicNav";
import Footer from "../components/Footer";
import { User, Cpu, Shield, Globe } from "../components/icons";
import { useAuth } from "../context/AuthContext";

export default function AboutPage() {
  const { t } = useAuth();

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <PublicNav />

      {/* Header */}
      <section className="border-b border-line bg-surface">
        <div className="mx-auto max-w-5xl px-5 py-16 sm:px-8 lg:py-24 text-center">
          <div className="inline-flex rounded-xs border border-line bg-canvas px-3 py-1 text-xs font-semibold text-muted">
            {t("academicProjectBadge")}
          </div>
          <h1 className="mt-4 font-display text-display text-ink">
            {t("aboutTitle")}
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-muted">
            {t("aboutSubtitle")}
          </p>
        </div>
      </section>

      {/* Traditional Reality vs System Intervention (Structured Table Comparison) */}
      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-24 w-full">
        <div className="mb-8">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("aboutFieldContext")}</span>
          <h2 className="mt-1 font-display text-2xl sm:text-3xl text-ink">{t("aboutTableTitle")}</h2>
        </div>

        <div className="overflow-x-auto rounded-sm border border-line bg-surface">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-line bg-canvas text-xs uppercase tracking-wider text-muted">
                <th className="px-6 py-4 font-semibold">{t("aboutColAspect")}</th>
                <th className="px-6 py-4 font-semibold">{t("aboutColConventional")}</th>
                <th className="px-6 py-4 font-semibold text-farmer-800 dark:text-farmer-300">{t("aboutColIntervention")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line text-ink/90">
              <tr>
                <td className="px-6 py-4 font-semibold text-ink">{t("aboutRow1Aspect")}</td>
                <td className="px-6 py-4 text-muted">{t("aboutRow1Conv")}</td>
                <td className="px-6 py-4">{t("aboutRow1Interv")}</td>
              </tr>
              <tr>
                <td className="px-6 py-4 font-semibold text-ink">{t("aboutRow2Aspect")}</td>
                <td className="px-6 py-4 text-muted">{t("aboutRow2Conv")}</td>
                <td className="px-6 py-4">{t("aboutRow2Interv")}</td>
              </tr>
              <tr>
                <td className="px-6 py-4 font-semibold text-ink">{t("aboutRow3Aspect")}</td>
                <td className="px-6 py-4 text-muted">{t("aboutRow3Conv")}</td>
                <td className="px-6 py-4">{t("aboutRow3Interv")}</td>
              </tr>
              <tr>
                <td className="px-6 py-4 font-semibold text-ink">{t("aboutRow4Aspect")}</td>
                <td className="px-6 py-4 text-muted">{t("aboutRow4Conv")}</td>
                <td className="px-6 py-4">{t("aboutRow4Interv")}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Core Architectural Pillars */}
      <section className="border-t border-line bg-surface">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-24">
          <div className="grid gap-12 lg:grid-cols-[0.4fr_0.6fr]">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("aboutPillarsBadge")}</span>
              <h2 className="mt-2 font-display text-3xl text-ink">{t("aboutPillarsTitle")}</h2>
              <p className="mt-3 text-sm leading-6 text-muted">
                {t("aboutPillarsSubtitle")}
              </p>
            </div>

            <div className="space-y-6">
              <div className="rounded-sm border border-line bg-canvas p-6">
                <div className="flex items-center gap-2.5 font-display text-lg text-ink">
                  <Cpu size={20} className="text-farmer-700 dark:text-farmer-300" />
                  <h3>{t("aboutPrinciple1Title")}</h3>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted">
                  {t("aboutPrinciple1Desc")}
                </p>
              </div>

              <div className="rounded-sm border border-line bg-canvas p-6">
                <div className="flex items-center gap-2.5 font-display text-lg text-ink">
                  <Shield size={20} className="text-farmer-700 dark:text-farmer-300" />
                  <h3>{t("aboutPrinciple2Title")}</h3>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted">
                  {t("aboutPrinciple2Desc")}
                </p>
              </div>

              <div className="rounded-sm border border-line bg-canvas p-6">
                <div className="flex items-center gap-2.5 font-display text-lg text-ink">
                  <Globe size={20} className="text-farmer-700 dark:text-farmer-300" />
                  <h3>{t("aboutPrinciple3Title")}</h3>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted">
                  {t("aboutPrinciple3Desc")}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Academic Attribution */}
      <section className="border-t border-line bg-canvas">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-20">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted">Academic Credentials</span>
            <h2 className="mt-2 font-display text-3xl text-ink">Project Guidance &amp; Contributors</h2>
            <p className="mt-2 text-sm text-muted">{t("aboutAttributionDesc")}</p>
          </div>

          <div className="grid gap-6 sm:grid-cols-3">
            <div className="rounded-sm border border-line bg-surface p-6 text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xs bg-farmer-100 dark:bg-farmer-900/60 text-farmer-800 dark:text-farmer-200">
                <User size={24} />
              </div>
              <h3 className="mt-4 font-display text-lg text-ink">Prof. Rajnik Katariya</h3>
              <p className="text-xs font-semibold text-muted uppercase tracking-wider mt-0.5">Project Guide &amp; Faculty</p>
              <p className="mt-2 text-xs text-muted">Department of Information Technology, BVM</p>
            </div>

            <div className="rounded-sm border border-line bg-surface p-6 text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xs bg-farmer-100 dark:bg-farmer-900/60 text-farmer-800 dark:text-farmer-200">
                <User size={24} />
              </div>
              <h3 className="mt-4 font-display text-lg text-ink">Kunj Lunagariya</h3>
              <p className="text-xs font-semibold text-muted uppercase tracking-wider mt-0.5">Core Contributor</p>
              <p className="mt-2 text-xs text-muted">Computer Vision &amp; Backend Engineering</p>
            </div>

            <div className="rounded-sm border border-line bg-surface p-6 text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xs bg-farmer-100 dark:bg-farmer-900/60 text-farmer-800 dark:text-farmer-200">
                <User size={24} />
              </div>
              <h3 className="mt-4 font-display text-lg text-ink">Manthan Kuvadiya</h3>
              <p className="text-xs font-semibold text-muted uppercase tracking-wider mt-0.5">Core Contributor</p>
              <p className="mt-2 text-xs text-muted">Full-Stack Development &amp; MLOps</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-line bg-surface px-5 py-12 text-center sm:px-8">
        <h2 className="font-display text-2xl text-ink">{t("landingBottomCtaTitle")}</h2>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link to="/scan" className="rounded-sm bg-farmer-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-farmer-800 transition-colors">
            {t("landingBottomCtaBtn")}
          </Link>
          <Link to="/crops" className="rounded-sm border border-line bg-canvas px-5 py-2.5 text-sm font-semibold text-ink hover:bg-farmer-50 transition-colors">
            {t("navCrops")}
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
