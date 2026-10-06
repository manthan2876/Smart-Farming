import PublicNav from "../components/PublicNav";
import Footer from "../components/Footer";
import { useAuth } from "../context/AuthContext";

export default function TermsPage() {
  const { t } = useAuth();

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <PublicNav />

      <main className="flex-1 mx-auto max-w-4xl px-5 py-12 sm:px-8 lg:py-16">
        <header className="border-b border-line pb-8">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("termsLegalAgreement")}</span>
          <h1 className="mt-2 font-display text-3xl sm:text-4xl text-ink">{t("termsTitle")}</h1>
          <p className="mt-3 text-sm text-muted">{t("termsLastUpdated")}</p>
        </header>

        <article className="mt-10 space-y-10 text-sm leading-7 text-ink/90">
          <section className="space-y-3">
            <h2 className="font-display text-xl text-ink">{t("termsSection1Title")}</h2>
            <p>{t("termsSection1P1")}</p>
            <p>{t("termsSection1P2")}</p>
          </section>

          <section className="space-y-3">
            <h2 className="font-display text-xl text-ink">{t("termsSection2Title")}</h2>
            <p>{t("termsSection2P1")}</p>
            <p>{t("termsSection2P2")}</p>
            <ul className="list-decimal pl-5 space-y-1.5 text-muted">
              <li>{t("termsSection2Item1")}</li>
              <li>{t("termsSection2Item2")}</li>
              <li>{t("termsSection2Item3")}</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="font-display text-xl text-ink">{t("termsSection3Title")}</h2>
            <p>{t("termsSection3P1")}</p>
          </section>

          <section className="space-y-3">
            <h2 className="font-display text-xl text-ink">{t("termsSection4Title")}</h2>
            <p>{t("termsSection4P1")}</p>
          </section>

          <section className="space-y-3">
            <h2 className="font-display text-xl text-ink">{t("termsSection5Title")}</h2>
            <p>{t("termsSection5P1")}</p>
          </section>

          <section className="space-y-3">
            <h2 className="font-display text-xl text-ink">{t("termsSection6Title")}</h2>
            <p>{t("termsSection6P1")}</p>
          </section>
        </article>
      </main>

      <Footer />
    </div>
  );
}
