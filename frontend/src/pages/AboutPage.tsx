import { Link } from "react-router-dom";
import { User, Cpu, Shield, Globe } from "lucide-react";
import { motion } from "motion/react";
import "../styles/AboutPage.css";
import "../styles/LandingPage.css"; // Reuse navbar

export default function AboutPage() {
  return (
    <div className="about-page">
      {/* Top Navbar */}
      <nav className="landing-navbar">
        <div className="brand">
          <span className="brand-name">Smart Farming</span>
        </div>
        <div className="nav-actions">
          <Link to="/">Home</Link>
          <Link to="/about">About</Link>
          <Link to="/services">Services</Link>
          <Link to="/crops">Supported Crops</Link>
          <Link to="/auth/login" className="btn-primary">Sign In</Link>
        </div>
      </nav>

      <section className="about-hero">
        <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          Cultivating Precision, Empowering Every Farmer.
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          To democratize agronomic diagnostics by delivering accurate, timely, and context-aware crop health intelligence to smallholder and commercial farmers alike.
        </motion.p>
        <motion.div className="origin-banner" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: 0.4 }}>
          Developed under IT452 Minor Project & Smart India Hackathon (SIH 25099)
        </motion.div>
      </section>

      <section className="problem-solution-section">
        <div className="problem-box">
          <h2>The Traditional Reality</h2>
          <ul>
            <li>Delayed disease detection leading to irreversible damage</li>
            <li>Inaccessible agronomic expertise constrained by geography</li>
            <li>Subjective and manual damage estimation</li>
            <li>Unrecognized pest pressure during initial stages</li>
          </ul>
        </div>
        <div className="solution-box">
          <h2>Our Intervention</h2>
          <ul>
            <li>Instant real-time leaf-level diagnosis</li>
            <li>Context-aware advice tailored to local weather patterns</li>
            <li>Quantitative and objective surface severity percentage</li>
            <li>Visual attention maps to explain AI decisions</li>
          </ul>
        </div>
      </section>

      <section className="pillars-section">
        <h2>Our Core Pillars</h2>
        <div className="pillars-grid">
          <motion.div className="pillar-card" whileHover={{ scale: 1.05 }}>
            <h3><Cpu /> CV & Neural Architectures</h3>
            <p>Fail-fast preprocessing prevents wasted compute. We use specialized, crop-specific models rather than forcing a single model to learn everything.</p>
          </motion.div>
          <motion.div className="pillar-card" whileHover={{ scale: 1.05 }}>
            <h3><Shield /> Responsible AI & Safety</h3>
            <p>Grad-CAM visualizations ensure transparency. Human-in-the-Loop review holds low-confidence outputs, and deterministic guardrails restrict hazardous advice.</p>
          </motion.div>
          <motion.div className="pillar-card" whileHover={{ scale: 1.05 }}>
            <h3><Globe /> Field Ready</h3>
            <p>AI predictions alone don't cure crops. We enrich diagnostics with regional meteorological indicators like temperature and humidity for true field readiness.</p>
          </motion.div>
        </div>
      </section>

      <section className="leadership-section">
        <h2>Project Leadership</h2>
        <div className="team-grid">
          <div className="team-member">
            <div className="team-avatar"><User size={48} /></div>
            <h4>Prof. Rajnik Katariya</h4>
            <p>Project Guide</p>
          </div>
          <div className="team-member">
            <div className="team-avatar"><User size={48} /></div>
            <h4>Kunj Lunagariya</h4>
            <p>Core Contributor</p>
          </div>
          <div className="team-member">
            <div className="team-avatar"><User size={48} /></div>
            <h4>Manthan Kuvadiya</h4>
            <p>Core Contributor</p>
          </div>
        </div>
      </section>

      <section className="services-cta" style={{ background: "#0F3D2E", color: "#fff", padding: "5rem", textAlign: "center" }}>
        <h2 style={{ marginBottom: "2rem" }}>Ready to inspect your crop health?</h2>
        <div className="cta-buttons" style={{ display: "flex", justifyContent: "center", gap: "1rem" }}>
          <Link to="/services" className="btn-outline-dark" style={{ borderColor: "#e1fc84", color: "#e1fc84" }}>Explore Our Services</Link>
          <Link to="/scan" className="btn-dark" style={{ background: "#e1fc84", color: "#000" }}>Scan Your Crop ?</Link>
        </div>
      </section>
    </div>
  );
}
