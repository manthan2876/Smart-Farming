import { motion } from "motion/react";
import { Link } from "react-router-dom";
import { Sprout } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { fetchSupportedCrops } from "../api/crops";
import "../styles/LandingPage.css"; // Reuse landing page styles for consistency

export default function CropsPage() {
  const { data: crops, isLoading, isError } = useQuery({
    queryKey: ["supportedCrops"],
    queryFn: () => fetchSupportedCrops(),
  });

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

      {/* Header Section */}
      <section className="impact-section" style={{ gridTemplateColumns: "1fr" }}>
        <div className="impact-title" style={{ borderRight: "none", display: "flex", flexDirection: "column", alignItems: "flex-start", justifyContent: "center", minHeight: "40vh" }}>
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ fontSize: "5rem", textTransform: "uppercase", lineHeight: "1", margin: 0, marginBottom: "2rem" }}
          >
            Supported Crops
          </motion.h1>
          <p style={{ fontSize: "1.2rem", maxWidth: "600px", fontFamily: "'DM Sans', sans-serif", textTransform: "none", color: "#444" }}>
            Our AI diagnostic engines are continuously trained on thousands of plant images. We currently provide production-ready pathology models for the following crops.
          </p>
        </div>
      </section>

      {/* Grid Section */}
      <section style={{ padding: "4rem", backgroundColor: "#fff" }}>
        {isLoading && <p>Loading supported crops...</p>}
        {isError && <p>Failed to load crops from server.</p>}

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "2rem" }}>
          {crops?.map((cropName: string, i: number) => (
            <motion.div 
              key={cropName} 
              initial={{ opacity: 0, y: 20 }} 
              animate={{ opacity: 1, y: 0 }} 
              transition={{ delay: i * 0.05 }}
              style={{
                border: "2px solid #000",
                padding: "2rem",
                display: "flex",
                flexDirection: "column",
                gap: "1.5rem",
                backgroundColor: "#fffdfa",
                transition: "transform 0.2s"
              }}
              onMouseEnter={(e) => e.currentTarget.style.transform = "translateY(-5px)"}
              onMouseLeave={(e) => e.currentTarget.style.transform = "translateY(0)"}
            >
              <div style={{ 
                width: "64px", height: "64px", borderRadius: "50%", 
                backgroundColor: "#e1fc84", display: "flex", alignItems: "center", justifyContent: "center", border: "2px solid #000"
              }}>
                <Sprout size={32} color="#000" />
              </div>
              <h3 style={{ margin: 0, fontSize: "2rem", textTransform: "uppercase" }}>{cropName}</h3>
              <p style={{ color: "#728079", fontFamily: "monospace", fontSize: "0.85rem", margin: 0 }}>
                [ACTIVE MODEL PIPELINE]
              </p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
