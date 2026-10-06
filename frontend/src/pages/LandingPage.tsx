import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import PublicNav from "../components/PublicNav";
import Footer from "../components/Footer";
import { Sprout, ScanSearch, ShieldCheck, Activity, Map, ArrowRight } from "../components/icons";
import { useAuth } from "../context/AuthContext";
import { translateCrop, translateDisease } from "../i18n/domain";

interface DemoSample {
  id: string;
  crop: string;
  condition: string;
  pathogen: string;
  severity: string;
  confidence: number;
  coverage: string;
  leafArea: string;
  saliencyTarget: string;
  recommendedTreatment: string;
  activeChemical: string;
  dosage: string;
  advisoryVernacular: {
    en: string;
    hi: string;
    gu: string;
  };
}

const DEMO_SAMPLES: DemoSample[] = [
  {
    id: "tomato-early-blight",
    crop: "Tomato",
    condition: "Early Blight",
    pathogen: "Alternaria solani",
    severity: "Moderate (28% Foliar Damage)",
    confidence: 96.4,
    coverage: "82% foliage present in frame",
    leafArea: "142 cm² segmented leaf area",
    saliencyTarget: "Concentric target-like lesion rings with yellow chlorotic halos on lower mature leaflets.",
    recommendedTreatment: "Apply copper oxychloride or mancozeb as protective spray. Prune infected bottom leaves touching moist soil.",
    activeChemical: "Mancozeb 75% WP or Copper Oxychloride 50% WP",
    dosage: "2.5 g / litre water (500 g / acre in 200 L water)",
    advisoryVernacular: {
      en: "Spray during early morning or late afternoon when ambient temperature is below 30°C and wind speed is under 10 km/h.",
      hi: "सुबह या देर शाम को छिड़काव करें जब तापमान 30 डिग्री सेल्सियस से कम हो और हवा की गति शांत हो।",
      gu: "સવારે અથવા સાંજના સમયે છંટકાવ કરવો જ્યારે તાપમાન 30°C થી ઓછું હોય અને પવનની ગતિ ધીમી હોય.",
    },
  },
  {
    id: "potato-late-blight",
    crop: "Potato",
    condition: "Late Blight",
    pathogen: "Phytophthora infestans",
    severity: "Severe (54% Foliar Damage)",
    confidence: 98.1,
    coverage: "91% foliage present in frame",
    leafArea: "168 cm² segmented leaf area",
    saliencyTarget: "Irregular water-soaked brown-black necrosis starting from leaflet margins with white mildew borders.",
    recommendedTreatment: "Immediate systemic intervention required. Alternate cymoxanil with dimethomorph to break resistance cycles.",
    activeChemical: "Cymoxanil 8% + Mancozeb 64% WP",
    dosage: "3.0 g / litre water (600 g / acre in 200 L water)",
    advisoryVernacular: {
      en: "High humidity alert: Relative humidity > 85% for 48 hours accelerates sporulation. Halt furrow irrigation temporarily.",
      hi: "उच्च आर्द्रता चेतावनी: 85% से अधिक नमी बीजाणु फैलाव को बढ़ाती है। सिंचाई अस्थायी रूप से रोकें।",
      gu: "વધુ ભેજ ચેતવણી: 85% થી વધુ ભેજ રોગનો ફેલાવો ઝડપી બનાવે છે. પિયત આપવાનું થોડા દિવસ મોકૂફ રાખો.",
    },
  },
  {
    id: "cotton-bacterial-blight",
    crop: "Cotton",
    condition: "Bacterial Blight",
    pathogen: "Xanthomonas axonopodis pv. malvacearum",
    severity: "Low (12% Foliar Damage)",
    confidence: 94.7,
    coverage: "78% foliage present in frame",
    leafArea: "115 cm² segmented leaf area",
    saliencyTarget: "Angular dark brown water-soaked lesions constrained by leaf veinlets with oily leaf translucency.",
    recommendedTreatment: "Spray copper oxychloride combined with streptocycline. Ensure tractor spray boom maintains uniform canopy coverage.",
    activeChemical: "Copper Oxychloride 50% WP + Streptocycline (100 ppm)",
    dosage: "2.0 g Copper Oxychloride + 1 g Streptocycline per 10 L water",
    advisoryVernacular: {
      en: "Inspect neighboring plants across 2-meter radius for systemic vein-clearing symptoms within 7 days.",
      hi: "7 दिनों के भीतर 2 मीटर के दायरे में पड़ोसी पौधों की नसों की जांच करें।",
      gu: "7 દિવસમાં 2 મીટર ત્રિજ્યામાં આવેલા આજુબાજુના છોડની નસોમાં રોગના ચિહ્નો તપાસો.",
    },
  },
];

