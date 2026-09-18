import { Link } from "react-router-dom";
import { User, Cpu, Shield, Globe } from "lucide-react";
import { motion } from "motion/react";
import PublicNav from "../components/PublicNav";

export default function AboutPage() {
  return (
    <div className="min-h-screen overflow-hidden bg-canvas">
      <PublicNav />

      <section className="mx-auto max-w-5xl px-5 py-20 text-center sm:px-8 lg:py-28">
        <motion.h1 className="font-display text-display text-ink" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          Cultivating Precision, Empowering Every Farmer.
        </motion.h1>
        <motion.p className="mx-auto mt-6 max-w-3xl text-lg leading-8 text-muted" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          To democratize agronomic diagnostics by delivering accurate, timely, and context-aware crop health intelligence to smallholder and commercial farmers alike.
        </motion.p>
        <motion.div className="mx-auto mt-8 inline-flex rounded-full bg-farmer-100 px-4 py-2 text-sm font-semibold text-farmer-800" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: 0.4 }}>
          Developed under IT452 Minor Project & Smart India Hackathon (SIH 25099)
        </motion.div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-5 px-5 pb-16 sm:px-8 lg:grid-cols-2 lg:pb-24">
        <div className="rounded-md border border-red-100 bg-red-50 p-7 sm:p-9">
          <h2 className="font-display text-2xl text-ink">The Traditional Reality</h2>
          <ul className="mt-5 space-y-3 text-sm leading-6 text-muted">
            <li>Delayed disease detection leading to irreversible damage</li>
            <li>Inaccessible agronomic expertise constrained by geography</li>
            <li>Subjective and manual damage estimation</li>
            <li>Unrecognized pest pressure during initial stages</li>
          </ul>
        </div>
        <div className="rounded-md border border-farmer-200 bg-farmer-50 p-7 sm:p-9">
          <h2 className="font-display text-2xl text-ink">Our Intervention</h2>
          <ul className="mt-5 space-y-3 text-sm leading-6 text-muted">
            <li>Instant real-time leaf-level diagnosis</li>
            <li>Context-aware advice tailored to local weather patterns</li>
            <li>Quantitative and objective surface severity percentage</li>
            <li>Visual attention maps to explain AI decisions</li>
          </ul>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-24">
        <h2 className="font-display text-3xl text-ink">Our Core Pillars</h2>
        <div className="mt-8 grid gap-5 md:grid-cols-3">
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <h3 className="flex items-center gap-2 font-display text-xl text-ink"><Cpu className="text-farmer-700" /> CV & Neural Architectures</h3>
            <p>Fail-fast preprocessing prevents wasted compute. We use specialized, crop-specific models rather than forcing a single model to learn everything.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <h3 className="flex items-center gap-2 font-display text-xl text-ink"><Shield className="text-farmer-700" /> Responsible AI & Safety</h3>
            <p>Grad-CAM visualizations ensure transparency. Human-in-the-Loop review holds low-confidence outputs, and deterministic guardrails restrict hazardous advice.</p>
          </motion.div>
          <motion.div className="rounded-md border border-line bg-surface p-6 shadow-soft" whileHover={{ y: -4 }}>
            <h3 className="flex items-center gap-2 font-display text-xl text-ink"><Globe className="text-farmer-700" /> Field Ready</h3>
            <p>AI predictions alone don't cure crops. We enrich diagnostics with regional meteorological indicators like temperature and humidity for true field readiness.</p>
          </motion.div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:py-24">
        <h2 className="font-display text-3xl text-ink">Project Leadership</h2>
        <div className="mt-8 grid gap-5 sm:grid-cols-3">
          <div className="rounded-md border border-line bg-surface p-6 text-center shadow-soft">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-farmer-100 text-farmer-700"><User size={32} /></div>
            <h4>Prof. Rajnik Katariya</h4>
            <p>Project Guide</p>
          </div>
          <div className="rounded-md border border-line bg-surface p-6 text-center shadow-soft">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-farmer-100 text-farmer-700"><User size={32} /></div>
            <h4>Kunj Lunagariya</h4>
            <p>Core Contributor</p>
          </div>
          <div className="rounded-md border border-line bg-surface p-6 text-center shadow-soft">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-farmer-100 text-farmer-700"><User size={32} /></div>
            <h4>Manthan Kuvadiya</h4>
            <p>Core Contributor</p>
          </div>
        </div>
      </section>

      <section className="bg-ink px-5 py-16 text-center text-white sm:px-8 lg:py-20">
        <h2 className="font-display text-3xl">Ready to inspect your crop health?</h2>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link to="/services" className="rounded-sm border border-farmer-300 px-5 py-3 text-sm font-bold text-farmer-200 hover:bg-farmer-900">Explore Our Services</Link>
          <Link to="/scan" className="rounded-sm bg-farmer-300 px-5 py-3 text-sm font-bold text-ink hover:bg-farmer-200">Scan Your Crop</Link>
        </div>
      </section>
    </div>
  );
}
