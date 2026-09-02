import { Link } from "react-router-dom";
import { ScanSearch, Map, Bell, ShieldCheck, Activity, Users } from "lucide-react";
import { motion } from "motion/react";
import "../styles/ServicesPage.css";
import "../styles/LandingPage.css"; // Reuse navbar

export default function ServicesPage() {
  return (
    <div className="services-page">
      <nav className="landing-navbar">
        <div className="brand">
          <span className="brand-name">Smart Farming</span>
        </div>
        <div className="nav-actions">
          <Link to="/about">About</Link>
          <Link to="/services">Services</Link>
          <Link to="/crops">Technology</Link>
          <Link to="/auth/login" className="btn-primary">Sign In</Link>
        </div>
      </nav>

      <section className="services-hero">
        <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          Comprehensive Crop Intelligence
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          Bridging deep learning vision with actionable agronomy from field to harvest.
        </motion.p>
      </section>

      <section className="services-matrix">
        <div className="services-grid">
          <motion.div className="service-card" whileHover={{ scale: 1.02 }}>
            <div className="service-icon"><ScanSearch size={28} /></div>
            <h3>Intelligent Disease Diagnosis</h3>
            <p>Fast, objective disease identification before visual symptoms spread. Detects exact leaf damage percentage and flags visible pests instantly.</p>
          </motion.div>
          <motion.div className="service-card" whileHover={{ scale: 1.02 }}>
            <div className="service-icon"><Map size={28} /></div>
            <h3>Explainable AI (XAI)</h3>
            <p>Eliminate the black-box nature of deep learning. View Grad-CAM attention heatmaps to verify the diagnosis is based on actual foliage lesions.</p>
          </motion.div>
          <motion.div className="service-card" whileHover={{ scale: 1.02 }}>
            <div className="service-icon"><Activity size={28} /></div>
            <h3>Context-Aware Advisory</h3>
            <p>Practical guidance adapted to current weather conditions. Receive step-by-step action plans spanning treatment, prevention, and monitoring.</p>
          </motion.div>
          <motion.div className="service-card" whileHover={{ scale: 1.02 }}>
            <div className="service-icon"><ShieldCheck size={28} /></div>
            <h3>Plot-Level Health Tracking</h3>
            <p>Track condition progression over time. Identify chronic hot-spots across specific acreage rather than treating the farm uniformly.</p>
          </motion.div>
          <motion.div className="service-card" whileHover={{ scale: 1.02 }}>
            <div className="service-icon"><Bell size={28} /></div>
            <h3>Proactive Risk Alerts</h3>
            <p>Continuous monitoring of regional meteorological indicators to warn farmers before fungal or bacterial outbreaks occur.</p>
          </motion.div>
          <motion.div className="service-card" whileHover={{ scale: 1.02 }}>
            <div className="service-icon"><Users size={28} /></div>
            <h3>Expert Verification (HITL)</h3>
            <p>Low-confidence predictions are automatically flagged for review by agricultural experts, ensuring safe and reliable chemical advice.</p>
          </motion.div>
        </div>
      </section>

      <section className="capability-strip">
        <h2>How We Deliver</h2>
        <div className="strip-grid">
          <div className="strip-item">
            <h4>[01] Preprocessing Validation</h4>
            <p>OpenCV filters out blurry or non-foliage images to save compute.</p>
          </div>
          <div className="strip-item">
            <h4>[02] Multi-Stage Neural Pipeline</h4>
            <p>Crop-specific routing using EfficientNet and YOLO detection.</p>
          </div>
          <div className="strip-item">
            <h4>[03] Contextual LLM Advisory</h4>
            <p>Generating region-aware plans tailored to weather.</p>
          </div>
          <div className="strip-item">
            <h4>[04] Expert Guardrails</h4>
            <p>Deterministic safety checks prevent speculative recommendations.</p>
          </div>
        </div>
      </section>

      <section className="personas-section">
        <h2 style={{ textAlign: "center", marginBottom: "3rem" }}>Who It's For</h2>
        <div className="personas-grid">
          <div className="persona-card">
            <h3>Individual Farmers</h3>
            <p>Easy mobile scans and localized advice to save time and reduce chemical waste.</p>
          </div>
          <div className="persona-card">
            <h3>Extension Officers</h3>
            <p>Batch triage and validation tools to support more farmers efficiently.</p>
          </div>
          <div className="persona-card">
            <h3>Farm Managers & Co-ops</h3>
            <p>Multi-plot analytics and condition history across large acreage.</p>
          </div>
        </div>
      </section>

      <section className="services-cta">
        <h2>Ready to transform your farm?</h2>
        <div className="cta-buttons">
          <Link to="/auth/register" className="btn-dark">Create Farm Account</Link>
          <Link to="/scan" className="btn-outline-dark">Scan Your First Crop</Link>
        </div>
      </section>
    </div>
  );
}
