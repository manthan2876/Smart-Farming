import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogIn, Sprout } from "lucide-react";
import { motion } from "motion/react";
import "../styles/AuthPages.css";

export default function LoginPage() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signIn } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signIn(identifier, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to login. Please check your credentials.");
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
            <div style={{ marginBottom: "2rem" }}>
              <Sprout size={40} color="#0F3D2E" />
            </div>
            <h2>Welcome Back</h2>
            <p className="auth-subtitle">[ACCESS YOUR DASHBOARD]</p>

            {error && <div className="alert alert-error">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label>Email or Phone</label>
                <input 
                  type="text" 
                  value={identifier} 
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="farmer@example.com"
                  required 
                />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input 
                  type="password" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required 
                />
              </div>
              <button type="submit" disabled={loading}>
                {loading ? "Authenticating..." : "Sign In"}
              </button>
            </form>

            <div className="auth-links">
              Don't have an account? <Link to="/auth/register">Create Account</Link>
              <br/><br/>
              <Link to="/" style={{ textDecoration: "none", color: "#728079" }}>← Back to Home</Link>
            </div>
          </motion.div>
        </div>
        <div className="auth-right">
          <div className="auth-quote">
            <h2>"Data-driven decisions start here. Monitor, analyze, and protect your harvest."</h2>
            <p>[SMART FARMING INTELLIGENCE]</p>
          </div>
        </div>
      </div>
    </div>
  );
}
