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
            <div className="flex h-12 w-12 items-center justify-center rounded-sm bg-farmer-100 text-farmer-700"><ScanSearch size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Intelligent Disease Diagnosis</h3>
            <p>Fast, objective disease identification before visual symptoms spread. Detects exact leaf damage percentage and flags visible pests instantly.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <div className="flex h-12 w-12 items-center justify-center rounded-sm bg-farmer-100 text-farmer-700"><Map size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Explainable AI (XAI)</h3>
            <p>Eliminate the black-box nature of deep learning. View Grad-CAM attention heatmaps to verify the diagnosis is based on actual foliage lesions.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <div className="flex h-12 w-12 items-center justify-center rounded-sm bg-farmer-100 text-farmer-700"><Activity size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Context-Aware Advisory</h3>
            <p>Practical guidance adapted to current weather conditions. Receive step-by-step action plans spanning treatment, prevention, and monitoring.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <div className="flex h-12 w-12 items-center justify-center rounded-sm bg-farmer-100 text-farmer-700"><ShieldCheck size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Plot-Level Health Tracking</h3>
            <p>Track condition progression over time. Identify chronic hot-spots across specific acreage rather than treating the farm uniformly.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <div className="flex h-12 w-12 items-center justify-center rounded-sm bg-farmer-100 text-farmer-700"><Bell size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Proactive Risk Alerts</h3>
            <p>Continuous monitoring of regional meteorological indicators to warn farmers before fungal or bacterial outbreaks occur.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <div className="flex h-12 w-12 items-center justify-center rounded-sm bg-farmer-100 text-farmer-700"><Users size={24} /></div>
            <h3 className="mt-6 font-display text-xl text-ink">Expert Verification (HITL)</h3>
            <p>Low-confidence predictions are automatically flagged for review by agricultural experts, ensuring safe and reliable chemical advice.</p>
          </motion.div>
        </div>
      </section>

      <section className="bg-farmer-900 px-5 py-16 text-white sm:px-8 lg:py-20">
        <div className="mx-auto max-w-7xl">
        <h2 className="font-display text-3xl">How We Deliver</h2>
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="border-l border-farmer-500 pl-4">
            <h4>[01] Preprocessing Validation</h4>
            <p>OpenCV filters out blurry or non-foliage images to save compute.</p>
          </div>
          <div className="border-l border-farmer-500 pl-4">
            <h4>[02] Multi-Stage Neural Pipeline</h4>
            <p>Crop-specific routing using EfficientNet and YOLO detection.</p>
          </div>
          <div className="border-l border-farmer-500 pl-4">
            <h4>[03] Contextual LLM Advisory</h4>
            <p>Generating region-aware plans tailored to weather.</p>
          </div>
          <div className="border-l border-farmer-500 pl-4">
            <h4>[04] Expert Guardrails</h4>
            <p>Deterministic safety checks prevent speculative recommendations.</p>
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

      <section className="bg-ink px-5 py-16 text-center text-white sm:px-8 lg:py-20">
        <h2 className="font-display text-3xl">Ready to transform your farm?</h2>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link to="/auth/register" className="rounded-sm bg-farmer-300 px-5 py-3 text-sm font-bold text-ink hover:bg-farmer-200">Create Farm Account</Link>
          <Link to="/scan" className="rounded-sm border border-farmer-300 px-5 py-3 text-sm font-bold text-farmer-200 hover:bg-farmer-900">Scan Your First Crop</Link>
        </div>
      </section>
    </div>
  );
}
