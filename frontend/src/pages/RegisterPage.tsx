import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { UserPlus, Sprout } from "lucide-react";
import { motion } from "motion/react";
import "../styles/AuthPages.css";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [language, setLanguage] = useState("English");
  const [location, setLocation] = useState("");
  
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signUp } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signUp({ name, email, phone, password, language, location });
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to create account.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-split">
        <div className="auth-left">
          <motion.div 
            className="auth-card"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <div style={{ marginBottom: "1.5rem" }}>
              <Sprout size={40} color="#0F3D2E" />
            </div>
            <h2 style={{ fontSize: "2rem" }}>Create Account</h2>
            <p className="auth-subtitle">[JOIN THE ECOSYSTEM]</p>

            {error && <div className="alert alert-error">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label>Full Name</label>
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} required />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <div className="form-group">
                  <label>Email Address</label>
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                </div>
                <div className="form-group">
                  <label>Phone Number</label>
                  <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)} required />
                </div>
              </div>
              <div className="form-group">
                <label>Password</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <div className="form-group">
                  <label>Language</label>
                  <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                    <option value="English">English</option>
                    <option value="Hindi">Hindi</option>
                    <option value="Gujarati">Gujarati</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Location</label>
                  <input type="text" value={location} onChange={(e) => setLocation(e.target.value)} required />
                </div>
              </div>

              <button type="submit" disabled={loading}>
                {loading ? "Creating..." : "Register & Continue"}
              </button>
            </form>

            <div className="auth-links">
              Already have an account? <Link to="/auth/login">Sign In</Link>
            </div>
          </motion.div>
        </div>
        <div className="auth-right" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1595841696650-622839b207ee?q=80&w=2069&auto=format&fit=crop')" }}>
          <div className="auth-quote">
            <h2>"Smarter agriculture built for the next generation of farming."</h2>
            <p>[CROP INTELLIGENCE PLATFORM]</p>
          </div>
        </div>
      </div>
    </div>
  );
}
