import { Link } from "react-router-dom";
import { Sprout, ArrowRight } from "../components/icons";
import { useQuery } from "@tanstack/react-query";
import { fetchSupportedCrops } from "../api/crops";
import PublicNav from "../components/PublicNav";
import Footer from "../components/Footer";
import { Skeleton } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { translateCrop } from "../i18n/domain";

export default function CropsPage() {
  const { t, language } = useAuth();
  const { data: crops, isLoading, isError } = useQuery({
    queryKey: ["supportedCrops"],
    queryFn: () => fetchSupportedCrops(),
  });

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <PublicNav />

      {/* Header Section */}
      <section className="border-b border-line bg-surface">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-20">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("pathologyRegistry")}</span>
          <h1 className="mt-2 font-display text-display uppercase tracking-tight text-ink">
            {t("supportedCrops")}
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-muted">
            {t("cropsPageDesc")}
          </p>
        </div>
      </section>

      {/* Grid Section */}
      <section className="flex-1 mx-auto max-w-7xl px-5 py-12 sm:px-8 w-full">
        {isLoading && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((idx) => (
              <div key={idx} className="rounded-sm border border-line bg-surface p-6 space-y-4">
                <Skeleton className="h-10 w-10" />
                <Skeleton className="h-6 w-32" />
                <Skeleton className="h-4 w-44" />
              </div>
            ))}
          </div>
        )}

        {isError && (
          <div className="rounded-sm border border-red-300 bg-red-50 p-6 text-sm text-danger dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
            {t("failedRetrieveCrops")}
          </div>
        )}

        {!isLoading && !isError && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {crops?.map((cropName: string) => {
              const localizedName = translateCrop(cropName, language);
              return (
                <div 
                  key={cropName} 
                  className="flex flex-col justify-between rounded-sm border border-line bg-surface p-6 transition-colors hover:border-farmer-700"
                >
                  <div>
                    <div className="flex h-10 w-10 items-center justify-center rounded-xs bg-farmer-100 dark:bg-farmer-900/60 text-farmer-800 dark:text-farmer-200">
                      <Sprout size={20} />
                    </div>
                    <h3 className="mt-4 font-display text-xl uppercase tracking-tight text-ink">{localizedName}</h3>
                    <p className="mt-1 text-xs font-semibold uppercase tracking-wider text-muted">
                      {t("activePathologyPipeline")}
                    </p>
                  </div>
                  <div className="mt-6 border-t border-line/60 pt-3">
                    <Link
                      to="/scan"
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-farmer-700 hover:text-farmer-900 dark:text-farmer-300 dark:hover:text-farmer-200"
                    >
                      <span>{t("inspectCropSpecimen")} ({localizedName})</span>
                      <ArrowRight size={13} />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      <Footer />
    </div>
  );
}
