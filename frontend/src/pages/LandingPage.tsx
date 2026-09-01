import { Link } from "react-router-dom";
import { Sprout, Scan, ShieldCheck, CloudSun, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

export default function LandingPage() {
  return (
    <div className="landing-page">
      {/* Top Navbar */}
      <nav className="landing-navbar">
        <div className="brand">
          <span className="logo">🌱</span>
          <span className="brand-name">Smart Farming</span>
        </div>
        <div className="nav-actions">
          <Link to="/crops" className="btn btn-ghost">Supported Crops</Link>
          <Link to="/auth/login" className="btn btn-outline">Sign In</Link>
          <Link to="/auth/register" className="btn btn-primary">Get Started</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <motion.div 
          className="hero-content"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="badge-pill mb-3">🚀 Next-Gen AI Agronomy Platform</span>
          <h1>Protect Your Harvest with <span>Instant AI Disease Diagnostics</span></h1>
          <p>
            Upload leaf photographs to instantly run OpenCV quality validation, pest identification, 
            severity metrics, and localized multi-lingual LLM remedy recommendations.
          </p>
          <div className="hero-cta-group">
            <Link to="/auth/register" className="btn btn-primary btn-lg btn-glow">
              Create Free Account <ArrowRight size={18} />
            </Link>
            <Link to="/crops" className="btn btn-secondary btn-lg">
              Explore Crops
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Features Grid */}
      <section className="features-section container">
        <div className="section-title text-center mb-5">
          <h2>Core Capabilities Built for Modern Farms</h2>
          <p>Everything you need from seeding to harvest management.</p>
        </div>

        <div className="features-grid">
          <div className="feature-card card">
            <Scan size={32} className="text-primary mb-3" />
            <h3>AI Leaf Diagnostics</h3>
            <p>Instant disease classification with Grad-CAM visual explainability overlays and confidence grading.</p>
          </div>
          <div className="feature-card card">
            <CloudSun size={32} className="text-warning mb-3" />
            <h3>Live Weather Telemetry</h3>
            <p>Real-time atmospheric monitoring for precise pesticide spray timing and irrigation scheduling.</p>
          </div>
          <div className="feature-card card">
            <ShieldCheck size={32} className="text-success mb-3" />
            <h3>MLOps Feedback Loop</h3>
            <p>Farmer verification notes fed directly back into our model retraining pipeline for continuous accuracy.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer text-center">
        <p>© 2026 Smart Farming Backend & Frontend Suite. All rights reserved.</p>
        <p className="mt-1"><Link to="/docs" target="_blank" className="link-inline">Interactive API Documentation (Swagger)</Link></p>
      </footer>
    </div>
  );
}