export default function LandingPage() {
  const { t, language } = useAuth();
  const [activeSampleId, setActiveSampleId] = useState(DEMO_SAMPLES[0].id);
  const [activeTab, setActiveTab] = useState<"analysis" | "saliency" | "advisory">("analysis");

  const effectiveLangCode: "en" | "hi" | "gu" = 
    language === "Gujarati" ? "gu" : language === "Hindi" ? "hi" : "en";
  const [demoLang, setDemoLang] = useState<"en" | "hi" | "gu">(effectiveLangCode);

  useEffect(() => {
    setDemoLang(effectiveLangCode);
  }, [effectiveLangCode]);

  const activeSample = DEMO_SAMPLES.find((s) => s.id === activeSampleId) || DEMO_SAMPLES[0];

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <PublicNav />

      {/* Hero Section */}
      <section className="border-b border-line bg-surface">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-24">
          <div className="grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 rounded-xs border border-line bg-canvas px-3 py-1 text-xs font-semibold text-muted">
                <span>{t("academicProjectBadge")}</span>
              </div>

              <h1 className="font-display text-display tracking-tight text-ink">
                {t("landingHeroTitle")}
              </h1>

              <p className="max-w-xl text-base leading-7 text-muted">
                {t("landingHeroSubtitle")}
              </p>

              <div className="flex flex-wrap gap-3 pt-2">
                <Link
                  to="/scan"
                  className="rounded-sm bg-farmer-700 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-farmer-800"
                >
                  {t("landingCtaScan")}
                </Link>
                <Link
                  to="/crops"
                  className="rounded-sm border border-line bg-surface px-5 py-3 text-sm font-semibold text-ink transition-colors hover:bg-farmer-50"
                >
                  {t("landingCtaCrops")}
                </Link>
              </div>

              <div className="grid grid-cols-3 gap-4 border-t border-line pt-6 text-xs text-muted">
                <div>
                  <div className="font-display text-lg font-semibold text-ink">{t("landingStatCrops")}</div>
                  <div className="mt-0.5">{t("landingStatCropsDesc")}</div>
                </div>
                <div>
                  <div className="font-display text-lg font-semibold text-ink">{t("landingStatGradCam")}</div>
                  <div className="mt-0.5">{t("landingStatGradCamDesc")}</div>
                </div>
                <div>
                  <div className="font-display text-lg font-semibold text-ink">{t("landingStatLanguages")}</div>
                  <div className="mt-0.5">{t("landingStatLanguagesDesc")}</div>
                </div>
              </div>
            </div>

            {/* Architecture Summary Box */}
            <div className="rounded-sm border border-line bg-canvas p-6 sm:p-8 space-y-5">
              <div className="text-xs font-semibold uppercase tracking-wider text-muted">
                {t("landingPipelineTitle")}
              </div>

              <div className="space-y-3 text-xs leading-6 text-ink/90">
                <div className="rounded-xs border border-line bg-surface p-3.5">
                  <div className="font-semibold text-ink">{t("landingStage1Title")}</div>
                  <div className="text-muted mt-1">{t("landingStage1Desc")}</div>
                </div>

                <div className="rounded-xs border border-line bg-surface p-3.5">
                  <div className="font-semibold text-ink">{t("landingStage2Title")}</div>
                  <div className="text-muted mt-1">{t("landingStage2Desc")}</div>
                </div>

                <div className="rounded-xs border border-line bg-surface p-3.5">
                  <div className="font-semibold text-ink">{t("landingStage3Title")}</div>
                  <div className="text-muted mt-1">{t("landingStage3Desc")}</div>
                </div>

                <div className="rounded-xs border border-line bg-surface p-3.5">
                  <div className="font-semibold text-ink">{t("landingStage4Title")}</div>
                  <div className="text-muted mt-1">{t("landingStage4Desc")}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Product Demo (SUBSTANCE ADDITION) */}
      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-24 w-full">
        <div className="mb-10">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("landingDemoBadge")}</span>
          <h2 className="mt-2 font-display text-3xl text-ink">{t("landingDemoTitle")}</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
            {t("landingDemoSubtitle")}
          </p>
        </div>

        {/* Specimen Selector */}
        <div className="grid gap-3 sm:grid-cols-3">
          {DEMO_SAMPLES.map((sample) => {
            const isSelected = sample.id === activeSampleId;
            const localizedCrop = translateCrop(sample.crop, language);
            const localizedDisease = translateDisease(sample.condition, language);
            return (
              <button
                key={sample.id}
                type="button"
                onClick={() => setActiveSampleId(sample.id)}
                className={`text-left rounded-sm border p-4 transition-colors ${
                  isSelected
                    ? "border-farmer-700 bg-farmer-50 dark:bg-farmer-950/60 dark:border-farmer-500"
                    : "border-line bg-surface hover:bg-canvas"
                }`}
              >
                <div className="flex items-center justify-between text-xs font-semibold text-muted">
                  <span>{localizedCrop}</span>
                  <span className="font-mono text-[0.7rem] text-farmer-800 dark:text-farmer-300">
                    {sample.confidence}% {t("confidence")}
                  </span>
                </div>
                <div className="mt-2 font-display text-base font-semibold text-ink">
                  {localizedDisease}
                </div>
                <div className="mt-1 text-xs italic text-muted">
                  {sample.pathogen}
                </div>
              </button>
            );
          })}
        </div>

        {/* Interactive Specimen Inspection Workbench */}
        <div className="mt-8 rounded-sm border border-line bg-surface p-6 sm:p-8">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-line pb-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted">Specimen:</span>
              <span className="font-display text-lg text-ink">
                {translateCrop(activeSample.crop, language)} : {translateDisease(activeSample.condition, language)}
              </span>
              <span className="rounded-xs border border-line bg-canvas px-2 py-0.5 text-xs font-mono text-muted">
                {activeSample.pathogen}
              </span>
            </div>

            {/* Workbench View Tabs */}
            <div className="inline-flex rounded-xs border border-line bg-canvas p-1 text-xs font-semibold">
              <button
                type="button"
                onClick={() => setActiveTab("analysis")}
                className={`rounded-xs px-3 py-1.5 transition-colors ${
                  activeTab === "analysis"
                    ? "bg-surface text-ink border border-line font-bold"
                    : "text-muted hover:text-ink"
                }`}
              >
                {t("landingTabMask")}
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("saliency")}
                className={`rounded-xs px-3 py-1.5 transition-colors ${
                  activeTab === "saliency"
                    ? "bg-surface text-ink border border-line font-bold"
                    : "text-muted hover:text-ink"
                }`}
              >
                {t("landingTabSaliency")}
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("advisory")}
                className={`rounded-xs px-3 py-1.5 transition-colors ${
                  activeTab === "advisory"
                    ? "bg-surface text-ink border border-line font-bold"
                    : "text-muted hover:text-ink"
                }`}
              >
                {t("landingTabAdvisory")}
              </button>
            </div>
          </div>

          <div className="mt-6">
            {activeTab === "analysis" && (
              <div className="space-y-4">
                <div>
                  <span className="text-xs uppercase tracking-wider text-muted">{t("spatialTelemetry")}</span>
                  <h3 className="font-display text-2xl text-ink mt-1">OpenCV Vegetation Segmentation</h3>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-xs border border-line bg-canvas p-4 space-y-1 text-xs">
                    <span className="font-semibold text-muted">{t("coverageMetric")}</span>
                    <p className="font-mono text-ink text-sm">{activeSample.coverage}</p>
                  </div>
                  <div className="rounded-xs border border-line bg-canvas p-4 space-y-1 text-xs">
                    <span className="font-semibold text-muted">{t("segmentedLeafArea")}</span>
                    <p className="font-mono text-ink text-sm">{activeSample.leafArea}</p>
                  </div>
                </div>
                <div className="rounded-xs border border-line bg-surface p-3 text-xs text-muted">
                  {t("preprocStatus")}: {t("preprocPassed")}
                </div>
              </div>
            )}

            {activeTab === "saliency" && (
              <div className="space-y-4">
                <div>
                  <span className="text-xs uppercase tracking-wider text-muted">{t("attentionFocus")}</span>
                  <h3 className="font-display text-2xl text-ink mt-1">{t("transparentSaliency")}</h3>
                </div>
                <p className="text-sm leading-6 text-muted">
                  {t("saliencyDesc")}
                </p>
                <div className="rounded-sm border border-line bg-canvas p-5">
                  <div className="text-xs font-semibold uppercase tracking-wider text-muted">{t("attentionFocus")}</div>
                  <p className="mt-2 text-sm leading-6 text-ink">
                    {activeSample.saliencyTarget}
                  </p>
                </div>
              </div>
            )}

            {activeTab === "advisory" && (
              <div className="space-y-5">
                <div>
                  <span className="text-xs uppercase tracking-wider text-muted">{t("agronomicAction")}</span>
                  <h3 className="font-display text-2xl text-ink mt-1">{t("treatmentGuidance")}</h3>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-xs border border-line bg-canvas p-4 space-y-2 text-xs">
                    <span className="font-semibold uppercase tracking-wider text-muted">{t("activeIngredient")}</span>
                    <p className="font-semibold text-ink text-sm">{activeSample.activeChemical}</p>
                    <p className="text-muted">{t("dosage")}: {activeSample.dosage}</p>
                  </div>
                  <div className="rounded-xs border border-line bg-canvas p-4 space-y-2 text-xs">
                    <span className="font-semibold uppercase tracking-wider text-muted">{t("culturalSanitation")}</span>
                    <p className="text-ink leading-5">{activeSample.recommendedTreatment}</p>
                  </div>
                </div>

                <div className="rounded-xs border border-farmer-300 bg-farmer-50 dark:bg-farmer-900/30 dark:border-farmer-700 p-4">
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-semibold uppercase tracking-wider text-farmer-800 dark:text-farmer-200">
                      {t("localizedSprayAdvisory")} ({demoLang.toUpperCase()})
                    </div>
                    <div className="flex gap-1 text-[0.65rem] font-bold">
                      {(["en", "hi", "gu"] as const).map((l) => (
                        <button
                          key={l}
                          type="button"
                          onClick={() => setDemoLang(l)}
                          className={`rounded px-1.5 py-0.5 border ${
                            demoLang === l
                              ? "bg-farmer-700 text-white border-farmer-700"
                              : "bg-surface text-muted border-line hover:text-ink"
                          }`}
                        >
                          {l.toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-ink">
                    {activeSample.advisoryVernacular[demoLang]}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Field Methodology Section (Asymmetric layout, no identical 3-card grid) */}
      <section className="border-t border-line bg-surface">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-24">
          <div className="grid gap-12 lg:grid-cols-3">
            <div className="space-y-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("landingMethodologyBadge")}</span>
              <h2 className="font-display text-3xl text-ink">{t("landingMethodologyTitle")}</h2>
              <p className="text-sm leading-6 text-muted">
                {t("landingMethodologySubtitle")}
              </p>
            </div>

            <div className="lg:col-span-2 space-y-6">
              <div className="border-b border-line pb-6">
                <div className="text-xs font-semibold uppercase tracking-wider text-muted">01: Preprocessing Rejection</div>
                <h3 className="font-display text-xl text-ink mt-1">{t("landingMethod1Title")}</h3>
                <p className="mt-2 text-sm leading-6 text-muted">
                  {t("landingMethod1Desc")}
                </p>
              </div>

              <div className="border-b border-line pb-6">
                <div className="text-xs font-semibold uppercase tracking-wider text-muted">02: Multi-Model Routing</div>
                <h3 className="font-display text-xl text-ink mt-1">{t("landingMethod2Title")}</h3>
                <p className="mt-2 text-sm leading-6 text-muted">
                  {t("landingMethod2Desc")}
                </p>
              </div>

              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-muted">03: Human-in-the-Loop Safety</div>
                <h3 className="font-display text-xl text-ink mt-1">{t("landingMethod3Title")}</h3>
                <p className="mt-2 text-sm leading-6 text-muted">
                  {t("landingMethod3Desc")}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Supported Crops Quick Links */}
      <section className="border-t border-line bg-canvas">
        <div className="mx-auto max-w-7xl px-5 py-12 sm:px-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h3 className="font-display text-xl text-ink">{t("landingBottomCtaTitle")}</h3>
            <p className="text-xs text-muted mt-1">{t("landingBottomCtaDesc")}</p>
          </div>
          <Link
            to="/crops"
            className="inline-flex items-center gap-2 rounded-sm border border-line bg-surface px-4 py-2.5 text-xs font-semibold text-ink hover:bg-farmer-50 transition-colors"
          >
            <span>{t("landingCtaCrops")}</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
