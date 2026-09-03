import { Link } from "react-router-dom";
import { Sprout, Droplet, Bug } from "lucide-react";
import { motion } from "motion/react";
import "../styles/LandingPage.css";

export default function LandingPage() {
  return (
    <div className="landing-page">
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

      {/* Hero Section */}
      <section className="hero-split">
        <div className="hero-left">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            Smarter Farming Starts Here
          </motion.h1>
          
          <motion.div 
            className="center-sprout"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Sprout size={80} color="#2C3A32" strokeWidth={1} />
          </motion.div>

          <div className="hero-left-bottom">
            <p>
              <strong>[We are Marbam,]</strong><br/>
              We turn your farm's data into clear, simple actions that boost efficiency, increase yield, and improve your bottom line.
            </p>
            <div className="hero-buttons">
              <Link to="/auth/register" className="wix-btn wix-btn-neon">Start A Demo</Link>
              <Link to="/services" className="wix-btn wix-btn-outline">Learn More</Link>
            </div>
          </div>
        </div>

        <div className="hero-right">
          <img src="https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=2070&auto=format&fit=crop" alt="Farmer in field" />
          <div className="hero-stats-overlay">
            <div className="stat-item-landing">
              <h4><span>[01]</span> 32% Higher Yields</h4>
              <p>From every treated acre</p>
            </div>
            <div className="stat-item-landing">
              <h4><span>[02]</span> 45% Less Water Use</h4>
              <p>Per ton of crop</p>
            </div>
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <section className="impact-section">
        <div className="impact-title">
          The Impact of Smarter Decisions
        </div>
        <div className="impact-content">
          <h2>When intelligence guides your operation, the results speak for themselves. From row crops to orchards and greenhouse, our clients achieve:</h2>
          
          <div className="impact-grid">
            <div className="impact-item">
              <h4><span>[01]</span> 40%</h4>
              <p>More Efficient Water &<br/>Nutrient Use</p>
            </div>
            <div className="impact-item">
              <div className="impact-icon"><Droplet color="#3b82f6" size={32} /></div>
              <h4><span>[02]</span> Up to 25%</h4>
              <p>Higher Harvest Value</p>
            </div>
            <div className="impact-item">
              <h4><span>[03]</span> 98%</h4>
              <p>Accuracy in Predictive<br/>Threat Detection</p>
            </div>
            <div className="impact-item">
              <div className="impact-icon"><Bug color="#D67756" size={32} /></div>
              <h4><span>[04]</span> Millions</h4>
              <p>of smart decisions made<br/>daily across our network</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
