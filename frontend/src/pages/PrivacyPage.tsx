import PublicNav from "../components/PublicNav";
import Footer from "../components/Footer";
import { useAuth } from "../context/AuthContext";

export default function PrivacyPage() {
  const { t } = useAuth();

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <PublicNav />

      <main className="flex-1 mx-auto max-w-4xl px-5 py-12 sm:px-8 lg:py-16">
        <header className="border-b border-line pb-8">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("privacyDataPrivacy")}</span>
          <h1 className="mt-2 font-display text-3xl sm:text-4xl text-ink">{t("privacyTitle")}</h1>
          <p className="mt-3 text-sm text-muted">{t("privacyLastUpdated")}</p>
        </header>

        <article className="mt-10 space-y-10 text-sm leading-7 text-ink/90">
          <section className="space-y-3">
            <h2 className="font-display text-xl text-ink">{t("privacySection1Title")}</h2>
            <p>{t("privacySection1P1")}</p>
            <ul className="list-decimal pl-5 space-y-1.5 text-muted">
              <li>{t("privacySection1Item1")}</li>
              <li>{t("privacySection1Item2")}</li>
              <li>{t("privacySection1Item3")}</li>
              <li>{t("privacySection1Item4")}</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="font-display text-xl text-ink">{t("privacySection2Title")}</h2>
            <p>{t("privacySection2P1")}</p>
            <ul className="list-decimal pl-5 space-y-1.5 text-muted">
              <li>{t("privacySection2Item1")}</li>
              <li>{t("privacySection2Item2")}</li>
              <li>{t("privacySection2Item3")}</li>
              <li>{t("privacySection2Item4")}</li>
              <li>{t("privacySection2Item5")}</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="font-display text-xl text-ink">{t("privacySection3Title")}</h2>
            <p>{t("privacySection3P1")}</p>
          </section>

          <section className="space-y-3">
            <h2 className="font-display text-xl text-ink">{t("privacySection4Title")}</h2>
            <p>{t("privacySection4P1")}</p>
          </section>

          <section className="space-y-3">
            <h2 className="font-display text-xl text-ink">{t("privacySection5Title")}</h2>
            <p>{t("privacySection5P1")}</p>
          </section>
        </article>
      </main>

      <Footer />
    </div>
  );
}
