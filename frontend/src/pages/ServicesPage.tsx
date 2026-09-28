import { ScanSearch, Map, Bell, ShieldCheck, Activity, Users } from "lucide-react";
import { motion } from "motion/react";
import { Link } from "react-router-dom";
import PublicNav from "../components/PublicNav";

export default function ServicesPage() {
  return (
    <div className="min-h-screen overflow-hidden bg-canvas">
      <PublicNav />

      <section className="mx-auto max-w-5xl px-5 py-20 text-center sm:px-8 lg:py-28">
        <motion.h1 className="font-display text-display text-ink" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          Comprehensive Crop Intelligence
        </motion.h1>
        <motion.p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-muted" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          Bridging deep learning vision with actionable agronomy from field to harvest.
        </motion.p>
      </section>

      <section className="mx-auto max-w-7xl px-5 pb-16 sm:px-8 lg:pb-24">
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <div className="flex h-12 w-12 items-center justify-center rounded-sm border border-farmer-200 bg-farmer-100 text-farmer-700 dark:border-farmer-700 dark:bg-farmer-900/80 dark:text-farmer-300"><ScanSearch size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Intelligent Disease Diagnosis</h3>
            <p>Fast, objective disease identification before visual symptoms spread. Detects exact leaf damage percentage and flags visible pests instantly.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <div className="flex h-12 w-12 items-center justify-center rounded-sm border border-farmer-200 bg-farmer-100 text-farmer-700 dark:border-farmer-700 dark:bg-farmer-900/80 dark:text-farmer-300"><Map size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Explainable AI (XAI)</h3>
            <p>Eliminate the black-box nature of deep learning. View Grad-CAM attention heatmaps to verify the diagnosis is based on actual foliage lesions.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <div className="flex h-12 w-12 items-center justify-center rounded-sm border border-farmer-200 bg-farmer-100 text-farmer-700 dark:border-farmer-700 dark:bg-farmer-900/80 dark:text-farmer-300"><Activity size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Context-Aware Advisory</h3>
            <p>Practical guidance adapted to current weather conditions. Receive step-by-step action plans spanning treatment, prevention, and monitoring.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <div className="flex h-12 w-12 items-center justify-center rounded-sm border border-farmer-200 bg-farmer-100 text-farmer-700 dark:border-farmer-700 dark:bg-farmer-900/80 dark:text-farmer-300"><ShieldCheck size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Plot-Level Health Tracking</h3>
            <p>Track condition progression over time. Identify chronic hot-spots across specific acreage rather than treating the farm uniformly.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <div className="flex h-12 w-12 items-center justify-center rounded-sm border border-farmer-200 bg-farmer-100 text-farmer-700 dark:border-farmer-700 dark:bg-farmer-900/80 dark:text-farmer-300"><Bell size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Proactive Risk Alerts</h3>
            <p>Continuous monitoring of regional meteorological indicators to warn farmers before fungal or bacterial outbreaks occur.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <div className="flex h-12 w-12 items-center justify-center rounded-sm border border-farmer-200 bg-farmer-100 text-farmer-700 dark:border-farmer-700 dark:bg-farmer-900/80 dark:text-farmer-300"><Users size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Expert Verification (HITL)</h3>
            <p>Low-confidence predictions are automatically flagged for review by agricultural experts, ensuring safe and reliable chemical advice.</p>
          </motion.div>
        </div>
      </section>

      <section className="border-y border-farmer-800 bg-farmer-900 px-5 py-16 text-farmer-100 sm:px-8 lg:py-20">
        <div className="mx-auto max-w-7xl">
        <h2 className="font-display text-3xl text-farmer-200">How We Deliver</h2>
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="border-l-2 border-farmer-400 pl-4">
            <h4 className="font-semibold text-farmer-200">[01] Preprocessing Validation</h4>
            <p className="mt-2 text-sm text-farmer-100/90">OpenCV filters out blurry or non-foliage images to save compute.</p>
          </div>
          <div className="border-l-2 border-farmer-400 pl-4">
            <h4 className="font-semibold text-farmer-200">[02] Multi-Stage Neural Pipeline</h4>
            <p className="mt-2 text-sm text-farmer-100/90">Crop-specific routing using EfficientNet and YOLO detection.</p>
          </div>
          <div className="border-l-2 border-farmer-400 pl-4">
            <h4 className="font-semibold text-farmer-200">[03] Contextual LLM Advisory</h4>
            <p className="mt-2 text-sm text-farmer-100/90">Generating region-aware plans tailored to weather.</p>
          </div>
          <div className="border-l-2 border-farmer-400 pl-4">
            <h4 className="font-semibold text-farmer-200">[04] Expert Guardrails</h4>
            <p className="mt-2 text-sm text-farmer-100/90">Deterministic safety checks prevent speculative recommendations.</p>
          </div>
        </div></div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-24">
        <h2 className="text-center font-display text-3xl text-ink">Who It's For</h2>
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          <div className="rounded-md border border-line bg-surface p-6 shadow-soft">
            <h3>Individual Farmers</h3>
            <p>Easy mobile scans and localized advice to save time and reduce chemical waste.</p>
          </div>
          <div className="rounded-md border border-line bg-surface p-6 shadow-soft">
            <h3>Extension Officers</h3>
            <p>Batch triage and validation tools to support more farmers efficiently.</p>
          </div>
          <div className="rounded-md border border-line bg-surface p-6 shadow-soft">
            <h3>Farm Managers & Co-ops</h3>
            <p>Multi-plot analytics and condition history across large acreage.</p>
          </div>
        </div>
      </section>

      <section className="border-t border-farmer-800 bg-farmer-900 px-5 py-16 text-center text-farmer-100 sm:px-8 lg:py-20">
        <h2 className="font-display text-3xl text-farmer-200">Ready to transform your farm?</h2>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link to="/auth/register" className="rounded-sm bg-farmer-400 px-5 py-3 text-sm font-bold text-farmer-950 hover:bg-farmer-300 shadow-soft transition-colors">Create Farm Account</Link>
          <Link to="/scan" className="rounded-sm border border-farmer-400 px-5 py-3 text-sm font-bold text-farmer-200 hover:bg-farmer-800 transition-colors">Scan Your First Crop</Link>
        </div>
      </section>
    </div>
  );
}
