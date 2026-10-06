import { Link } from "react-router-dom";
import PublicNav from "../components/PublicNav";
import Footer from "../components/Footer";
import { ScanSearch, Map, Activity, ArrowRight } from "../components/icons";
import { useAuth } from "../context/AuthContext";

export default function ServicesPage() {
  const { t } = useAuth();

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <PublicNav />

      {/* Hero */}
      <section className="border-b border-line bg-surface">
        <div className="mx-auto max-w-5xl px-5 py-16 sm:px-8 lg:py-24 text-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("servicesBadge")}</span>
          <h1 className="mt-3 font-display text-display text-ink">
            {t("servicesTitle")}
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-muted">
            {t("servicesSubtitle")}
          </p>
        </div>
      </section>

      {/* Alternating Technical Feature Sections */}
      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-24 w-full space-y-16">
        {/* Capability 1 */}
        <div className="grid gap-8 lg:grid-cols-2 lg:items-center">
          <div className="space-y-4">
            <div className="inline-flex h-10 w-10 items-center justify-center rounded-xs bg-farmer-100 dark:bg-farmer-900/60 text-farmer-800 dark:text-farmer-200">
              <ScanSearch size={22} />
            </div>
            <h2 className="font-display text-2xl sm:text-3xl text-ink">
              {t("service1Title")}
            </h2>
            <p className="text-sm leading-7 text-muted">
              {t("service1Desc")}
            </p>
            <div className="border-t border-line pt-4 text-xs text-muted space-y-1.5">
              <div>{t("service1Output")}</div>
              <div>{t("service1Turnaround")}</div>
            </div>
          </div>

          <div className="rounded-sm border border-line bg-surface p-6 sm:p-8 space-y-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">{t("serviceSpecsBadge")}</h3>
            <div className="space-y-3 text-xs">
              <div className="border-b border-line pb-2.5">
                <span className="font-semibold text-ink">Tomato:</span>
                <span className="text-muted ml-2">Early Blight, Late Blight, Septoria Leaf Spot, Yellow Leaf Curl Virus, Bacterial Spot</span>
              </div>
              <div className="border-b border-line pb-2.5">
                <span className="font-semibold text-ink">Potato:</span>
                <span className="text-muted ml-2">Early Blight, Late Blight, Blackleg, Mosaic Virus</span>
              </div>
              <div className="border-b border-line pb-2.5">
                <span className="font-semibold text-ink">Cotton:</span>
                <span className="text-muted ml-2">Bacterial Blight, Alternaria Leaf Spot, Grey Mildew, Leaf Curl</span>
              </div>
              <div>
                <span className="font-semibold text-ink">Additional Crops:</span>
                <span className="text-muted ml-2">Groundnut, Pepper Bell, Corn, Rice, Wheat</span>
              </div>
            </div>
          </div>
        </div>

        {/* Capability 2 */}
        <div className="grid gap-8 lg:grid-cols-2 lg:items-center border-t border-line pt-16">
          <div className="rounded-sm border border-line bg-surface p-6 sm:p-8 space-y-4 order-2 lg:order-1">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">{t("serviceXaiTitle")}</h3>
            <p className="text-xs leading-6 text-muted">
              {t("serviceXaiDesc")}
            </p>
            <div className="rounded-xs border border-line bg-canvas p-4 text-xs text-ink/90">
              {t("serviceXaiBox")}
            </div>
          </div>

          <div className="space-y-4 order-1 lg:order-2">
            <div className="inline-flex h-10 w-10 items-center justify-center rounded-xs bg-farmer-100 dark:bg-farmer-900/60 text-farmer-800 dark:text-farmer-200">
              <Map size={22} />
            </div>
            <h2 className="font-display text-2xl sm:text-3xl text-ink">
              {t("service2Title")}
            </h2>
            <p className="text-sm leading-7 text-muted">
              {t("service2Desc")}
            </p>
          </div>
        </div>

        {/* Capability 3 */}
        <div className="grid gap-8 lg:grid-cols-2 lg:items-center border-t border-line pt-16">
          <div className="space-y-4">
            <div className="inline-flex h-10 w-10 items-center justify-center rounded-xs bg-farmer-100 dark:bg-farmer-900/60 text-farmer-800 dark:text-farmer-200">
              <Activity size={22} />
            </div>
            <h2 className="font-display text-2xl sm:text-3xl text-ink">
              {t("service3Title")}
            </h2>
            <p className="text-sm leading-7 text-muted">
              {t("service3Desc")}
            </p>
            <div className="border-t border-line pt-4 text-xs text-muted space-y-1.5">
              <div>Telemetry: Open-Meteo hourly temperature, humidity, wind velocity, precipitation index</div>
              <div>Languages: English, Hindi, and Gujarati with transliterated botanical names</div>
            </div>
          </div>

          <div className="rounded-sm border border-line bg-surface p-6 sm:p-8 space-y-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">{t("serviceWeatherRulesTitle")}</h3>
            <div className="space-y-3 text-xs leading-6 text-ink/90">
              <div className="border-b border-line pb-2.5">
                <span className="font-semibold text-ink">Relative Humidity &gt; 85%:</span>
                <span className="text-muted ml-2">{t("serviceWeatherRule1")}</span>
              </div>
              <div className="border-b border-line pb-2.5">
                <span className="font-semibold text-ink">Wind Speed &gt; 15 km/h:</span>
                <span className="text-muted ml-2">{t("serviceWeatherRule2")}</span>
              </div>
              <div>
                <span className="font-semibold text-ink">Ambient Temp &gt; 35°C:</span>
                <span className="text-muted ml-2">{t("serviceWeatherRule3")}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* User Workflows */}
      <section className="border-t border-line bg-surface">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-24">
          <div className="max-w-2xl mb-12">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("serviceDeploymentBadge")}</span>
            <h2 className="mt-2 font-display text-3xl text-ink">{t("serviceDeploymentTitle")}</h2>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-sm border border-line bg-canvas p-6 space-y-3">
              <h3 className="font-display text-xl text-ink">{t("serviceTopology1Title")}</h3>
              <p className="text-xs leading-6 text-muted">
                {t("serviceTopology1Desc")}
              </p>
              <div className="pt-2 text-xs font-semibold text-farmer-800 dark:text-farmer-300">
                Core: Offline sync queue &amp; quantized models
              </div>
            </div>

            <div className="rounded-sm border border-line bg-canvas p-6 space-y-3">
              <h3 className="font-display text-xl text-ink">{t("serviceTopology2Title")}</h3>
              <p className="text-xs leading-6 text-muted">
                {t("serviceTopology2Desc")}
              </p>
              <div className="pt-2 text-xs font-semibold text-farmer-800 dark:text-farmer-300">
                Core: Cooperative cloud cluster &amp; MLOps
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-line bg-canvas px-5 py-12 text-center sm:px-8">
        <h2 className="font-display text-2xl text-ink">{t("landingBottomCtaTitle")}</h2>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link to="/scan" className="rounded-sm bg-farmer-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-farmer-800 transition-colors">
            {t("landingCtaScan")}
          </Link>
          <Link to="/crops" className="rounded-sm border border-line bg-surface px-5 py-2.5 text-sm font-semibold text-ink hover:bg-farmer-50 transition-colors">
            {t("navCrops")}
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
