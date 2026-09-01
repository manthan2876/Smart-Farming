import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Mail, Lock, LogIn, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await signIn(username, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.message || "Invalid credentials or server error.");
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-layout">
      <motion.div 
        className="auth-card card"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <div className="auth-header">
          <div className="logo-icon-lg">🌱</div>
          <h2>Farmer Portal Login</h2>
          <p>Access your smart farming dashboard and history</p>
        </div>

        {error && (
          <div className="alert alert-error">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="auth-form">
          <div className="form-group">
            <label><Mail size={16} /> Email or Phone Number</label>
            <input 
              type="text" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              placeholder="farmer@example.com"
              className="form-control"
              required 
            />
          </div>

          <div className="form-group">
            <label><Lock size={16} /> Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="••••••••"
              className="form-control"
              required 
            />
          </div>

          <button type="submit" className="btn btn-primary btn-full btn-glow" disabled={loading}>
            <LogIn size={18} /> {loading ? "Authenticating..." : "Sign In"}
          </button>
        </form>

        <div className="auth-footer">
          <p>Don't have an account? <Link to="/auth/register">Register as a Farmer</Link></p>
          <p className="mt-2"><Link to="/">← Back to Home</Link></p>
        </div>
      </motion.div>
    </div>
  );
}