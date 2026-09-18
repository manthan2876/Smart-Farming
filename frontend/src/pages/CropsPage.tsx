import { motion } from "motion/react";
import { Link } from "react-router-dom";
import { Sprout } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { fetchSupportedCrops } from "../api/crops";
import PublicNav from "../components/PublicNav";

export default function CropsPage() {
  const { data: crops, isLoading, isError } = useQuery({
    queryKey: ["supportedCrops"],
    queryFn: () => fetchSupportedCrops(),
  });

  return (
    <div className="min-h-screen overflow-hidden bg-canvas">
      <PublicNav />

      {/* Header Section */}
      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-24">
        <div className="flex min-h-[20rem] flex-col justify-center rounded-lg bg-farmer-100 p-8 sm:p-12">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="font-display text-display uppercase text-ink"
          >
            Supported Crops
          </motion.h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-muted">
            Our AI diagnostic engines are continuously trained on thousands of plant images. We currently provide production-ready pathology models for the following crops.
          </p>
        </div>
      </section>

      {/* Grid Section */}
      <section className="mx-auto max-w-7xl px-5 pb-20 sm:px-8">
        {isLoading && <p className="rounded-md border border-line bg-surface p-6 text-muted">Loading supported crops...</p>}
        {isError && <p className="rounded-md border border-red-100 bg-red-50 p-6 text-danger">Failed to load crops from server.</p>}

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {crops?.map((cropName: string, i: number) => (
            <motion.div 
              key={cropName} 
              initial={{ opacity: 0, y: 20 }} 
              animate={{ opacity: 1, y: 0 }} 
              transition={{ delay: i * 0.05 }}
              className="group flex flex-col gap-6 rounded-md border border-line bg-surface p-7 shadow-soft transition-transform hover:-translate-y-1 hover:shadow-card"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-full border border-farmer-700 bg-farmer-200 text-farmer-900">
                <Sprout size={32} />
              </div>
              <h3 className="font-display text-2xl uppercase text-ink">{cropName}</h3>
              <p className="m-0 text-xs font-semibold uppercase tracking-[0.12em] text-muted">
                [ACTIVE MODEL PIPELINE]
              </p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
